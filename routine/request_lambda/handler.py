"""arabamerican.ai/build/ backend: one POST, one email to the inbound inbox.

The static site posts the deployment request as JSON to this Lambda function URL. Each valid request is sent
through Amazon SES to every address in RECIPIENTS, one message per address. Reply-To is the person who wrote.
Nothing is stored; the log keeps the organisation and the outcome only, which is what the daily run counts.

Env: RECIPIENTS (comma separated), MAIL_FROM.
Deployed 28 Nov 2026 as aai-deployment-request (us-east-1, profile hyper-fde), role codeatoms-contact-role.
Revert: set FORM_API = "" in build.py (the form falls back to the email app) and delete the function.
"""
import json, os, re, time
import boto3

SES = boto3.client("sesv2", region_name=os.getenv("SES_REGION", "us-east-1"))
RECIPIENTS = [r.strip() for r in os.getenv("RECIPIENTS", "hello@codeninjaconsulting.com").split(",") if r.strip()]
MAIL_FROM = os.getenv("MAIL_FROM", "Arab American Instruments <noreply@codeatoms.ai>")
EMAIL = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$")
LIMITS = {"Name": 120, "Organisation": 160, "Email": 200, "Country": 120, "Platform": 120, "Requirement": 4000,
          "Connectivity": 160, "Quantity": 160, "Timeline": 200, "page": 300}
FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com", "proton.me", "protonmail.com"}


def _resp(code, body):
    return {"statusCode": code, "headers": {"content-type": "application/json"}, "body": json.dumps(body)}


def _clean(v, n):
    return re.sub(r"[\r\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(v or "")).strip()[:n]


def handler(event, context):
    method = (event.get("requestContext", {}).get("http", {}) or {}).get("method", "POST")
    if method != "POST":
        return _resp(405, {"ok": False})
    try:
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64
            raw = base64.b64decode(raw).decode("utf-8", "replace")
        d = json.loads(raw)
    except Exception:
        return _resp(400, {"ok": False, "error": "bad request"})
    if not isinstance(d, dict):
        return _resp(400, {"ok": False, "error": "bad request"})

    f = {k: _clean(d.get(k), n) for k, n in LIMITS.items()}
    # Bots: the hidden field is filled, or the form came back faster than a person types.
    if _clean(d.get("website"), 200) or (isinstance(d.get("elapsed"), (int, float)) and d["elapsed"] < 3000):
        print(json.dumps({"outcome": "dropped_bot"}))
        return _resp(200, {"ok": True})
    if not f["Name"] or not f["Organisation"] or not f["Requirement"] or not EMAIL.match(f["Email"]):
        return _resp(422, {"ok": False, "error": "Please fill in your name, a work email, your organisation and the requirement."})
    if len(re.findall(r"https?://", f["Requirement"])) > 3:
        print(json.dumps({"outcome": "dropped_links"}))
        return _resp(200, {"ok": True})

    domain = f["Email"].split("@")[-1].lower()
    subject = f"Deployment request: {f['Organisation']} ({f['Platform'] or 'device not chosen'})"
    lines = [f"Name: {f['Name']}", f"Email: {f['Email']}" + ("  (personal address)" if domain in FREE_MAIL else ""),
             f"Organisation: {f['Organisation']}", f"Country: {f['Country'] or 'not given'}",
             f"Closest device: {f['Platform'] or 'not given'}", f"Where the data goes: {f['Connectivity'] or 'not given'}",
             f"Units to start: {f['Quantity'] or 'not given'}", f"Timeline: {f['Timeline'] or 'not given'}", "",
             "Requirement:", f["Requirement"], "",
             f"Sent from {f['page'] or 'https://arabamerican.ai/build/'} at {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}.",
             "Reply to this email to answer them directly."]
    sent = 0
    for to in RECIPIENTS:
        try:
            SES.send_email(FromEmailAddress=MAIL_FROM, Destination={"ToAddresses": [to]}, ReplyToAddresses=[f["Email"]],
                           Content={"Simple": {"Subject": {"Data": " ".join(subject.split())[:200]}, "Body": {"Text": {"Data": "\n".join(lines)}}}})
            sent += 1
        except Exception as e:
            print(json.dumps({"outcome": "send_failed", "to": to, "error": type(e).__name__}))
    print(json.dumps({"outcome": "sent" if sent else "failed", "organisation": f["Organisation"], "delivered": sent}))
    if not sent:
        return _resp(502, {"ok": False, "error": "We could not send your request. Please email hello@codeninjaconsulting.com."})
    return _resp(200, {"ok": True})
