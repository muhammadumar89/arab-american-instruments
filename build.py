#!/usr/bin/env python3
"""Build the Arab American Instruments site into ./site.

Run: python3 build.py
Pages, products and Design Lab notes live in this file as data. Videos are in
assets/video (credits in assets/video/CREDITS.md); product images in
assets/img/products. House style: no hyphens or dashes in copy, no prices,
no customer names, every banner a real world video.
"""
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
BASE = ""  # set to "/sub/path" if served below a domain root
SITE_URL = "https://arabamericaninstruments.com"  # placeholder until a domain is chosen
CONTACT = "hello@codeninjaconsulting.com"  # inbound router; change when AAI has its own mailbox

TAGLINE = "Low-power edge devices for sensing, Satcoms and RT controls in Air Gapped Environments."

e = html.escape


def u(path):
    return BASE + path


# ---------------------------------------------------------------- data

LINES = {
    "sensing": {
        "name": "Sensing",
        "film": "dashcam-desert",
        "title": "Eyes and nerves at the edge.",
        "body": "Cameras, motion, heart rate, temperature and the vehicle's own data, turned into events on the device itself. Only the result leaves the unit.",
    },
    "satcoms": {
        "name": "Satcoms and mesh",
        "film": "dish-sunset",
        "title": "Links that hold when the network does not.",
        "body": "LoRa mesh, cellular and satellite in layers, so a message finds a way out of the desert, the sea or a closed site. Nothing is dropped; everything queues and catches up.",
    },
    "controls": {
        "name": "RT Controls",
        "film": "pumpjack-dusk",
        "title": "Real time control, close to the machine.",
        "body": "Interfaces that read and drive vehicles, pumps, valves and lines in milliseconds, with no cloud in the loop and nothing that phones home.",
    },
}

STATUS = {
    "fab": "Boards at fab",
    "final": "Design complete",
    "design": "In design",
    "concept": "Reference concept",
}

PRODUCTS = [
    {
        "slug": "drivesense",
        "name": "DriveSense 2.0",
        "line": "sensing",
        "status": "fab",
        "kind": "Fleet vision unit",
        "film": "dashcam-desert",
        "short": "Two cameras on the windscreen, AI on the device, events over LTE. Watches the driver and the road and reads the truck's own data.",
        "images": [
            ("carrier-top.jpg", "Windscreen carrier board, top, with the compute module footprint and LTE modem"),
            ("carrier-bottom.jpg", "Windscreen carrier board, bottom"),
            ("carrier-bare.jpg", "Windscreen carrier board, bare layout"),
        ],
        "sections": [
            ("Driver, day and night", [
                "Drowsiness: eyes closing, long blinks, yawning, head nodding",
                "Distraction: eyes or head off the road for too long",
                "Phone use, smoking, eating and drinking",
                "Seatbelt on or off",
                "Who is driving, matched to enrolled drivers, and driver swaps",
                "No driver in the seat, passenger present, camera covered",
            ]),
            ("Road", [
                "Forward collision warning for vehicles, pedestrians and animals",
                "Following distance, lane departure and swerving",
                "Speed limit signs and traffic lights",
                "Number plates at close range",
            ]),
            ("Location and driving", [
                "Live position, speed, heading and route history",
                "Trips, stops and idling",
                "Harsh braking, acceleration and cornering",
                "Crash, impact and rollover; a knock while parked",
            ]),
            ("Video and status", [
                "A short clip from both cameras with every event, and on a button press",
                "Continuous recording on the unit, pulled for any time later",
                "Live view from either camera on request, with cabin audio",
                "A last message when power is cut; alerts when the case is opened or a camera is blocked",
            ]),
        ],
        "specs": [
            ("Compute", "RK3576 class compute module on our own carrier board"),
            ("Cameras", "Two: driver facing RGB IR for night, and road facing"),
            ("Links", "LTE and GPS; stores everything with no signal and sends when coverage returns"),
            ("Vehicle data", "Through VIM 2.0 on the truck's diagnostic or FMS port"),
            ("In the cab", "Spoken alerts and a driver button"),
            ("Shell", "Printed nylon housing, built for desert heat"),
        ],
        "pairs": ["vim"],
    },
    {
        "slug": "vim",
        "name": "VIM 2.0",
        "line": "controls",
        "status": "final",
        "kind": "Vehicle Interface Module",
        "film": "night-highway",
        "short": "A small box that plugs into the truck, reads its data buses and powers the camera unit. Works on light trucks and heavy fleets alike.",
        "images": [
            ("vim-top.jpg", "VIM 2.0 board, top, with CAN, ignition and power headers"),
            ("vim-bottom.jpg", "VIM 2.0 board, bottom"),
        ],
        "sections": [
            ("Any truck", [
                "Ignition on and off",
                "Battery voltage and engine running",
                "Power for the camera unit, with a last gasp message on power loss",
            ]),
            ("Light and medium trucks, 16 pin diagnostic port", [
                "Engine speed, vehicle speed, coolant temperature",
                "Engine load and accelerator pedal",
                "Fault codes and warning lamps",
                "Vehicle ID, and fuel level and rate where the truck reports them",
            ]),
            ("Heavy trucks, 12 pin FMS port", [
                "Total fuel used, live fuel rate and economy",
                "Odometer, engine hours and distance to next service",
                "Brake, clutch and cruise control",
                "Axle weight, AdBlue level, and driver hours where a tachograph is fitted",
            ]),
        ],
        "specs": [
            ("Buses", "Two CAN channels plus a K line"),
            ("Ports", "16 pin diagnostic and 12 pin FMS harnesses"),
            ("Power", "Truck battery in, regulated power out to the camera unit"),
            ("Fallback", "Where the truck gives no speed or distance, GPS does"),
        ],
        "pairs": ["drivesense"],
    },
    {
        "slug": "field-band",
        "name": "Field Band",
        "line": "sensing",
        "status": "design",
        "kind": "LoRa wrist band for people in the field",
        "film": "walker-desert",
        "short": "A slim, sealed band that reports position, heart rate and skin temperature over LoRa, calls for help with one button and lasts days on a charge.",
        "images": [
            ("band-wrist.jpg", "Field Band on the wrist"),
            ("band-angle.jpg", "Field Band, three quarter view with the hidden light ring"),
            ("band-loop.jpg", "Field Band strap and loop"),
            ("band-under.jpg", "Field Band underside, heart rate window and charging contacts"),
            ("band-mainboard.jpg", "Main board, top: GPS antenna area kept clear"),
            ("band-sensor.jpg", "Sensor board for heart rate, temperature and charging"),
        ],
        "sections": [
            ("What it reports", [
                "Position from a low power GPS with a thin patch antenna",
                "Heart rate and skin temperature, chosen for accuracy on a moving wrist",
                "Falls and stillness from a motion sensor",
                "Battery level and an off wrist alert",
            ]),
            ("When something goes wrong", [
                "A recessed SOS button that goes out on every path at once",
                "Vibration only once help has confirmed the message",
                "A separation alarm when the wearer loses their group",
                "A hidden light ring that glows only in an emergency, so rescuers can find the wearer at night",
            ]),
            ("Two builds", [
                "LoRa only: the slimmest band, about 5 to 7 days per charge (estimate)",
                "LoRa plus soldered eSIM: calls for help alone wherever there is phone signal, about 2 days per charge (estimate)",
            ]),
        ],
        "specs": [
            ("Radio", "Processor with built in LoRa; optional cellular with eSIM"),
            ("Message", "24 bytes every 5 minutes, instantly for SOS and falls, encrypted per band"),
            ("Boards", "Main board about 4 by 2.7 cm, sensor board about 2 by 2 cm (current estimates)"),
            ("Battery", "150 to 250 mAh cell with protection, temperature limited charging and a fuse"),
            ("Sealing", "IP67, button included; charging contacts are dead off the dock"),
        ],
        "pairs": ["guide-hub", "vehicle-gateway", "solar-relay", "charging-dock"],
    },
    {
        "slug": "guide-hub",
        "name": "Guide Hub",
        "line": "satcoms",
        "status": "concept",
        "kind": "Backpack gateway",
        "film": "radio-site",
        "short": "Carried at the front and back of a group, it collects every band in range and sends the data on by cellular, or by satellite when there is nothing else.",
        "images": [],
        "sections": [
            ("Inside", [
                "LoRa gateway for the group's bands",
                "Cellular modem with a satellite messaging modem as backup",
                "GPS, local storage for queued messages",
                "Bluetooth to a phone app for the guide",
                "Antenna on the shoulder strap, rugged sealed case",
            ]),
        ],
        "specs": [
            ("Power", "Swappable pack, about 10 to 20 Wh, charged nightly"),
            ("Load", "A group of about 50 bands is roughly one message every 6 seconds"),
        ],
        "pairs": ["field-band", "vehicle-gateway"],
    },
    {
        "slug": "vehicle-gateway",
        "name": "Vehicle Gateway",
        "line": "satcoms",
        "status": "concept",
        "kind": "Roof unit for patrol and safety vehicles",
        "film": "mojave-hwy",
        "short": "Reaches much further than a backpack. In search mode a missing band reports every few seconds and the screen counts down as the vehicle closes in.",
        "images": [],
        "sections": [
            ("Inside", [
                "Multi channel LoRa gateway with a magnetic roof antenna",
                "Cellular modem with external antenna and a satellite link",
                "GPS and a rugged tablet with a live map",
                "Search mode with a warmer and colder signal meter",
            ]),
        ],
        "specs": [("Power", "Vehicle 12 V supply")],
        "pairs": ["field-band", "guide-hub"],
    },
    {
        "slug": "solar-relay",
        "name": "Solar Relay",
        "line": "satcoms",
        "status": "concept",
        "kind": "Pole mounted mesh relay",
        "film": "solar-desert",
        "short": "Bolts onto a pole, runs on the sun and passes data pole to pole until it reaches one with a real uplink.",
        "images": [],
        "sections": [
            ("Inside", [
                "LoRa gateway for nearby bands and sensors",
                "Long range LoRa link to the next pole on a directional antenna",
                "Health reports: battery, solar and temperature",
                "White, shaded, sealed box with passive vents",
                "Uplink build adds cellular on a high gain antenna, or satellite, or microwave",
            ]),
        ],
        "specs": [
            ("Power", "About 80 to 100 W solar and about 300 Wh of heat tolerant LiFePO4"),
            ("Bandwidth", "300 wearers need under 1 kbit/s; a thin satellite link carries it easily"),
        ],
        "pairs": ["field-band", "guide-hub"],
    },
    {
        "slug": "charging-dock",
        "name": "Charging Dock",
        "line": "satcoms",
        "status": "concept",
        "kind": "Camp dock for Field Bands",
        "film": "soldering",
        "short": "Charges, tests and pairs bands in one tray, and refuses anything that is not ours.",
        "images": [],
        "sections": [
            ("Inside", [
                "10 to 20 slots with sealed 3 pin contacts",
                "A check that only our bands charge",
                "Status light per slot; a red light and a dashboard alert if a battery fails",
                "USB link to a laptop for pairing bands to people, firmware updates and self tests",
            ]),
        ],
        "specs": [("Power", "Mains or generator")],
        "pairs": ["field-band"],
    },
]
PBY = {p["slug"]: p for p in PRODUCTS}

INDUSTRIES = [
    ("Fleets and logistics", "truck-desert", "Driver safety, vehicle data and video for fleets running thousands of heavy trucks.", ["drivesense", "vim"]),
    ("Crowd and walker safety", "walkers-desert", "Bands, hubs and relays that keep large groups covered on long routes far from the network.", ["field-band", "guide-hub", "solar-relay"]),
    ("Energy and pipelines", "pumpjacks-desert", "Sensing and control on wells, valves and lines, on links you own.", ["solar-relay", "vim"]),
    ("Utilities and grid", "substation", "Monitoring and control near the equipment, isolated from the public internet.", []),
    ("Agriculture and water", "irrigation", "Low power sensing and pump control across fields and wells.", ["solar-relay"]),
    ("Remote and closed sites", "desert-aerial", "Border, camp and range sites where nothing may leave the perimeter.", ["vehicle-gateway", "guide-hub"]),
    ("Telecom and satellite", "cell-tower", "Edge radios, relays and terminals for networks that must keep running.", ["solar-relay", "vehicle-gateway"]),
    ("Ports and supply chain", "harbor-night", "Tracking and sensing for yards, terminals and the trucks that serve them.", ["drivesense"]),
]

NOTES = [
    {
        "slug": "what-a-truck-will-tell-you",
        "title": "What a truck will tell you",
        "sub": "The data you get depends on the port the truck has. Here is the honest table.",
        "date": "11 Nov 2026",
        "film": "night-highway",
        "body": [
            ("p", "Every fleet asks the same first question: what data will we get? The answer is not ours to give. It depends on the truck, and above all on which port sits under the dashboard."),
            ("p", "Three things work on any truck: ignition, battery voltage and whether the engine is running. Beyond that, light and medium trucks usually expose a 16 pin diagnostic port, and heavy trucks built for fleet management carry a 12 pin FMS port. The second gives far more."),
            ("table", [
                ["Data", "Any truck", "16 pin diagnostic", "12 pin FMS"],
                ["Ignition, battery, engine running", "Yes", "Yes", "Yes"],
                ["Engine speed, vehicle speed, coolant", "", "Yes", "Yes"],
                ["Engine load, accelerator pedal", "", "Yes", "Yes"],
                ["Fault codes, warning lamps", "", "Yes", "Newer trucks"],
                ["Vehicle ID", "", "Usually", "Yes"],
                ["Fuel level, live fuel rate", "", "Sometimes", "Yes"],
                ["Total fuel used, odometer, engine hours", "", "No", "Yes"],
                ["Brake, clutch, cruise control", "", "No", "Yes"],
                ["Axle weight, distance to service", "", "No", "Yes"],
                ["AdBlue level", "", "No", "Newer trucks"],
                ["Driver hours from the tachograph", "", "No", "If fitted"],
            ]),
            ("p", "Where the truck does not give speed or distance, GPS does. Where there is no signal, the unit keeps everything and sends it when coverage returns. Events and their clips go straight away; location and truck data follow every few seconds to a minute."),
            ("p", "So before we quote a fleet, we look at the trucks. A fleet of fleet managed heavy trucks gets the whole table; a fleet of light trucks gets the top half, and we say so up front."),
        ],
    },
    {
        "slug": "a-person-in-24-bytes",
        "title": "A person in 24 bytes",
        "sub": "How a wrist band can report every five minutes for days, over links slower than old 2G.",
        "date": "10 Nov 2026",
        "film": "walker-desert",
        "body": [
            ("p", "A band on a wrist has a small battery and a long way to shout. So the message has to be tiny. Ours is 24 bytes."),
            ("table", [
                ["Field", "Bytes"],
                ["Band ID", "4"],
                ["Latitude", "4"],
                ["Longitude", "4"],
                ["Timestamp", "4"],
                ["Sequence number", "2"],
                ["Skin temperature", "2"],
                ["Heart rate", "1"],
                ["Battery level", "1"],
                ["Alert flags: SOS, fall, still, off wrist, battery fault", "1"],
                ["Spare", "1"],
            ]),
            ("p", "With wrapping and security it is about 100 bytes by the time it reaches a server. One message every five minutes means 300 people need about 0.8 kbit/s and about 9 MB a day: roughly one phone photo an hour."),
            ("h", "Why it does not collide"),
            ("p", "GPS gives every band the exact time, so each band speaks in its own slot of the five minute cycle. Before sending it listens for a fraction of a second. The hub answers every few seconds with one short list of the bands it heard; a band that is not on the list tries again within seconds on another channel."),
            ("p", "Nothing is dropped. A message that cannot get through stays on the band and goes out with the next one, and the sequence number puts everything back in order. SOS and falls skip the queue, go out on every path, and repeat until someone confirms."),
        ],
    },
    {
        "slug": "small-decisions-on-a-small-board",
        "title": "Small decisions on a small board",
        "sub": "Why the top of the band's board is nearly empty, and what a board colour costs.",
        "date": "11 Nov 2026",
        "film": "pcb-macro",
        "body": [
            ("p", "Look at the main board of the Field Band and the top is almost bare. That is on purpose. The GPS antenna is a thin patch, and anything switching nearby makes it deaf. So the electronics live underneath and the top is kept clear for the sky."),
            ("p", "The sensor board sits at the very bottom, against the skin, where the heart rate sensor and the charging contacts need to be. Today it is about 2 by 2 cm and the main board about 4 by 2.7 cm. Those numbers will move as the requirements settle."),
            ("p", "Colour is a choice too. A black solder mask costs about $3.30 more per board than the standard green. It photographs beautifully. Inside a sealed shell nobody sees it, so for a production run green is usually the right answer, and the customer decides."),
            ("p", "We write these down because the customer owns the design. Every one of these choices is in the files they keep."),
        ],
    },
]

# ---------------------------------------------------------------- chrome

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600&family=Geist+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&display=swap" rel="stylesheet">'

MARK = '<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7 27 Q20 4 33 27" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="7" cy="27" r="3" fill="var(--signal)"/><circle cx="33" cy="27" r="3" fill="var(--sand)"/></svg>'

NAV = [("Platforms", "/platforms/"), ("Industries", "/industries/"), ("Design Lab", "/lab/"), ("Supply chain", "/supply-chain/"), ("About", "/about/")]


def header(active=""):
    links = "".join(
        f'<a href="{u(h)}"{" class=on" if active == h else ""}>{n}</a>' for n, h in NAV
    )
    return f'''<header class="top"><div class="bar">
<a class="brand" href="{u("/")}">{MARK}<span>Arab American <b>Instruments</b></span></a>
<nav id="nav">{links}<a class="btn small" href="{u("/build/")}">Request a build</a></nav>
<button class="menu" aria-label="Menu" aria-expanded="false" onclick="document.body.classList.toggle('open');this.setAttribute('aria-expanded',document.body.classList.contains('open'))"><span></span><span></span></button>
</div></header>'''


def footer():
    cols = "".join(f'<a href="{u(h)}">{n}</a>' for n, h in NAV)
    prods = "".join(f'<a href="{u("/platforms/" + p["slug"] + "/")}">{e(p["name"])}</a>' for p in PRODUCTS)
    return f'''<footer class="foot"><div class="wrap">
<div class="fgrid">
<div><a class="brand" href="{u("/")}">{MARK}<span>Arab American <b>Instruments</b></span></a>
<p class="tag">{e(TAGLINE)}</p></div>
<div><h4>Company</h4>{cols}<a href="{u("/credits/")}">Credits</a></div>
<div><h4>Platforms</h4>{prods}</div>
<div><h4>Headquarters</h4><p>Riyadh, Saudi Arabia<br><span class="mono">24.71 N, 46.68 E</span></p><p>Dallas, Texas<br><span class="mono">32.78 N, 96.80 W</span></p></div>
</div>
<div class="legal"><span>Arab American Instruments is a fully owned subsidiary of CodeNinja.</span><span>&copy; 2026 Arab American Instruments</span></div>
</div></footer>'''


SCRIPT = '''<script>
(function(){
  function solid(){ document.body.classList.toggle('scrolled', window.scrollY>40); }
  solid(); window.addEventListener('scroll', solid, {passive:true});
  var vids=[].slice.call(document.querySelectorAll('video[data-src]'));
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load(v){ if(!v.src){ v.src=v.getAttribute('data-src'); } }
  if(!reduce && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){ es.forEach(function(x){ var v=x.target;
      if(x.isIntersecting){ load(v); var p=v.play(); if(p&&p.catch){p.catch(function(){});} } else { v.pause(); } }); },{rootMargin:'200px 0px'});
    vids.forEach(function(v){ io.observe(v); });
  }
  document.querySelectorAll('.card[data-film]').forEach(function(c){
    var v=c.querySelector('video'); if(!v) return;
    c.addEventListener('mouseenter',function(){ load(v); var p=v.play(); if(p&&p.catch){p.catch(function(){});} });
    c.addEventListener('mouseleave',function(){ v.pause(); });
  });
  var f=document.getElementById('buildform');
  if(f){ f.addEventListener('submit',function(ev){ ev.preventDefault();
    var d=new FormData(f), lines=[]; d.forEach(function(val,k){ if(val) lines.push(k+': '+val); });
    var subj='Build request: '+(d.get('Organisation')||'')+' '+(d.get('Platform')||'');
    window.location.href='mailto:%s?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(lines.join('\\n'));
    f.querySelector('.sent').hidden=false; }); }
})();
</script>''' % CONTACT


def page(path, title, desc, body, active=""):
    full = title if title == "Arab American Instruments" else f"{title} | Arab American Instruments"
    canon = SITE_URL + path
    doc = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}/assets/video/home-montage.jpg"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0b0a">
<link rel="icon" href="{u("/assets/img/mark.svg")}" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="{u("/assets/site.css")}">
</head><body>
{header(active)}
<main>{body}</main>
{footer()}
{SCRIPT}
</body></html>
'''
    dest = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        fh.write(doc)
    PAGES.append(path)


PAGES = []

# ---------------------------------------------------------------- blocks


def film(slug, inner, cls="", hero=False):
    v = f"/assets/video/{slug}"
    if hero:
        media = f'<video autoplay muted loop playsinline preload="auto" poster="{u(v + ".jpg")}" aria-hidden="true"><source src="{u(v + ".mp4")}" type="video/mp4"></video>'
    else:
        media = f'<video muted loop playsinline preload="none" poster="{u(v + ".jpg")}" data-src="{u(v + ".mp4")}" aria-hidden="true"></video>'
    return f'<section class="film {cls}"><img class="poster" src="{u(v + ".jpg")}" alt="" aria-hidden="true">{media}<div class="scrim"></div><div class="inner">{inner}</div></section>'


def status_badge(p):
    return f'<span class="badge s-{p["status"]}">{STATUS[p["status"]]}</span>'


def product_card(p):
    img = p["images"][0][0] if p["images"] else None
    if img:
        media = f'<img src="{u("/assets/img/products/" + img)}" alt="{e(p["images"][0][1])}" loading="lazy">'
        cls = "card prod"
    else:
        f = p["film"]
        media = f'<img src="{u("/assets/video/" + f + ".jpg")}" alt="" loading="lazy"><video muted loop playsinline preload="none" data-src="{u("/assets/video/" + f + ".mp4")}" aria-hidden="true"></video>'
        cls = "card prod filmcard"
    data = ' data-film="1"' if not img else ""
    return f'''<a class="{cls}"{data} href="{u("/platforms/" + p["slug"] + "/")}">
<div class="cm">{media}</div>
<div class="cb"><div class="meta"><span class="mono">{e(LINES[p["line"]]["name"])}</span>{status_badge(p)}</div>
<h3>{e(p["name"])}</h3><p class="kind">{e(p["kind"])}</p><p>{e(p["short"])}</p>
<span class="more">Made to order <i>&rarr;</i></span></div></a>'''


OWN = [
    ("Design files", "Schematics, board layout and mechanical files. Yours to keep."),
    ("Bill of materials", "Every part with its maker and where it comes from."),
    ("Firmware and keys", "Source code and the signing keys, held by you."),
    ("Your choice of fab", "Build the next thousand wherever you trust."),
]


def own_strip(light=False):
    items = "".join(f'<div><span class="mono n">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(OWN))
    return f'<section class="own{" light" if light else ""}"><div class="wrap"><p class="kicker">What you own when we hand over</p><div class="own4">{items}</div></div></section>'


def cta(title="Tell us what you need to sense, send or control.", film_slug="print-timelapse"):
    return film(film_slug, f'<p class="kicker">Made to order</p><h2>{e(title)}</h2><p class="lede">No catalogue prices. We start from your site, your vehicles and your rules, and quote the build.</p><a class="btn" href="{u("/build/")}">Request a build</a>', "cta center")


# ---------------------------------------------------------------- pages


def home():
    hero = film(
        "home-montage",
        f'''<p class="kicker">Arab American Instruments &middot; Riyadh and Dallas</p>
<h1>{e(TAGLINE)}</h1>
<p class="lede">We design the hardware. You own the supply chain. Every board, every part and every line of firmware comes with its origin and its source.</p>
<div class="actions"><a class="btn" href="{u("/build/")}">Request a build</a><a class="btn ghost" href="{u("/platforms/")}">See the platforms</a></div>
<p class="coords mono">RIYADH 24.71 N 46.68 E &nbsp;&middot;&nbsp; DALLAS 32.78 N 96.80 W</p>''',
        "hero",
        hero=True,
    )
    statement = f'''<section class="statement light"><div class="wrap narrow">
<p class="kicker">Why we exist</p>
<h2 class="serif">The biggest threats now sit in the hardware.</h2>
<p>For a decade the fight over control was a software fight. It has moved down the stack. A camera on a truck, a band on a wrist, a relay on a pole: each carries chips, radios and firmware that someone else chose, from a supply chain nobody in the room can see.</p>
<p>The phone in your pocket shows where that ends: a sealed stack you rent and never own. We think any organisation that runs critical work should own its hardware the way it already owns its data.</p>
<p>Arab American Instruments is a hardware design company. We own our designs, publish what we learn, and build purpose built devices for each customer, so the customer leaves with the design files, the parts list and the keys.</p>
</div></section>'''
    lines = ""
    for i, (k, L) in enumerate(LINES.items()):
        prods = [p for p in PRODUCTS if p["line"] == k]
        plinks = "".join(f'<a href="{u("/platforms/" + p["slug"] + "/")}">{e(p["name"])} <i>&rarr;</i></a>' for p in prods)
        if k == "controls":
            plinks += f'<a href="{u("/build/")}">Custom controllers <i>&rarr;</i></a>'
        lines += film(
            L["film"],
            f'<p class="kicker mono">0{i + 1} &nbsp; {e(L["name"])}</p><h2>{e(L["title"])}</h2><p class="lede">{e(L["body"])}</p><div class="plinks">{plinks}</div>',
            "band " + ("right" if i % 2 else "left"),
        )
    hw = film(
        "aai-hardware",
        f'<p class="kicker">Designed in house</p><h2>Made to order. Never off the shelf.</h2><p class="lede">These are our own boards and renders. Each platform is a reference design we adapt to your site and build in the quantity you need.</p>',
        "band left short",
    )
    cards = "".join(product_card(p) for p in PRODUCTS)
    grid = f'<section class="cards"><div class="wrap"><div class="head"><h2>Platforms</h2><a href="{u("/platforms/")}">All platforms <i>&rarr;</i></a></div><div class="grid3">{cards}</div></div></section>'
    inds = "".join(
        f'<a class="card ind" data-film="1" href="{u("/industries/")}#{slugify(n)}"><div class="cm"><img src="{u("/assets/video/" + f + ".jpg")}" alt="" loading="lazy"><video muted loop playsinline preload="none" data-src="{u("/assets/video/" + f + ".mp4")}" aria-hidden="true"></video></div><div class="cb"><h3>{e(n)}</h3></div></a>'
        for n, f, _, _ in INDUSTRIES
    )
    ind = f'<section class="cards dark2"><div class="wrap"><div class="head"><h2>Where it runs</h2><a href="{u("/industries/")}">All industries <i>&rarr;</i></a></div><div class="grid4">{inds}</div></div></section>'
    notes = "".join(note_card(n) for n in NOTES)
    lab = f'<section class="cards light"><div class="wrap"><div class="head"><h2 class="serif">From the Design Lab</h2><a href="{u("/lab/")}">All notes <i>&rarr;</i></a></div><div class="grid3">{notes}</div></div></section>'
    hq = f'''<section class="hq">
{film("riyadh-day", '<p class="kicker mono">HQ 01</p><h2>Riyadh</h2><p>Design, customer engineering and field trials for the Gulf.</p>', "half")}
{film("dallas-sunset", '<p class="kicker mono">HQ 02</p><h2>Dallas</h2><p>Design, partners and supply for the United States.</p>', "half")}
</section>
<section class="statement"><div class="wrap narrow center"><h2 class="serif">Two headquarters, one stack.</h2><p>The Gulf and the United States share one problem: critical systems running on hardware nobody in the room designed. We work from both and build for both.</p></div></section>'''
    body = hero + statement + own_strip() + lines + hw + grid + ind + lab + hq + cta()
    page("/", "Arab American Instruments", "Arab American Instruments designs low power edge devices for sensing, satcoms and real time control in air gapped environments. Riyadh and Dallas. You own the design and the supply chain.", body)


def slugify(s):
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-").replace("--", "-")


def note_card(n):
    return f'<a class="card note" href="{u("/lab/" + n["slug"] + "/")}"><div class="cm"><img src="{u("/assets/video/" + n["film"] + ".jpg")}" alt="" loading="lazy"></div><div class="cb"><span class="mono">{e(n["date"])}</span><h3 class="serif">{e(n["title"])}</h3><p>{e(n["sub"])}</p></div></a>'


def platforms():
    hero = film("oasis-road", f'<p class="kicker">Platforms</p><h1>Reference designs, built to order.</h1><p class="lede">Three lines from one design house. Nothing here has a list price: every unit is adapted to where it will live and built for the customer who will own it.</p>', "hero mid")
    sections = ""
    for k, L in LINES.items():
        prods = [p for p in PRODUCTS if p["line"] == k]
        cards = "".join(product_card(p) for p in prods)
        extra = ""
        if k == "controls":
            extra = f'<a class="card prod ask" href="{u("/build/")}"><div class="cb"><span class="mono">RT Controls</span><h3>Custom controllers</h3><p class="kind">Commissioned designs</p><p>Pumps, valves, irrigation, gates and lines. Tell us the machine and the timing budget and we design the controller around it.</p><span class="more">Start a commission <i>&rarr;</i></span></div></a>'
        tech = {"sensing": "cams-sunset", "satcoms": "antenna-sky", "controls": "scope-wave"}[k]
        sections += f'<div id="{k}">' + film(tech, f'<p class="kicker mono">{e(L["name"])}</p><h2>{e(L["title"])}</h2>', "band short left") + '</div>'
        sections += f'<section class="cards"><div class="wrap"><div class="head"><h2>{e(L["name"])}</h2><p>{e(L["body"])}</p></div><div class="grid3">{cards}{extra}</div></div></section>'
    legend = "".join(f'<span class="badge s-{k}">{v}</span>' for k, v in STATUS.items())
    leg = f'<section class="legend"><div class="wrap"><span class="mono">Status</span>{legend}<span class="mono">Updated 12 Nov 2026</span></div></section>'
    page("/platforms/", "Platforms", "Sensing, satcoms and mesh, and real time control platforms from Arab American Instruments. Made to order, never off the shelf.", hero + leg + sections + own_strip(True) + cta(), "/platforms/")


def product_page(p):
    L = LINES[p["line"]]
    hero = film(
        p["film"],
        f'<p class="kicker"><a href="{u("/platforms/")}#{p["line"]}">{e(L["name"])}</a> &middot; {e(p["kind"])}</p><h1>{e(p["name"])}</h1><p class="lede">{e(p["short"])}</p><div class="actions">{status_badge(p)}<a class="btn" href="{u("/build/")}?platform={p["slug"]}">Request this build</a></div>',
        "hero mid",
    )
    gal = ""
    if p["images"]:
        figs = "".join(f'<figure><img src="{u("/assets/img/products/" + f)}" alt="{e(c)}" loading="lazy"><figcaption>{e(c)}</figcaption></figure>' for f, c in p["images"])
        gal = f'<section class="gallery"><div class="wrap"><p class="kicker">From the Design Lab</p><div class="gal">{figs}</div></div></section>'
    else:
        gal = f'<section class="gallery"><div class="wrap"><p class="note-pending">Renders for {e(p["name"])} are in progress. This page describes the reference concept as designed today; parts are shortlisted, not final.</p></div></section>'
    secs = "".join(f'<div class="feat"><h3>{e(h)}</h3><ul>{"".join("<li>" + e(i) + "</li>" for i in items)}</ul></div>' for h, items in p["sections"])
    specs = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in p["specs"])
    pairs = "".join(product_card(PBY[s]) for s in p.get("pairs", []))
    body = (
        hero
        + gal
        + f'<section class="detail light"><div class="wrap"><div class="cols"><div><p class="kicker">What it does</p><div class="feats">{secs}</div></div><aside><p class="kicker">Reference specification</p><table class="spec">{specs}</table><p class="fine">Figures marked estimate are design targets, set conservatively, and will be confirmed in field trials. Every unit is adapted to the customer, so the delivered specification may differ.</p></aside></div></div></section>'
        + own_strip()
        + (f'<section class="cards"><div class="wrap"><div class="head"><h2>Works with</h2></div><div class="grid3">{pairs}</div></div></section>' if pairs else "")
        + cta(f"Build {p['name']} for your site.")
    )
    page(f"/platforms/{p['slug']}/", p["name"], f"{p['name']}: {p['short']}", body, "/platforms/")


def industries():
    hero = film("desert-drone", '<p class="kicker">Industries</p><h1>Where nothing may phone home.</h1><p class="lede">We build for work that runs far from the network or must stay off it: fleets, crowds, energy, water, grids and closed sites across the Gulf and the United States.</p>', "hero mid")
    rows = ""
    for i, (n, f, d, ps) in enumerate(INDUSTRIES):
        links = "".join(f'<a href="{u("/platforms/" + s + "/")}">{e(PBY[s]["name"])} <i>&rarr;</i></a>' for s in ps) or f'<a href="{u("/build/")}">Commission a design <i>&rarr;</i></a>'
        rows += f'<div id="{slugify(n)}">' + film(f, f'<p class="kicker mono">0{i + 1}</p><h2>{e(n)}</h2><p class="lede">{e(d)}</p><div class="plinks">{links}</div>', "band short " + ("right" if i % 2 else "left")) + "</div>"
    page("/industries/", "Industries", "Industries served by Arab American Instruments: fleets, crowd safety, energy, utilities, agriculture, remote sites, telecom and ports.", hero + rows + cta(), "/industries/")


def lab():
    hero = film("smt-line", '<p class="kicker">Design Lab</p><h1>We publish what we learn.</h1><p class="lede">Short notes from the bench: the decisions behind our boards, the numbers behind our links, and what we got wrong. Our customers own their designs; the method we share with everyone.</p>', "hero mid")
    notes = "".join(note_card(n) for n in NOTES)
    page("/lab/", "Design Lab", "Notes from the Arab American Instruments Design Lab on edge hardware, LoRa links, vehicle data and board design.", hero + f'<section class="cards light"><div class="wrap"><div class="grid3">{notes}</div></div></section>' + cta(), "/lab/")
    for n in NOTES:
        out = ""
        for kind, val in n["body"]:
            if kind == "p":
                out += f"<p>{e(val)}</p>"
            elif kind == "h":
                out += f"<h2>{e(val)}</h2>"
            elif kind == "table":
                head = "".join(f"<th>{e(c)}</th>" for c in val[0])
                rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in val[1:])
                out += f'<div class="tw"><table class="data"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
        hero = film(n["film"], f'<p class="kicker"><a href="{u("/lab/")}">Design Lab</a> &middot; {e(n["date"])}</p><h1 class="serif">{e(n["title"])}</h1><p class="lede">{e(n["sub"])}</p>', "hero mid")
        art = f'<article class="article light"><div class="wrap narrow">{out}<p class="byline mono">Design Lab, Arab American Instruments</p></div></article>'
        page(f"/lab/{n['slug']}/", n["title"], n["sub"], hero + art + cta(), "/lab/")


def supply():
    hero = film("terminal-timelapse", '<p class="kicker">Supply chain</p><h1>Own the stack, down to the part.</h1><p class="lede">Most edge devices arrive as sealed boxes from a supply chain you cannot see. Ours arrive with their design, their parts list and their keys.</p>', "hero mid")
    steps = [
        ("Requirement", "What must be sensed, sent or controlled, where, for how long, and what may never leave the site."),
        ("Reference design", "We start from the closest platform and show you the tradeoffs: battery, range, size, cost."),
        ("Your board", "We adapt the schematic, layout and shell to your vehicles, your heat and your rules."),
        ("Pilot run", "A small batch built and tested with you, with every part traced to its maker."),
        ("Field trial", "Units in the field, measured against the targets we set together."),
        ("Handover", "Design files, bill of materials, firmware source and keys. Build the rest wherever you trust."),
    ]
    st = "".join(f'<li><span class="mono n">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></li>' for i, (a, b) in enumerate(steps))
    body = (
        hero
        + f'<section class="statement light"><div class="wrap narrow"><p class="kicker">How we work</p><h2 class="serif">We own the design. You own the supply chain.</h2><p>We work the way a design house does. We keep and improve our reference designs, publish what we learn in the Design Lab, and for each customer we build a purpose built device on top of them. When the work is done, the customer holds everything needed to build it again without us.</p></div></section>'
        + f'<section class="steps"><div class="wrap"><ol>{st}</ol></div></section>'
        + own_strip(True)
        + film("robot-lab", '<p class="kicker">Built where you trust</p><h2>Your fab, your line, your country.</h2><p class="lede">After the pilot, the next thousand units can be built by any qualified manufacturer you choose, in the Gulf, in the United States or anywhere else you trust.</p>', "band right short")
        + film("chip-macro", '<p class="kicker">Traceable by default</p><h2>Every part with its maker and its origin.</h2><p class="lede">Each bill of materials we hand over names the maker of every part and where it was made, so your security team can audit the device the way it audits code.</p>', "band left short")
        + cta()
    )
    page("/supply-chain/", "Supply chain", "How Arab American Instruments hands customers their design files, parts list, firmware and keys so they own their hardware supply chain.", body, "/supply-chain/")


def about():
    hero = film("alula", f'<p class="kicker">About</p><h1>A hardware design company for sovereign systems.</h1><p class="lede">{e(TAGLINE)}</p>', "hero mid")
    body = (
        hero
        + '<section class="statement light"><div class="wrap narrow"><p class="kicker">The idea</p><h2 class="serif">Counterbalance the sealed stack.</h2><p>Technology keeps concentrating. More and more of what runs a country, a fleet or a field sits on hardware designed by a few companies, sealed so that the people who rely on it cannot look inside or change it.</p><p>We think that is a risk every organisation should be able to remove. Arab American Instruments designs edge devices for sensing, satellite and mesh links, and real time control, and builds them so that the customer owns the design and the supply chain, not us and not anyone else.</p><p>We do not chase a catalogue. We keep reference designs, publish what we learn, and build purpose built hardware for each customer, from a single pilot to a national fleet.</p></div></section>'
        + film("engineer-board", '<p class="kicker">The bench</p><h2>Engineers who own the whole board.</h2><p class="lede">Schematic, layout, firmware and shell under one roof, so every decision on the device is one we can explain and hand over.</p>', "band left short")
        + '<section class="hq">' + film("riyadh-day", '<p class="kicker mono">HQ 01</p><h2>Riyadh</h2><p>Saudi Arabia</p>', "half") + film("dallas-dusk", '<p class="kicker mono">HQ 02</p><h2>Dallas</h2><p>Texas, United States</p>', "half") + '</section>'
        + '<section class="statement"><div class="wrap narrow center"><p class="kicker">Ownership</p><h2 class="serif">A fully owned subsidiary of CodeNinja.</h2><p>Arab American Instruments brings hardware design into the CodeNinja group, alongside its work on sovereign AI systems for governments and enterprises.</p></div></section>'
        + cta()
    )
    page("/about/", "About", "Arab American Instruments is a hardware design company headquartered in Riyadh and Dallas, a fully owned subsidiary of CodeNinja.", body, "/about/")


def build_page():
    opts = "".join(f'<option value="{e(p["name"])}">{e(p["name"])} ({e(p["kind"])})</option>' for p in PRODUCTS)
    qty = [("Pilot run, 10 to 100 units (recommended first step)", True), ("Prototype, under 10 units", False), ("Production, 100 to 1,000 units", False), ("Fleet or national scale, over 1,000 units", False)]
    qopts = "".join(f'<label class="opt"><input type="radio" name="Quantity" value="{e(q)}"{" checked" if c else ""}><span>{e(q)}</span></label>' for q, c in qty)
    env = [("Air gapped: nothing may leave the site (recommended default)", True), ("Private network or private cloud", False), ("Public cellular or satellite is acceptable", False), ("Not known yet", False)]
    eopts = "".join(f'<label class="opt"><input type="radio" name="Connectivity" value="{e(q)}"{" checked" if c else ""}><span>{e(q)}</span></label>' for q, c in env)
    form = f'''<section class="formwrap light"><div class="wrap narrow">
<p class="kicker">Request a build</p><h2 class="serif">Tell us the job. We design the device.</h2>
<p>No prices on this site, because every unit is made for its owner. Send the outline below and an engineer replies with questions, a reference design and a plan for a pilot.</p>
<form id="buildform">
<div class="two"><label>Name<input name="Name" required autocomplete="name"></label><label>Organisation<input name="Organisation" required autocomplete="organization"></label></div>
<div class="two"><label>Work email<input type="email" name="Email" required autocomplete="email"></label><label>Country<input name="Country" placeholder="Saudi Arabia, United States, ..."></label></div>
<label>Closest platform<select name="Platform"><option value="Not sure yet">Not sure yet, recommend one</option>{opts}<option value="Custom controller">Custom controller</option></select></label>
<label>What must it sense, send or control?<textarea name="Requirement" rows="4" required placeholder="For example: driver and road cameras for 800 heavy trucks, vehicle data from the FMS port, events over LTE."></textarea></label>
<fieldset><legend>Where will the data go?</legend>{eopts}</fieldset>
<fieldset><legend>How many units to start?</legend>{qopts}</fieldset>
<label>Timeline<input name="Timeline" placeholder="For example: pilot in Q1 2027"></label>
<button class="btn" type="submit">Send the request</button>
<p class="fine">This opens your email app with the request filled in, addressed to {CONTACT}. Nothing is stored on this site.</p>
<p class="sent" hidden>Your email app should now be open. If it did not open, write to {CONTACT}.</p>
</form></div></section>
<script>(function(){{var m=location.search.match(/platform=([a-z-]+)/);if(!m)return;var map={json.dumps({p["slug"]: p["name"] for p in PRODUCTS})};var s=document.querySelector('select[name=Platform]');if(map[m[1]])s.value=map[m[1]];}})();</script>'''
    hero = film("print-timelapse", '<p class="kicker">Made to order</p><h1>Request a build.</h1><p class="lede">From a single pilot to a national fleet. You keep the design, the parts list and the keys.</p>', "hero short")
    page("/build/", "Request a build", "Request a made to order edge device from Arab American Instruments.", hero + form, "")


def credits():
    lines = open(os.path.join(ROOT, "assets/video/CREDITS.md")).read().splitlines()
    items = "".join(f"<li>{e(l[2:])}</li>" for l in lines if l.startswith("- "))
    body = f'<section class="article light" style="padding-top:140px"><div class="wrap narrow"><h1 class="serif">Credits</h1><p>Every banner video on this site is real world footage from Pexels under the Pexels License, checked frame by frame for brands and signage before use. Product images are our own renders and board layouts.</p><ul class="credits">{items}</ul></div></section>'
    page("/credits/", "Credits", "Video and image credits for the Arab American Instruments site.", body)


def extras():
    with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in PAGES:
            fh.write(f"<url><loc>{SITE_URL}{p}</loc></url>\n")
        fh.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"), ignore=shutil.ignore_patterns("CREDITS.md"))
    home(); platforms()
    for p in PRODUCTS:
        product_page(p)
    industries(); lab(); supply(); about(); build_page(); credits(); extras()
    print(f"built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
