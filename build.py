#!/usr/bin/env python3
"""Build the Arab American Instruments site into ./site.

Run: python3 build.py
Pages, products and Design Lab notes live in this file as data. Videos are in
assets/video (credits in assets/video/CREDITS.md); product images in
assets/img/stock (Pexels photos of the use case, never our own boards). House style: no hyphens or dashes in copy, no prices,
no customer names, every banner a real world video.
"""
import html
import json
import os
import shutil
import subprocess
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
# Served at the domain root (GitHub Pages with the custom domain arabamerican.ai).
BASE = os.environ.get("AAI_BASE", "")
SITE_URL = os.environ.get("AAI_SITE_URL", "https://arabamerican.ai")
DOMAIN = "arabamerican.ai"
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
        "slug": "fleet-vision-unit",
        "name": "Fleet Vision Unit",
        "line": "sensing",
        "status": "fab",
        "kind": "AI cameras for the cab and the road",
        "film": "dashcam-desert",
        "short": "Watches the driver and the road, runs the models on the unit and sends events and clips to your platform. Reads the vehicle's own data through the Vehicle Interface Module.",
        "images": [
            ("driving.jpg", "The road view: collision warnings, following distance and lane departure"),
            ("truck-driver-2.jpg", "The cab view: drowsiness, distraction and phone use, day and night"),
            ("trucks-parked.jpg", "One unit per vehicle, from a pilot batch to a national fleet"),
        ],
        "sections": [
            ("Driver, day and night", [
                "Drowsiness, distraction and phone use",
                "Seatbelt on or off",
                "Who is driving, matched to enrolled drivers",
                "Camera covered or no driver in the seat",
            ]),
            ("Road", [
                "Forward collision warning for vehicles, pedestrians and animals",
                "Following distance, lane departure and swerving",
                "Speed limit signs and traffic lights",
            ]),
            ("Location and driving", [
                "Live position, speed, heading and route history",
                "Trips, stops and idling",
                "Harsh braking, acceleration and cornering",
                "Crash, impact and rollover, and a knock while parked",
            ]),
            ("Video and status", [
                "A short clip with every event, and on a button press",
                "Continuous recording on the unit, pulled for any time later",
                "Live view on request",
                "Tamper, power loss and camera blocked alerts",
            ]),
        ],
        "specs": [
            ("Where it runs", "On the unit; only events and clips leave the vehicle"),
            ("Operating system", "Linux or Android, your choice, signed with keys you hold"),
            ("Links", "Cellular and GPS, with store and forward when there is no signal"),
            ("Vehicle data", "Through the Vehicle Interface Module"),
            ("In the cab", "Spoken alerts and a driver button"),
            ("Environment", "Sealed housing, built for desert heat"),
        ],
        "pairs": ["vehicle-interface-module"],
    },
    {
        "slug": "vehicle-interface-module",
        "name": "Vehicle Interface Module",
        "line": "controls",
        "status": "final",
        "kind": "Vehicle data and power gateway",
        "film": "night-highway",
        "short": "Plugs into the vehicle's own port, reads speed, fuel, faults, hours and load, and powers the camera unit. Works on light trucks and heavy fleets alike.",
        "images": [
            ("truck-cab-bw.jpg", "The module sits out of sight below the dash and plugs into the vehicle's own port"),
            ("cluster.jpg", "Speed, fuel, faults and hours read from the vehicle, not estimated"),
        ],
        "sections": [
            ("Any vehicle", [
                "Ignition on and off",
                "Battery voltage and engine running",
                "Power for the camera unit, with a last message on power loss",
            ]),
            ("Light and medium trucks, diagnostic port", [
                "Engine speed, vehicle speed and coolant temperature",
                "Engine load and accelerator pedal",
                "Fault codes and warning lamps",
                "Vehicle ID, and fuel level and rate where the vehicle reports them",
            ]),
            ("Heavy trucks, fleet management port", [
                "Total fuel used, live fuel rate and economy",
                "Odometer, engine hours and distance to next service",
                "Brake, clutch and cruise control",
                "Axle weight, AdBlue level and driver hours where a tachograph is fitted",
            ]),
        ],
        "specs": [
            ("Ports", "Standard diagnostic and fleet management harnesses"),
            ("Power", "Vehicle battery in, regulated power out to the camera unit"),
            ("Fallback", "Where the vehicle gives no speed or distance, GPS does"),
        ],
        "pairs": ["fleet-vision-unit"],
    },
    {
        "slug": "field-band",
        "name": "Field Band",
        "line": "sensing",
        "status": "design",
        "kind": "Wearable for people in the field",
        "film": "walker-desert",
        "short": "A slim, sealed band that reports position, heart rate and skin temperature over a long range radio, calls for help with one button and lasts days on a charge.",
        "images": [
            ("watch-1.jpg", "A sealed band on the wrist reports position, heart rate and skin temperature for days"),
            ("watch-3.jpg", "One recessed button calls for help on every path at once"),
            ("tablet-engineer.jpg", "Guides and supervisors see their group on a hub or a tablet, with no network needed"),
        ],
        "sections": [
            ("What it reports", [
                "Position",
                "Heart rate and skin temperature",
                "Falls and stillness",
                "Battery level and an off wrist alert",
            ]),
            ("When something goes wrong", [
                "A recessed SOS button that goes out on every path at once",
                "Confirmation back to the wearer once help has the message",
                "A separation alarm when the wearer loses their group",
                "A light that shows only in an emergency, so rescuers can find the wearer at night",
            ]),
            ("Two builds", [
                "Long range radio only: the slimmest band and the longest charge",
                "Long range radio plus cellular: calls for help alone wherever there is phone signal",
            ]),
        ],
        "specs": [
            ("Radio", "Long range mesh radio; optional cellular"),
            ("Battery", "Several days per charge"),
            ("Sealing", "Sealed against rain and immersion, including the button"),
            ("Security", "Every message encrypted; charges only on your own docks"),
        ],
        "pairs": ["guide-hub", "patrol-gateway", "solar-relay", "charging-dock"],
    },
    {
        "slug": "guide-hub",
        "name": "Guide Hub",
        "line": "satcoms",
        "status": "concept",
        "kind": "Backpack gateway",
        "film": "radio-site",
        "short": "Carried at the front and back of a group, it collects every band in range and sends the data on by cellular, or by satellite when there is nothing else.",
        "images": [("radio-1.jpg", "The guide at the back of every group carries the hub and stays in touch"), ("tablet-engineer.jpg", "A phone or tablet app shows the guide every band in the group")],
        "sections": [
            ("What it does", [
                "Collects every band in the group",
                "Sends on by cellular, with satellite messaging as backup",
                "Queues messages locally and catches up when a link returns",
                "Shows the group on the guide's phone or tablet",
            ]),
        ],
        "specs": [
            ("Power", "Swappable pack, charged nightly"),
            ("Build", "Rugged sealed case, antenna on the strap"),
        ],
        "pairs": ["field-band", "patrol-gateway"],
    },
    {
        "slug": "patrol-gateway",
        "name": "Patrol Gateway",
        "line": "satcoms",
        "status": "concept",
        "kind": "Roof unit for patrol and safety vehicles",
        "film": "mojave-hwy",
        "short": "Reaches much further than a backpack. In search mode a missing band reports every few seconds and the display shows the signal strengthening as the vehicle closes in.",
        "images": [("truck-cab-bw.jpg", "A roof antenna on a magnetic mount and a rugged tablet in the cab"), ("radio-tower.jpg", "Cellular and satellite links reach out where the mesh ends")],
        "sections": [
            ("What it does", [
                "Long range mesh gateway with a roof antenna",
                "Cellular and satellite links",
                "A live map on a rugged tablet",
                "Search mode for a missing wearer",
            ]),
        ],
        "specs": [("Power", "Vehicle supply")],
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
        "images": [("solar-cam-1.jpg", "A sealed box, a panel and a battery on any pole"), ("weather-station.jpg", "Sensors and relays share the same pole and the same link"), ("radio-tower.jpg", "The last pole carries the uplink")],
        "sections": [
            ("What it does", [
                "Gateway for nearby bands and sensors",
                "Long range link to the next pole",
                "Health reports: battery, solar and temperature",
                "Uplink build adds cellular, satellite or microwave",
            ]),
        ],
        "specs": [
            ("Power", "Solar panel and a heat tolerant battery, sized for days without sun"),
            ("Bandwidth", "Hundreds of wearers on a narrowband link"),
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
        "short": "Charges, tests and pairs bands in one tray, and refuses anything that is not yours.",
        "images": [("radios.jpg", "Every unit charged, tested and paired in one place before it goes out")],
        "sections": [
            ("What it does", [
                "Charges a camp's bands overnight",
                "Accepts only your own bands",
                "A light per slot, and an alert if a battery fails",
                "Pairs bands to people, updates firmware and runs self tests",
            ]),
        ],
        "specs": [("Power", "Mains or generator")],
        "pairs": ["field-band"],
    },
]
PBY = {p["slug"]: p for p in PRODUCTS}

INDUSTRIES = [
    ("Fleets and logistics", "truck-depot", "Driver safety, vehicle data and video for fleets of heavy trucks.", ["fleet-vision-unit", "vehicle-interface-module"]),
    ("Crowd and walker safety", "walkers-desert", "Bands, hubs and relays that keep large groups covered on long routes far from the network.", ["field-band", "guide-hub", "solar-relay"]),
    ("Energy and pipelines", "pumpjacks-desert", "Sensing and control on wells, valves and lines, on links you own.", ["solar-relay", "vehicle-interface-module"]),
    ("Utilities and grid", "substation", "Monitoring and control near the equipment, isolated from the public internet.", []),
    ("Agriculture and water", "irrigation", "Low power sensing and pump control across fields and wells.", ["solar-relay"]),
    ("Government and critical sites", "military-exercise", "Vehicles, people and sites that must run inside a perimeter, on air gapped links, with hardware you can audit part by part.", ["fleet-vision-unit", "field-band", "patrol-gateway", "solar-relay"]),
    ("Remote and closed sites", "desert-aerial", "Border, camp and range sites where nothing may leave the perimeter.", ["patrol-gateway", "guide-hub"]),
    ("Telecom and satellite", "cell-tower", "Edge radios, relays and terminals for networks that must keep running.", ["solar-relay", "patrol-gateway"]),
    ("Ports and supply chain", "harbor-night", "Tracking and sensing for yards, terminals and the trucks that serve them.", ["fleet-vision-unit"]),
]

NOTES = [
    {
        "slug": "what-is-air-gapped-ai",
        "title": "What is air gapped AI?",
        "sub": "Air gapped AI runs its models on devices and servers that never touch a public network. Here is what that takes in the field.",
        "date": "24 Nov 2026",
        "film": "radio-site",
        "body": [
            ("p", "Air gapped AI is AI that runs with no path to a public network. The models, the data they see and the answers they give all stay inside one perimeter."),
            ("p", "The idea is old in computing. What changed is that vision and language models now fit on a device at the edge, so the gap no longer costs you the intelligence."),
            ("h", "Connected AI and air gapped AI, side by side"),
            ("table", [
                ["Question", "Connected AI", "Air gapped AI"],
                ["Where the model runs", "A provider's cloud", "On the device and on your servers"],
                ["Where the data goes", "Out to the provider", "Nowhere outside the perimeter"],
                ["Who holds the weights", "The provider", "You, as open weights you host"],
                ["How updates arrive", "Pushed by the provider", "Carried in and approved by you"],
                ["What happens with no signal", "The service stops", "Work continues; devices store and forward"],
            ]),
            ("h", "Where air gapped AI runs"),
            ("p", "A truck cab far from coverage. A gate at a closed site. A line of poles across open desert. A walking route crowded with people and short on bandwidth."),
            ("p", "In each case the model sits where the event happens. The device decides, records and alerts on its own, then passes the event along a link the operator owns."),
            ("h", "What to ask a supplier"),
            ("p", "Ask where the weights live and who can change them. Ask what the device does when every link is down. Ask whether any part of the system calls home, even for a licence check."),
            ("p", "When the answers are open weights you hold, full operation offline and no outbound connection, the system is air gapped."),
            ("links", [("Air gapped AI operations", "/solutions/airgap/"), ("Sovereign edge AI", "/solutions/sovereignty/"), ("Edge AI devices", "/products/")]),
        ],
    },
    {
        "slug": "what-a-truck-will-tell-you",
        "title": "What a truck will tell you",
        "sub": "The data you get depends on the port the truck has. The table below sets out what each port provides.",
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
]

# ---------------------------------------------------------------- positioning data

# A fixed site camera unit joins the line.
PRODUCTS.append({
    "slug": "site-camera",
    "name": "Site Camera",
    "line": "sensing",
    "status": "concept",
    "kind": "Fixed AI camera for yards, gates and sites",
    "film": "cams-sunset",
    "short": "The Fleet Vision Unit camera and AI stack in a fixed housing. Watches a gate, a yard or a line, runs the models on the unit and keeps the video on site.",
    "images": [("solar-cam-2.jpg", "A fixed unit on a pole, powered by the sun where there is no mains"), ("pole-cam-2.jpg", "Gates, yards and perimeter lines watched around the clock")],
    "sections": [
        ("What it watches", [
            "People and vehicles in zones you draw, at any hour",
            "Gates, loading bays and perimeter lines",
            "Safety vests, helmets and restricted areas",
            "Plates at close range",
        ]),
        ("How it stays yours", [
            "Models run on the unit; only events and clips leave it, and only to where you say",
            "Continuous recording kept on the unit, pulled on request",
            "Works over LoRa for events alone, or over your own network for video",
        ]),
    ],
    "specs": [
        ("Where it runs", "On the unit; only events and clips leave the site"),
        ("Operating system", "Linux or Android, your choice, signed with keys you hold"),
        ("Power", "Mains, PoE or the Solar Relay's panel and battery"),
        ("Links", "Your network, cellular, or LoRa for events only"),
    ],
    "pairs": ["fleet-vision-unit", "solar-relay"],
})
PBY = {p["slug"]: p for p in PRODUCTS}

# Product categories. Each holds devices from PRODUCTS.
CATEGORIES = [
    {
        "slug": "cameras", "name": "Vision at the Edge", "film": "dashcam-desert",
        "tag": "Cameras that run vision models on the unit",
        "title": "Vision models on the device. Nothing leaves that you did not choose.",
        "body": "Cab and road cameras, and fixed cameras for gates, yards and lines. The vision models run on the unit, so only events and short clips leave it, and the video stays on your site.",
        "devices": ["fleet-vision-unit", "site-camera"],
        "outcomes": ["safety", "security", "compliance"],
    },
    {
        "slug": "telematics", "name": "Vehicle Telematics", "film": "night-highway",
        "tag": "The vehicle's own data, on your terms",
        "title": "Every vehicle's own data, on your terms.",
        "body": "A small gateway that plugs into the vehicle's own port, reads speed, fuel, faults, hours and load, adds GPS, and powers the camera unit. Where the vehicle gives nothing, GPS fills in.",
        "devices": ["vehicle-interface-module"],
        "outcomes": ["efficiency", "compliance", "security"],
    },
    {
        "slug": "workforce", "name": "People in the Field", "film": "walker-desert",
        "tag": "Wearables and hubs that work with no network at all",
        "title": "Know where every person is, and that they are well.",
        "body": "A sealed wrist band that reports position, heart rate and skin temperature for days on a charge, calls for help with one button, and keeps working when there is no signal of any kind.",
        "devices": ["field-band", "guide-hub", "charging-dock"],
        "outcomes": ["safety", "coverage"],
    },
    {
        "slug": "network", "name": "Air Gapped Links", "film": "dish-sunset",
        "tag": "Mesh, relays and uplinks you control end to end",
        "title": "Links that hold when the network does not, and never need it.",
        "body": "Mesh between devices, solar relays pole to pole, vehicle gateways, and one uplink only where you decide there should be one. Every message queues and catches up; nothing is dropped and nothing leaves without you.",
        "devices": ["solar-relay", "patrol-gateway", "guide-hub"],
        "outcomes": ["coverage", "security"],
    },
    {
        "slug": "command", "name": "Command", "film": "control-room",
        "tag": "The platform where everything lands, hosted by you",
        "title": "One screen for the whole operation, inside your perimeter.",
        "body": "Live map, events and clips, alerts, trips and search mode, running in your data centre, on a site server, or on a laptop in camp. It speaks the devices' own protocol and runs the same language and vision models you run at the edge, so the stack stays yours end to end.",
        "devices": [],
        "outcomes": ["efficiency", "compliance", "security"],
        "features": [
            ("Live map", "Every vehicle, person and relay, with trips, stops and routes."),
            ("Events and clips", "Drowsiness, collision warnings, SOS and falls, each with its video and position."),
            ("Ask it in words", "A language model, hosted with the platform, answers questions over the fleet's own data."),
            ("Search mode", "A missing band reports every few seconds and the display shows the signal strengthening as the searcher closes in."),
            ("Device health", "Online, signal, storage, temperature, tamper and power loss for every unit."),
            ("Your hosting", "Air gapped by default. Your servers, your keys, your retention rules."),
        ],
    },
]
CBY = {c["slug"]: c for c in CATEGORIES}
CAT_OF = {d: c["slug"] for c in CATEGORIES for d in c["devices"]}

# One short line per device, in the Anduril manner.
TAGLINES = {
    "fleet-vision-unit": "Vision models on the unit. Only events leave the vehicle.",
    "vehicle-interface-module": "Vehicle data and power from the vehicle's own port.",
    "field-band": "Position and vital signs with no network.",
    "guide-hub": "Portable gateway for every band in a group.",
    "patrol-gateway": "Mesh gateway and search mode for patrol vehicles.",
    "solar-relay": "Solar powered mesh relay for poles and remote sites.",
    "charging-dock": "Charges, tests and pairs bands. Accepts only your own.",
    "site-camera": "Fixed AI camera. Recording kept on site.",
}

SOLUTIONS = [
    {
        "slug": "sovereignty", "name": "Sovereignty", "film": "chip-macro",
        "tag": "Own the design, the parts, the firmware and the keys",
        "title": "A stack nobody else holds the keys to.",
        "body": "Every device is handed over with its design files, its bill of materials naming the maker of every part, its firmware source and its signing keys. You can audit it, rebuild it, and run it without us.",
        "points": ["Design files, bill of materials and firmware source handed to the customer", "Signing keys held by you; no vendor update path you did not approve", "Every part traced to its maker and origin", "Build the next thousand units at any manufacturer you trust", "No subscription, no cloud dependency, no remote kill switch"],
        "devices": ["fleet-vision-unit", "vehicle-interface-module", "solar-relay"],
        "industries": ["Government and critical sites", "Utilities and grid", "Energy and pipelines"],
    },
    {
        "slug": "airgap", "name": "Air Gapped Operations", "film": "solar-desert",
        "tag": "Run the whole operation with nothing leaving the perimeter",
        "title": "Everything works inside the perimeter. Nothing has to leave.",
        "body": "Models run on the devices. Devices talk to each other over your own mesh. Command runs on your own servers. Where there is no network, nothing is lost: every device stores and forwards, and the uplink exists only where you decide.",
        "points": ["Vision and language models run on the device and on your servers", "Mesh links between devices with no public network in the loop", "Store and forward on every unit", "Command hosted in your data centre, on a site server, or in camp", "One uplink, where you choose, by cellular, satellite or microwave"],
        "devices": ["solar-relay", "patrol-gateway", "guide-hub", "field-band"],
        "industries": ["Government and critical sites", "Remote and closed sites", "Crowd and walker safety"],
    },
    {
        "slug": "safety", "name": "Safety and Risk", "film": "dashcam-desert",
        "tag": "Fewer accidents on the road and in the field",
        "title": "Detect the drowsy driver and the fallen worker in time.",
        "body": "The cab camera sees eyes closing, phone use and a missing seatbelt and alerts the driver in the cab. The road camera warns of a collision ahead. The band detects a fall and sends an SOS on every path at once.",
        "points": ["Drowsiness, distraction, phone use and seatbelt alerts spoken in the cab", "Forward collision, tailgating and lane departure warnings", "Harsh braking, cornering and impact events with video", "Falls, stillness and SOS from the wrist, confirmed back to the wearer"],
        "devices": ["fleet-vision-unit", "field-band", "guide-hub"],
        "industries": ["Fleets and logistics", "Crowd and walker safety", "Energy and pipelines"],
    },
    {
        "slug": "security", "name": "Security", "film": "tactical",
        "tag": "Protect the assets and the devices that watch them",
        "title": "Tamper proof devices that report their own tampering.",
        "body": "Case opened, unit unmounted, camera covered, power cut, a knock while parked: the unit reports each one, and sends a last message before it goes dark. Site cameras watch gates, yards and perimeter lines around the clock.",
        "points": ["Tamper, unmount and camera blocked alerts", "Parked impact and tow away detection", "A last message on power loss", "Perimeter and gate watch with the models on the unit", "Every message encrypted end to end"],
        "devices": ["fleet-vision-unit", "site-camera", "vehicle-interface-module"],
        "industries": ["Government and critical sites", "Ports and supply chain", "Utilities and grid"],
    },
    {
        "slug": "compliance", "name": "Compliance and Records", "film": "terminal-timelapse",
        "tag": "Trips, hours, video and audits you can stand behind",
        "title": "A record of every trip, every event and every part.",
        "body": "Driver hours from the tachograph, odometer and engine hours from the vehicle, continuous recording on the unit for any time later, and a bill of materials that names the maker of every component.",
        "points": ["Trips with start, end, distance, duration, stops and idling", "Driver hours where a tachograph is fitted, and who was driving", "Continuous recording on the unit, pulled for any time later", "Event clips with position and time", "A traceable bill of materials for the device itself"],
        "devices": ["vehicle-interface-module", "fleet-vision-unit"],
        "industries": ["Fleets and logistics", "Ports and supply chain", "Utilities and grid"],
    },
    {
        "slug": "efficiency", "name": "Efficiency and Cost", "film": "truck-desert",
        "tag": "Fuel, idling, service and utilisation from the source",
        "title": "Cut fuel and downtime with numbers from the vehicle itself.",
        "body": "Live fuel rate, total fuel used, idling, engine load and distance to next service, read from the vehicle rather than estimated. Routes and utilisation from GPS on every vehicle and relay.",
        "points": ["Fuel level, live fuel rate and economy", "Idling and harsh driving by driver", "Fault codes, warning lamps and distance to next service", "Odometer, engine hours and axle weight", "Routes and utilisation across the fleet"],
        "devices": ["vehicle-interface-module", "fleet-vision-unit"],
        "industries": ["Fleets and logistics", "Agriculture and water", "Energy and pipelines"],
    },
    {
        "slug": "coverage", "name": "Coverage Off the Network", "film": "military-exercise",
        "tag": "Keep working where there is no signal",
        "title": "The desert, the sea and the closed site, all covered.",
        "body": "Devices store everything with no signal and send it when a link returns. Bands reach hubs, hubs reach vehicles, relays pass messages pole to pole, and one uplink reaches out by cellular, satellite or microwave.",
        "points": ["Store and forward on every device", "Mesh between bands, hubs, vehicles and poles", "Solar relays that run for days without sun", "Cellular, satellite or microwave uplink where there is finally a link", "Hundreds of wearers on a narrowband link"],
        "devices": ["solar-relay", "patrol-gateway", "guide-hub", "field-band"],
        "industries": ["Crowd and walker safety", "Remote and closed sites", "Telecom and satellite"],
    },
]
SBY = {s["slug"]: s for s in SOLUTIONS}

# The four pillars under the home banner. Each carries the banner line.
PILLARS = [
    ("sovereignty", "Sovereign by design", "You own the design, the parts, the firmware and the keys. We hand it all over with the build.", "chip-macro", "/solutions/sovereignty/"),
    ("airgap", "Air gapped by default", "Models on the device, mesh between devices, Command on your servers. Nothing leaves that you did not choose.", "solar-desert", "/solutions/airgap/"),
    ("edge", "AI at the edge", "Vision and language models run on the hardware itself, on our own AI platform, with no cloud in the loop.", "engineer-scope", "/platform/"),
    ("field", "Built for the field", "Low power, sealed, store and forward, built inside your perimeter for your vehicles, your sites and your climate.", "truck-desert", "/hardware/"),
]

# Our AI platform. The parent stack, named.
PLATFORM = [
    ("01", "Praxis", "Designs the system: what each device senses, which model runs where, what the object model holds and who approves every action."),
    ("02", "Hyper Ontology", "The object model the devices and Command share: vehicles, people, sites, events and the relations between them."),
    ("03", "Hyper Pragma", "Runs the models and the workflows on the device and on your servers, air gapped, with the same code in both places."),
    ("04", "Hyper Engram", "The memory. What the fleet learned, what was decided and why, kept inside your perimeter and queryable in words."),
]
MODELS = [
    ("Vision models", "Driver state, road events, people and vehicles in zones, plates, helmets and vests, running on the unit at full frame rate."),
    ("Language models", "Hosted with Command on your servers. Ask the fleet a question in words and get an answer from its own data."),
    ("Open weights, your hosting", "Every model we ship runs from weights you hold, on hardware you own, with no outbound connection."),
]

# ---------------------------------------------------------------- chrome

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Inter:wght@400;500&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">'

MARK = '<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M7 27 Q20 4 33 27" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="7" cy="27" r="3" fill="currentColor"/><circle cx="33" cy="27" r="3" fill="currentColor"/></svg>'


def menu_products():
    cats = "".join(f'<a href="{u("/products/" + c["slug"] + "/")}"><b>{e(c["name"])}</b><span>{e(c["tag"])}</span></a>' for c in CATEGORIES)
    return f'<div class="ddgrid"><div class="ddcol">{cats}</div><div class="ddside"><span class="mono">Hardware</span><a href="{u("/hardware/")}"><b>All hardware</b><span>Every device in the stack</span></a><a href="{u("/platform/")}"><b>AI platform</b><span>The models and the stack that run on the hardware</span></a><a href="{u("/build/")}"><b>Request a deployment</b><span>From a pilot to a fleet, inside your perimeter</span></a></div></div>'


def menu_solutions():
    sols = "".join(f'<a href="{u("/solutions/" + s["slug"] + "/")}"><b>{e(s["name"])}</b><span>{e(s["tag"])}</span></a>' for s in SOLUTIONS)
    inds = "".join(f'<a href="{u("/industries/")}#{slugify(n)}"><b>{e(n)}</b></a>' for n, _, _, _ in INDUSTRIES)
    return f'<div class="ddgrid"><div class="ddcol">{sols}</div><div class="ddside"><span class="mono">Industries</span>{inds}</div></div>'


def header(active=""):
    def grp(name, href, menu):
        on = " on" if active.startswith(href) else ""
        return f'<div class="grp"><a class="tab{on}" href="{u(href)}">{name}<svg viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.2"/></svg></a><div class="dd">{menu}</div></div>'
    nav = grp("Products", "/products/", menu_products()) + grp("Solutions", "/solutions/", menu_solutions()) + f'<a class="tab{" on" if active == "/platform/" else ""}" href="{u("/platform/")}">Platform</a>' + f'<a class="tab{" on" if active == "/lab/" else ""}" href="{u("/lab/")}">Design Lab</a>' + f'<a class="tab{" on" if active == "/supply-chain/" else ""}" href="{u("/supply-chain/")}">Supply chain</a>' + f'<a class="tab{" on" if active == "/about/" else ""}" href="{u("/about/")}">About</a>'
    mobile = ""
    for title, items in [("Products", [(c["name"], "/products/" + c["slug"] + "/") for c in CATEGORIES] + [("All hardware", "/hardware/"), ("AI platform", "/platform/")]), ("Solutions", [(s["name"], "/solutions/" + s["slug"] + "/") for s in SOLUTIONS] + [("Industries", "/industries/")]), ("Company", [("Design Lab", "/lab/"), ("Supply chain", "/supply-chain/"), ("About", "/about/")])]:
        mobile += f'<span class="mono">{title}</span>' + "".join(f'<a href="{u(h)}">{e(n)}</a>' for n, h in items)
    return f'''<header class="top"><div class="pill">
<a class="brand" href="{u("/")}">{MARK}<span>Arab American Instruments</span></a>
<nav id="nav">{nav}</nav>
<a class="btn small" href="{u("/build/")}">Request a deployment</a>
<button class="menu" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</div></header>
<div class="mnav" id="mnav">{mobile}<a class="btn" href="{u("/build/")}">Request a deployment</a></div>'''


def footer():
    prods = "".join(f'<a href="{u("/products/" + c["slug"] + "/")}">{e(c["name"])}</a>' for c in CATEGORIES) + f'<a href="{u("/hardware/")}">All hardware</a><a href="{u("/platform/")}">AI platform</a>'
    sols = "".join(f'<a href="{u("/solutions/" + s["slug"] + "/")}">{e(s["name"])}</a>' for s in SOLUTIONS) + f'<a href="{u("/industries/")}">Industries</a>'
    comp = "".join(f'<a href="{u(h)}">{n}</a>' for n, h in [("Supply chain", "/supply-chain/"), ("Design Lab", "/lab/"), ("Request a deployment", "/build/")])
    return f'''<footer class="foot"><div class="wrap">
<div class="ftop"><p class="tag">{e(TAGLINE)}</p><a class="btn ghost" href="{u("/build/")}">Request a deployment</a></div>
<div class="fgrid">
<div><h4>Products</h4>{prods}</div>
<div><h4>Solutions</h4>{sols}</div>
<div><h4>Company</h4>{comp}</div>
<div><h4>Headquarters</h4><p>Riyadh, Saudi Arabia</p><p>Dallas, Texas, United States</p></div>
</div>
<div class="legal"><span>Arab American Instruments is a fully owned subsidiary of CodeNinja</span><span>&copy; 2026 Arab American Instruments</span></div>
</div></footer>'''


SCRIPT = '''<script>
(function(){
  function solid(){ document.body.classList.toggle('scrolled', window.scrollY>40); }
  solid(); window.addEventListener('scroll', solid, {passive:true});
  var mb=document.querySelector('.menu');
  if(mb){ mb.addEventListener('click',function(){ var o=document.body.classList.toggle('open'); mb.setAttribute('aria-expanded',o); }); }
  var grps=[].slice.call(document.querySelectorAll('.grp'));
  grps.forEach(function(g){ var t=g.querySelector('.tab');
    t.addEventListener('click',function(ev){ if(window.matchMedia('(hover: none)').matches||ev.detail===0){ ev.preventDefault(); var was=g.classList.contains('open'); grps.forEach(function(x){x.classList.remove('open')}); if(!was) g.classList.add('open'); } }); });
  document.addEventListener('click',function(ev){ if(!ev.target.closest('.grp')) grps.forEach(function(x){x.classList.remove('open')}); });
  var vids=[].slice.call(document.querySelectorAll('video[data-src]'));
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load(v){ if(!v.src){ v.src=v.getAttribute('data-src'); } }
  if(!reduce && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){ es.forEach(function(x){ var v=x.target;
      if(x.isIntersecting){ load(v); var p=v.play(); if(p&&p.catch){p.catch(function(){});} } else { v.pause(); } }); },{rootMargin:'200px 0px'});
    vids.forEach(function(v){ io.observe(v); });
  }
  var f=document.getElementById('buildform');
  if(f){ f.addEventListener('submit',function(ev){ ev.preventDefault();
    var d=new FormData(f), lines=[]; d.forEach(function(val,k){ if(val) lines.push(k+': '+val); });
    var subj='Build request: '+(d.get('Organisation')||'')+' '+(d.get('Platform')||'');
    window.location.href='mailto:%s?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(lines.join('\\n'));
    f.querySelector('.sent').hidden=false; }); }
})();
</script>''' % CONTACT


# Search engine ownership proofs (Search Console URL prefix property, Bing Webmaster Tools). Keep them: removal unverifies.
GOOGLE_VERIFY_FILE = "google5c8034f5c559d4ab.html"
BING_VERIFY = "C0BA30668F739D132B60D2147D569A8E"

ORG_ID = SITE_URL + "/#organization"
CRUMBS = {"/": "Home", "/products/": "Products", "/hardware/": "Hardware", "/solutions/": "Solutions", "/lab/": "Design Lab"}

# Search titles: what a searcher types comes first; locked terms lead on their owning page (routine/locked.json).
# The home page is frozen (brand query at Google position 1) and is not listed here. H1 and breadcrumbs keep the short title.
SEO_TITLES = {
    "/hardware/": "Sovereign AI Hardware",
    "/products/": "Edge AI Devices for Air Gapped Sites",
    "/solutions/airgap/": "Air Gapped AI for Operations Off the Network",
    "/products/cameras/": "Edge AI Camera for Fleets, Gates and Sites",
    "/solutions/sovereignty/": "Sovereign Edge AI Inside Your Perimeter",
    "/platform/": "Edge AI Platform: Models On the Device",
    "/about/": "About Arab American Instruments, Riyadh and Dallas",
    "/build/": "Request an Edge AI Deployment",
    "/solutions/": "Sovereign AI Solutions for Edge Operations",
    "/industries/": "Edge AI by Industry: Fleets, Energy, Ports",
    "/lab/": "Design Lab: Notes on Edge AI Hardware",
    "/supply-chain/": "Own Your Hardware Supply Chain",
    "/products/command/": "Self Hosted Command Platform for Edge Devices",
    "/products/telematics/": "Vehicle Telematics on Your Own Servers",
    "/products/network/": "Air Gapped Satellite and Mesh Links",
    "/products/workforce/": "Wearables for People in the Field",
    "/solutions/compliance/": "Compliance and Records Kept On Site",
    "/solutions/coverage/": "Edge AI Coverage Off the Network",
    "/solutions/efficiency/": "Fleet Efficiency and Cost with Edge AI",
    "/solutions/safety/": "Safety and Risk with Edge AI",
    "/solutions/security/": "Site Security with Edge AI Cameras",
    "/lab/what-a-truck-will-tell-you/": "What a Truck Will Tell You: Fleet Vehicle Data",
    "/lab/what-is-air-gapped-ai/": "What Is Air Gapped AI? Models That Never Touch a Public Network",
}
# One sentence under the H1 of each locked term's owning page that answers the term in its own words (routine/locked.json).
ANSWERS = {
    "/hardware/": "Sovereign AI hardware is a device that runs its vision and language models on the unit, with open weights you host and keys you hold.",
    "/products/": "Edge AI devices run vision and language models on the unit itself, so decisions are made where the data is captured.",
    "/solutions/airgap/": "Air gapped AI runs open weight vision and language models on devices and servers that never touch a public network.",
    "/products/cameras/": "An edge AI camera runs its vision model on the unit and sends only events and short clips, so the video stays on your site.",
    "/solutions/sovereignty/": "Sovereign edge AI keeps the models, the devices and the keys inside your perimeter: open weights, self hosted, owned outright.",
}
MONTHS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def iso_date(d):
    day, mon, year = d.split()
    return f"{int(year):04d}-{MONTHS[mon]:02d}-{int(day):02d}"


def ld_org():
    """Organization: who we are, where, and whose subsidiary. Founders carry their own profiles; no sameAs to another company."""
    return {
        "@context": "https://schema.org", "@type": "Organization", "@id": ORG_ID,
        "name": "Arab American Instruments", "alternateName": "AAI", "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/img/mark.svg", "image": SITE_URL + "/assets/video/home-montage.jpg",
        "description": TAGLINE,
        "address": [
            {"@type": "PostalAddress", "addressLocality": "Riyadh", "addressCountry": "SA"},
            {"@type": "PostalAddress", "addressLocality": "Dallas", "addressRegion": "TX", "addressCountry": "US"},
        ],
        "parentOrganization": {"@type": "Organization", "name": "CodeNinja", "url": "https://codeatoms.ai/"},
        "founder": [{"@type": "Person", "name": L["name"], "jobTitle": L["title"], "sameAs": L["link"]} for L in LEADERS],
    }


def ld_crumbs(path, title):
    parts = [x for x in path.strip("/").split("/") if x]
    items, acc = [("Home", "/")], "/"
    for i, seg in enumerate(parts):
        acc += seg + "/"
        items.append((title if i == len(parts) - 1 else CRUMBS.get(acc, seg.replace("-", " ").title()), acc))
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + p} for i, (n, p) in enumerate(items)]}


def ld_tags(path, title, ld):
    blocks = list(ld or []) + ([ld_crumbs(path, title)] if path != "/" else [])
    return "".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False).replace("</", "<\\/") + "</script>\n" for b in blocks)


class _MD(HTMLParser):
    """Minimal HTML to Markdown for the page's <main>: headings, paragraphs, lists, links. Media and scripts dropped."""
    BLOCK = {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "figcaption", "tr", "br", "span"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.href, self.link = [], 0, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "video", "svg", "select", "noscript"):
            self.skip += 1
        elif tag in ("h1", "h2", "h3", "h4"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag in self.BLOCK:
            self.out.append("\n\n" if tag != "span" else " ")
        elif tag == "a" and a.get("href", "").startswith(("/", "http", "mailto:")):
            h = a["href"]
            if BASE and h.startswith(BASE):
                h = h[len(BASE):]
            self.href = SITE_URL + h if h.startswith("/") else h
            self.link = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "video", "svg", "select", "noscript"):
            self.skip = max(0, self.skip - 1)
        elif tag == "a" and self.href is not None:
            t = " ".join("".join(self.link).split())
            self.out.append(f"[{t}]({self.href})" if t else "")
            self.href = None
        elif tag in self.BLOCK and tag != "span":
            self.out.append("\n")

    def handle_data(self, d):
        if self.skip:
            return
        (self.link if self.href is not None else self.out).append(d)

    def text(self):
        lines = [" ".join(l.split()) for l in "".join(self.out).split("\n")]
        md, blank = [], False
        for l in lines:
            if not l or l in ("-", "#", "##", "###"):
                if md and not blank:
                    md.append("")
                blank = True
                continue
            md.append(l)
            blank = False
        return "\n".join(md).strip() + "\n"


def to_md(path, full, desc, body):
    m = _MD()
    m.feed(body)
    return f"# {full}\n\n> {desc}\n\nSource: {SITE_URL}{path}\n\n" + m.text()


MD = []  # (path, full title, desc, markdown) for llms.txt, llms-full.txt and index.md copies


def page(path, title, desc, body, active="", ld=None):
    t = SEO_TITLES.get(path, title)
    full = t if t == "Arab American Instruments" or "Arab American Instruments" in t else f"{t} | Arab American Instruments"
    canon = SITE_URL + path
    doc = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}/assets/video/home-montage.jpg"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#010101">
{f'<meta name="msvalidate.01" content="{BING_VERIFY}">' + chr(10) if path == "/" else ""}{ld_tags(path, title, ld)}<link rel="icon" href="{u("/assets/img/mark.svg")}" type="image/svg+xml">
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
    md = to_md(path, full, desc, body)
    with open(os.path.join(os.path.dirname(dest), "index.md"), "w") as fh:
        fh.write(md)
    MD.append((path, full, desc, md))
    PAGES.append(path)


def redirect(path, to):
    dest = os.path.join(OUT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        fh.write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><meta http-equiv="refresh" content="0;url={u(to)}"><link rel="canonical" href="{SITE_URL}{to}"><meta name="robots" content="noindex"></head><body><p>This page has moved to <a href="{u(to)}">{to}</a>.</p></body></html>')


PAGES = []

# ---------------------------------------------------------------- blocks


def label(text):
    return f'<p class="label"><span class="sq"></span>{e(text)}</p>'


def video_tag(slug, hero=False):
    v = f"/assets/video/{slug}"
    if hero:
        sm = f'<source src="{u(v + "-sm.mp4")}" type="video/mp4" media="(max-width:700px)">' if os.path.exists(os.path.join(ROOT, "assets", "video", slug + "-sm.mp4")) else ""
        return f'<video autoplay muted loop playsinline preload="auto" poster="{u(v + ".jpg")}" aria-hidden="true">{sm}<source src="{u(v + ".mp4")}" type="video/mp4"></video>'
    return f'<video muted loop playsinline preload="none" poster="{u(v + ".jpg")}" data-src="{u(v + ".mp4")}" aria-hidden="true"></video>'


def banner(slug, inner, cls="", hero=False):
    return f'<section class="banner {cls}"><img class="poster" src="{u("/assets/video/" + slug + ".jpg")}" alt="" aria-hidden="true">{video_tag(slug, hero)}<div class="scrim"></div><div class="inner">{inner}</div></section>'


def split(kicker, title, text, media, links="", side="right", cls="", h="h2"):
    ln = f'<div class="plinks">{links}</div>' if links else ""
    txt = f'<div class="col text">{label(kicker) if kicker else ""}<{h}>{title}</{h}><p class="lede">{text}</p>{ln}</div>'
    med = f'<div class="col media">{media}</div>'
    order = txt + med if side == "right" else med + txt
    return f'<section class="split {side} {cls}"><div class="wrap grid2">{order}</div></section>'


def panel_video(slug, caption=""):
    cap = f'<figcaption>{e(caption)}</figcaption>' if caption else ""
    return f'<figure class="panel"><img src="{u("/assets/video/" + slug + ".jpg")}" alt="" loading="lazy">{video_tag(slug)}{cap}</figure>'


def panel_img(src, caption="", alt=""):
    cap = f'<figcaption>{e(caption)}</figcaption>' if caption else ""
    return f'<figure class="panel"><img src="{u(src)}" alt="{e(alt or caption)}" loading="lazy">{cap}</figure>'


def page_head(kicker, title, text, slug=None, actions=""):
    media = f'<div class="wrap">{panel_video(slug)}</div>' if slug else ""
    return f'<section class="phead"><div class="wrap">{label(kicker)}<h1>{title}</h1><p class="lede">{text}</p>{actions}</div>{media}</section>'


def film_head(slug, kicker, title, tagline, text, actions="", path=""):
    """Anduril style page opener: name and tagline over footage."""
    ans = f'<p class="lede answer">{e(ANSWERS[path])}</p>' if path in ANSWERS else ""
    return banner(slug, f'{label(kicker)}<h1>{title}</h1><p class="tagline">{e(tagline)}</p>{ans}<p class="lede">{text}</p>{actions}', "phero")


def pill(href, text, primary=False):
    return f'<a class="btn{"" if primary else " ghost"}" href="{href}">{e(text)}</a>'


def dev_url(p):
    return u("/hardware/" + p["slug"] + "/")


def product_card(p):
    img = p["images"][0][0] if p["images"] else None
    if img:
        media = f'<img src="{u("/assets/img/stock/" + img)}" alt="{e(p["images"][0][1])}" loading="lazy">'
    else:
        media = f'<img src="{u("/assets/video/" + p["film"] + ".jpg")}" alt="" loading="lazy">{video_tag(p["film"])}'
    cat = CBY[CAT_OF[p["slug"]]]["name"] if p["slug"] in CAT_OF else ""
    return f'''<a class="card prod" href="{dev_url(p)}">
<div class="cm">{media}</div>
<div class="cb"><div class="meta"><span class="mono">{e(cat)}</span></div>
<h3>{e(p["name"])}</h3><p class="kind">{e(TAGLINES.get(p["slug"], p["kind"]))}</p><p>{e(p["short"])}</p>
<span class="more">Deployment details <i>&rarr;</i></span></div></a>'''


def cat_card(c):
    n = len(c["devices"])
    count = f'{n} device{"s" if n != 1 else ""}' if n else "Self hosted software"
    return f'<a class="card cat" href="{u("/products/" + c["slug"] + "/")}"><div class="cm"><img src="{u("/assets/video/" + c["film"] + ".jpg")}" alt="" loading="lazy">{video_tag(c["film"])}</div><div class="cb"><span class="mono">{count}</span><h3>{e(c["name"])}</h3><p>{e(c["tag"])}</p><span class="more">Explore <i>&rarr;</i></span></div></a>'


def sol_card(s):
    return f'<a class="card sol" href="{u("/solutions/" + s["slug"] + "/")}"><div class="cm"><img src="{u("/assets/video/" + s["film"] + ".jpg")}" alt="" loading="lazy">{video_tag(s["film"])}</div><div class="cb"><h3>{e(s["name"])}</h3><p>{e(s["tag"])}</p><span class="more">See the solution <i>&rarr;</i></span></div></a>'


def ind_tile(n, f):
    return f'<a class="itile" href="{u("/industries/")}#{slugify(n)}"><div class="cm"><img src="{u("/assets/video/" + f + ".jpg")}" alt="" loading="lazy">{video_tag(f)}</div><h3>{e(n)}</h3></a>'


OWN = [
    ("Design files", "Schematics, board layout and mechanical files. Yours to keep."),
    ("Bill of materials", "Every part with its maker and where it comes from."),
    ("Firmware and keys", "Source code and the signing keys, held by you."),
    ("Your choice of fab", "Build the next thousand wherever you trust."),
]


def own_strip():
    items = "".join(f'<div><span class="mono n">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(OWN))
    return f'<section class="own"><div class="wrap">{label("Designed by us. Owned by you.")}<div class="own4">{items}</div></div></section>'


def pillars():
    tiles = ""
    for i, (k, title, text, film, href) in enumerate(PILLARS):
        tiles += f'<a class="pillar" href="{u(href)}"><img src="{u("/assets/video/" + film + ".jpg")}" alt="" loading="{"eager" if i < 2 else "lazy"}">{video_tag(film)}<div class="pt"><span class="mono">0{i + 1}</span><h3>{e(title)}</h3><p>{e(text)}</p></div></a>'
    return f'<section class="pillars" id="pillars">{tiles}</section>'


def mosaic():
    order = [("fleet-vision-unit", "wide"), ("field-band", "tall"), ("vehicle-interface-module", ""), ("solar-relay", ""), ("site-camera", ""), ("patrol-gateway", ""), ("guide-hub", "")]
    tiles = ""
    for slug, cls in order:
        p = PBY[slug]
        if p["images"]:
            media = f'<img src="{u("/assets/img/stock/" + p["images"][0][0])}" alt="" loading="lazy">'
        else:
            media = f'<img src="{u("/assets/video/" + p["film"] + ".jpg")}" alt="" loading="lazy">{video_tag(p["film"])}'
        if slug in ("fleet-vision-unit", "field-band"):
            media = f'<img src="{u("/assets/video/" + p["film"] + ".jpg")}" alt="" loading="lazy">{video_tag(p["film"])}'
        tiles += f'<a class="tile {cls}" href="{dev_url(p)}">{media}<div class="tt"><span class="cat">{e(CBY[CAT_OF[slug]]["name"])}</span><span class="name">{e(p["name"])}</span><span class="tag">{e(TAGLINES[slug])}</span></div></a>'
    cmd = f'<a class="tile wide" href="{u("/products/command/")}"><img src="{u("/assets/video/control-room.jpg")}" alt="" loading="lazy">{video_tag("control-room")}<div class="tt"><span class="cat">Platform</span><span class="name">Command</span><span class="tag">The whole operation, inside your perimeter.</span></div></a>'
    return f'<section class="sec" style="border-top:0;padding-bottom:0"><div class="wrap"><div class="head">{label("Hardware")}<h2>Every device built inside your perimeter. Every one of them yours.</h2><a class="btn ghost" href="{u("/hardware/")}">All hardware</a></div></div></section><section class="mosaic">{tiles}{cmd}</section>'


def platform_block(full=False):
    stack = "".join(f'<div><span class="mono">{n}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for n, a, b in PLATFORM)
    models = "".join(f'<div><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in MODELS)
    head = f'<div class="head">{label("AI at the edge")}<h2>Hardware that runs the models where the work is.</h2>{"" if full else f"<a class=\'btn ghost\' href=\'{u("/platform/")}\'>The platform</a>"}<p class="lede">Vision models on the unit. Language models on your servers. One AI platform, built by our parent CodeNinja, designs the system, holds the object model, runs the models and keeps the memory, all inside your perimeter. The hardware is designed around what runs on it.</p></div>'
    return f'<section class="platform"><div class="wrap">{head}<div class="stack4">{stack}</div><div class="models">{models}</div></div></section>'


TERM_LINKS = [("Sovereign AI hardware", "/hardware/"), ("Edge AI devices", "/products/"), ("Air gapped AI", "/solutions/airgap/"), ("Edge AI camera", "/products/cameras/"), ("Sovereign edge AI", "/solutions/sovereignty/")]


def term_links():
    """Internal links in the locked terms' own words (routine/locked.json), below the first screen of home and platform."""
    return '<section class="jump"><div class="wrap"><span class="mono">Explore</span><div class="jumps">' + "".join(f'<a href="{u(h)}">{e(t)} <i>&rarr;</i></a>' for t, h in TERM_LINKS) + "</div></div></section>"


def cta(title="Tell us what you need to sense, send or control.", film_slug="print-timelapse"):
    return banner(film_slug, f'{label("Deployments")}<h2>{e(title)}</h2><p class="lede">No catalogue prices. We start from your site, your vehicles and your rules, and scope the deployment.</p><div class="actions">{pill(u("/build/"), "Request a deployment", True)}{pill(u("/hardware/"), "See all hardware")}</div>', "cta")


def slugify(s):
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-").replace("--", "-")


def note_card(n):
    return f'<a class="card note" href="{u("/lab/" + n["slug"] + "/")}"><div class="cm"><img src="{u("/assets/video/" + n["film"] + ".jpg")}" alt="" loading="lazy"></div><div class="cb"><span class="mono">{e(n["date"])}</span><h3>{e(n["title"])}</h3><p>{e(n["sub"])}</p></div></a>'


# ---------------------------------------------------------------- pages


def home():
    hero = banner(
        "home-montage",
        f'<h1>{e(TAGLINE)}</h1><p class="lede">Hardware that runs vision and language models on the device, on a stack the customer owns outright. Commercial operations and national ones, from the Gulf, Pakistan and the United States.</p><div class="actions">{pill(u("/build/"), "Request a deployment", True)}{pill(u("/hardware/"), "All hardware")}</div>',
        "hero",
        hero=True,
    )
    why = split(
        "Why we exist",
        "The biggest threats now sit in the hardware.",
        "For a decade the fight over control was a software fight. It has moved down the stack. A camera on a truck, a band on a wrist, a relay on a pole: each carries chips, radios, firmware and now models that someone else chose, from a supply chain nobody in the room can see. We think any organisation that runs critical work should own its hardware the way it already owns its data. So we design the devices, run the models on them, and hand each customer the design files, the parts list and the keys.",
        panel_video("engineer-scope", "Every device is designed, tested and documented so the customer can build it again without us."),
        pill(u("/supply-chain/"), "How ownership works"),
        side="right",
    )
    sols = "".join(sol_card(s) for s in SOLUTIONS[:5])
    solsec = f'<section class="cards"><div class="wrap"><div class="head">{label("Solutions")}<h2>Sovereignty first. Then everything an operator is measured on.</h2><a class="btn ghost" href="{u("/solutions/")}">All solutions</a></div><div class="grid5">{sols}</div></div></section>'
    inds = "".join(ind_tile(n, f) for n, f, _, _ in INDUSTRIES)
    ind = f'<section class="cards"><div class="wrap"><div class="head">{label("Where it runs")}<h2>Commercial operations and national ones. The same stack.</h2><a class="btn ghost" href="{u("/industries/")}">All industries</a></div><div class="grid4">{inds}</div></div></section>'
    notes = "".join(note_card(n) for n in NOTES)
    lab = f'<section class="cards"><div class="wrap"><div class="head">{label("Design Lab")}<h2>We publish what we learn.</h2><a class="btn ghost" href="{u("/lab/")}">All notes</a></div><div class="grid3">{notes}</div></div></section>'
    hq = f'<section class="hq"><div class="wrap">{label("Headquarters")}<div class="grid2 even">{panel_video("riyadh-day", "Riyadh, Saudi Arabia. Design, customer engineering and field trials for the Gulf.")}{panel_video("dallas-sunset", "Dallas, Texas. Design, partners and supply for the United States.")}</div></div></section>'
    body = hero + pillars() + mosaic() + platform_block() + term_links() + why + own_strip() + solsec + ind + lab + hq + cta()
    page("/", "Arab American Instruments", "Arab American Instruments designs low power edge devices that run vision and language models on the device, for sovereign and air gapped operations. Riyadh and Dallas. You own the design and the supply chain.", body, "", [ld_org(), {"@context": "https://schema.org", "@type": "WebSite", "name": "Arab American Instruments", "url": SITE_URL + "/", "publisher": {"@id": ORG_ID}}])


def platform_page():
    head = film_head("control-room", "AI platform", "AI at the edge.", "Vision on the device. Language on your servers. One stack, inside your perimeter.", "Our hardware is different because of what runs on it. The parent company's AI platform designs the system, holds the object model, runs the models and keeps the memory, with no cloud in the loop.", f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}{pill(u("/hardware/"), "All hardware")}</div>')
    body = (
        head
        + platform_block(full=True)
        + term_links()
        + split("On the device", "Vision models at full frame rate, on the unit.", "Driver state, road events, people and vehicles in zones, plates, helmets and vests. The models run on the hardware we design, tuned to the camera and the climate it operates in. Only the event and a short clip leave the unit, and only to where you say.", panel_video("dashcam-desert"), side="right")
        + split("On your servers", "A language model that knows your fleet.", "Command hosts a language model next to the fleet's own data. Ask which drivers were drowsy this week, which relay has been running on battery, where the missing band last reported. The answer comes from your perimeter and never leaves it.", panel_video("engineer-scope"), side="left")
        + split("Open weights, your hosting", "Models you hold, on hardware you own.", "Every model we ship runs from weights you hold, on devices and servers you own, signed with keys you keep. Updates arrive on your schedule, by your approval, or not at all.", panel_video("chip-macro"), side="right")
        + own_strip()
        + cta("Tell us what the devices should sense, report and decide.")
    )
    page("/platform/", "AI platform", "The AI platform behind Arab American Instruments hardware: vision models on the device, language models on your servers, built on CodeNinja's stack.", body, "/platform/")


def products():
    head = film_head("oasis-road", "Products", "One stack, inside your perimeter.", "Cameras, telematics, wearables, air gapped links and the platform they report to.", "Every device is built inside your perimeter and handed over whole. The models run on the hardware, the data stays on your site, and the design stays with you.", f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}{pill(u("/hardware/"), "See all hardware")}</div>', path="/products/")
    jump = '<section class="jump"><div class="wrap"><span class="mono">Explore the products</span><div class="jumps">' + "".join(f'<a href="#{c["slug"]}">{e(c["name"])} <i>&darr;</i></a>' for c in CATEGORIES) + f'<a href="{u("/hardware/")}">All hardware <i>&rarr;</i></a><a href="{u("/platform/")}">AI platform <i>&rarr;</i></a></div></div></section>'
    secs = ""
    for i, c in enumerate(CATEGORIES):
        devs = "".join(product_card(PBY[d]) for d in c["devices"])
        if c["slug"] == "command":
            devs = "".join(f'<div class="card flat"><div class="cb"><h3>{e(a)}</h3><p>{e(b)}</p></div></div>' for a, b in c["features"])
        secs += f'<div id="{c["slug"]}">' + split(f"0{i + 1} · {c['name']}", e(c["title"]), e(c["body"]), panel_video(c["film"]), pill(u("/products/" + c["slug"] + "/"), "Learn more"), side="right" if i % 2 == 0 else "left", cls="line") + f'<section class="cards tight"><div class="wrap"><div class="grid3">{devs}</div></div></section></div>'
    page("/products/", "Products", "Arab American Instruments products: vision at the edge, vehicle telematics, people in the field, air gapped links, and the self hosted Command platform.", head + jump + secs + own_strip() + cta(), "/products/")


def category_page(c):
    head = film_head(c["film"], f"Products · {c['name']}", e(c["name"]), c["title"], e(c["body"]), f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}{pill(u("/hardware/"), "All hardware")}</div>', path=f"/products/{c['slug']}/")
    if c["devices"]:
        devs = "".join(product_card(PBY[d]) for d in c["devices"])
        devsec = f'<section class="cards"><div class="wrap"><div class="head">{label("Devices")}<h2>{e(c["name"])} hardware.</h2></div><div class="grid3">{devs}</div></div></section>'
    else:
        feats = "".join(f'<div class="card flat"><div class="cb"><h3>{e(a)}</h3><p>{e(b)}</p></div></div>' for a, b in c["features"])
        devsec = f'<section class="cards"><div class="wrap"><div class="head">{label("What Command does")}<h2>Everything the devices send, on one screen you host.</h2></div><div class="grid3">{feats}</div><p class="fine">Command is built around the devices\' own protocol and runs wherever you put it: a data centre, a site server, or a laptop in camp.</p></div></section>'
    sols = "".join(sol_card(SBY[s]) for s in c["outcomes"])
    solsec = f'<section class="cards"><div class="wrap"><div class="head">{label("Solutions")}<h2>What it is for.</h2></div><div class="grid3">{sols}</div></div></section>'
    others = "".join(cat_card(o) for o in CATEGORIES if o["slug"] != c["slug"])
    more = f'<section class="cards"><div class="wrap"><div class="head">{label("The rest of the stack")}<h2>Works with</h2></div><div class="grid4">{others}</div></div></section>'
    page(f"/products/{c['slug']}/", c["name"], c["tag"], head + devsec + solsec + own_strip() + more + cta(), "/products/")


def hardware():
    head = film_head("smt-line", "All hardware", "Every device in the stack.", "Built inside your perimeter. Owned outright.", "Nothing here has a list price. Each deployment is scoped to where it will live and built for the customer who will own it.", f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}</div>', path="/hardware/")
    rows = ""
    for c in CATEGORIES:
        for d in c["devices"]:
            if f'data-s="{d}"' in rows:
                continue
            p = PBY[d]
            spec = "; ".join(f"{a}: {b}" for a, b in p["specs"][:2])
            rows += f'<tr data-s="{d}"><td><a href="{dev_url(p)}"><b>{e(p["name"])}</b><br><span>{e(TAGLINES.get(d, p["kind"]))}</span></a></td><td data-l="Category">{e(c["name"])}</td><td class="specs" data-l="At a glance">{e(spec)}</td></tr>'
    table = f'<section class="hwtable"><div class="wrap"><div class="tw"><table class="data"><thead><tr><th>Device</th><th>Category</th><th>At a glance</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'
    cards = "".join(product_card(p) for p in PRODUCTS)
    grid = f'<section class="cards"><div class="wrap"><div class="grid3">{cards}</div></div></section>'
    page("/hardware/", "All hardware", "Every Arab American Instruments device at a glance.", head + table + grid + own_strip() + cta(), "/products/")


def product_page(p):
    c = CBY[CAT_OF[p["slug"]]]
    actions = f'<div class="actions">{pill(u("/build/") + "?platform=" + p["slug"], "Request this deployment", True)}{pill(u("/hardware/"), "All hardware")}</div>'
    head = film_head(p["film"], f"{c['name']} · {p['kind']}", e(p["name"]), TAGLINES.get(p["slug"], ""), e(p["short"]), actions)
    gal = ""
    if p["images"]:
        figs = "".join(f'<figure class="panel"><img src="{u("/assets/img/stock/" + f)}" alt="{e(cp)}" loading="lazy"><figcaption>{e(cp)}</figcaption></figure>' for f, cp in p["images"])
        gal = f'<section class="gallery"><div class="gal">{figs}</div></section>'
    secs = "".join(f'<div class="feat"><h3>{e(h)}</h3><ul>{"".join("<li>" + e(i) + "</li>" for i in items)}</ul></div>' for h, items in p["sections"])
    specs = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in p["specs"])
    pairs = "".join(product_card(PBY[s]) for s in p.get("pairs", []))
    sols = "".join(sol_card(s) for s in SOLUTIONS if p["slug"] in s["devices"])
    body = (
        head
        + gal
        + f'<section class="detail"><div class="wrap"><div class="cols"><div>{label("What it does")}<div class="feats">{secs}</div></div><aside>{label("At a glance")}<table class="spec">{specs}</table><p class="fine">Every unit is adapted to the customer, so the delivered configuration may differ.</p></aside></div></div></section>'
        + (f'<section class="cards"><div class="wrap"><div class="head">{label("Solutions")}<h2>What it is for.</h2></div><div class="grid3">{sols}</div></div></section>' if sols else "")
        + own_strip()
        + (f'<section class="cards"><div class="wrap"><div class="head">{label("Works with")}<h2>Part of one stack.</h2></div><div class="grid3">{pairs}</div></div></section>' if pairs else "")
        + cta(f"Deploy {p['name']} inside your perimeter.")
    )
    url = f"{SITE_URL}/hardware/{p['slug']}/"
    img = SITE_URL + ("/assets/img/stock/" + p["images"][0][0] if p["images"] else f"/assets/video/{p['film']}.jpg")
    ld = [{"@context": "https://schema.org", "@type": "Product", "@id": url + "#product", "name": p["name"], "description": p["short"],
           "category": c["name"], "image": img, "url": url,
           "brand": {"@type": "Brand", "name": "Arab American Instruments"}, "manufacturer": {"@id": ORG_ID}}]
    hd = f"{p['name']}: {p['short']}"
    if len(hd) > 160:
        hd = f"{p['name']}: {p['short'].split('. ')[0].rstrip('.')}."
    if len(hd) > 160:
        hd = hd[:hd.rfind(",", 0, 158)] + "."
    SEO_TITLES.setdefault(f"/hardware/{p['slug']}/", f"{p['name']}: {p['kind']}")
    page(f"/hardware/{p['slug']}/", p["name"], hd, body, "/products/", ld)


def solutions():
    head = film_head("truck-desert", "Solutions", "Sovereignty first.", "Then safety, security, records, cost and coverage, on hardware you own.", "The outcomes operators are measured on, delivered by devices that run their models on the unit and report to a platform you host.", f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}</div>')
    cards = "".join(sol_card(s) for s in SOLUTIONS)
    grid = f'<section class="cards"><div class="wrap"><div class="grid3">{cards}</div></div></section>'
    inds = "".join(ind_tile(n, f) for n, f, _, _ in INDUSTRIES)
    ind = f'<section class="cards"><div class="wrap"><div class="head">{label("Industries")}<h2>Where it runs.</h2><a class="btn ghost" href="{u("/industries/")}">All industries</a></div><div class="grid4">{inds}</div></div></section>'
    page("/solutions/", "Solutions", "Arab American Instruments solutions: sovereignty, air gapped operations, safety, security, compliance, efficiency and coverage.", head + grid + ind + own_strip() + cta(), "/solutions/")


def solution_page(s):
    head = film_head(s["film"], f"Solutions · {s['name']}", e(s["name"]), s["title"], e(s["body"]), f'<div class="actions">{pill(u("/build/"), "Request a deployment", True)}</div>', path=f"/solutions/{s['slug']}/")
    pts = "".join(f"<li>{e(x)}</li>" for x in s["points"])
    devs = "".join(product_card(PBY[d]) for d in s["devices"])
    ibys = {n: f for n, f, _, _ in INDUSTRIES}
    inds = "".join(ind_tile(n, ibys[n]) for n in s["industries"])
    body = (
        head
        + f'<section class="detail"><div class="wrap"><div class="cols"><div>{label("What you get")}<ul class="points">{pts}</ul></div><aside>{label("How it stays yours")}<p>The models run on the device. Events and clips go only where you send them. Command runs on your servers. The design files, the bill of materials and the keys are handed over at the end of the build.</p>{pill(u("/supply-chain/"), "How ownership works")}{pill(u("/lab/what-is-air-gapped-ai/"), "What is air gapped AI?") if s["slug"] == "airgap" else ""}</aside></div></div></section>'
        + f'<section class="cards"><div class="wrap"><div class="head">{label("Hardware")}<h2>The devices behind it.</h2><a class="btn ghost" href="{u("/hardware/")}">All hardware</a></div><div class="grid3">{devs}</div></div></section>'
        + f'<section class="cards"><div class="wrap"><div class="head">{label("Industries")}<h2>Where it runs.</h2></div><div class="grid3">{inds}</div></div></section>'
        + cta()
    )
    page(f"/solutions/{s['slug']}/", s["name"], s["tag"], body, "/solutions/")


def industries():
    head = film_head("desert-drone", "Industries", "Where nothing may leave the perimeter.", "Commercial operations and national ones, on the same stack.", "We build for work that runs far from the network or must stay off it: fleets, crowds, energy, water, grids, ports and closed sites across the Gulf, Pakistan and the United States.")
    rows = ""
    for i, (n, f, d, ps) in enumerate(INDUSTRIES):
        links = "".join(f'<a href="{dev_url(PBY[s])}">{e(PBY[s]["name"])} <i>&rarr;</i></a>' for s in ps) or f'<a href="{u("/build/")}">Request a deployment <i>&rarr;</i></a>'
        rows += f'<div id="{slugify(n)}">' + split(f"0{i + 1}", e(n), e(d), panel_video(f), links, side="right" if i % 2 == 0 else "left", cls="line") + "</div>"
    page("/industries/", "Industries", "Edge AI devices by industry: fleets, crowd safety, energy, utilities, agriculture, government and critical sites, remote sites, telecom and ports.", head + rows + cta(), "/solutions/")


def lab():
    head = film_head("smt-line", "Design Lab", "We publish what we learn.", "Engineering notes from Arab American Instruments.", "The decisions behind our devices, the numbers behind our links, and the tradeoffs we weighed. Our customers own their designs; the method we share with everyone.")
    notes = "".join(note_card(n) for n in NOTES)
    page("/lab/", "Design Lab", "Notes from the Arab American Instruments Design Lab on edge hardware, mesh links, vehicle data and air gapped AI.", head + f'<section class="cards"><div class="wrap"><div class="grid3">{notes}</div></div></section>' + cta(), "/lab/")
    for n in NOTES:
        out = ""
        for kind, val in n["body"]:
            if kind == "p":
                out += f"<p>{e(val)}</p>"
            elif kind == "h":
                out += f"<h2>{e(val)}</h2>"
            elif kind == "links":
                out += '<p class="plinks">' + "".join(f'<a href="{u(h)}">{e(t)} <i>&rarr;</i></a>' for t, h in val) + "</p>"
            elif kind == "table":
                hd = "".join(f"<th>{e(c)}</th>" for c in val[0])
                rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in val[1:])
                out += f'<div class="tw"><table class="data"><thead><tr>{hd}</tr></thead><tbody>{rows}</tbody></table></div>'
        head = film_head(n["film"], f"Design Lab · {n['date']}", e(n["title"]), "", e(n["sub"]))
        art = f'<article class="article paper"><div class="wrap narrow">{out}<p class="byline mono">Design Lab, Arab American Instruments</p></div></article>'
        url = f"{SITE_URL}/lab/{n['slug']}/"
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": n["title"], "description": n["sub"],
               "datePublished": iso_date(n["date"]), "dateModified": iso_date(n["date"]), "image": f"{SITE_URL}/assets/video/{n['film']}.jpg",
               "mainEntityOfPage": url, "author": {"@type": "Organization", "@id": ORG_ID, "name": "Arab American Instruments", "url": SITE_URL + "/"},
               "publisher": {"@id": ORG_ID}}]
        page(f"/lab/{n['slug']}/", n["title"], n["sub"], head + art + cta(), "/lab/", ld)


def supply():
    head = film_head("terminal-timelapse", "Supply chain", "Own the stack, down to the part.", "Design, parts, firmware, keys. Handed over whole.", "Most edge devices arrive as sealed boxes from a supply chain you cannot see. Ours arrive with their design, their parts list and their keys.")
    steps = [
        ("Requirement", "What must be sensed, sent or controlled, where, for how long, and what may never leave the site."),
        ("Reference design", "We start from the closest platform and show you the tradeoffs: battery, range, size, cost."),
        ("Your board", "We adapt the schematic, layout and shell to your vehicles, your climate and your rules."),
        ("Pilot run", "A small batch built and tested with you, with every part traced to its maker."),
        ("Field trial", "Units in the field, measured against the targets we set together."),
        ("Handover", "Design files, bill of materials, firmware source and keys. Build the rest wherever you trust."),
    ]
    st = "".join(f'<li><span class="mono n">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></li>' for i, (a, b) in enumerate(steps))
    body = (
        head
        + split("How we work", "We own the design. You own the supply chain.", "We are a technology company that owns its hardware designs. We keep and improve our reference designs, publish what we learn in the Design Lab, and for each customer we build a purpose built device on top of them. When the work is done, the customer holds everything needed to build it again without us.", panel_video("engineer-scope"), side="right")
        + f'<section class="steps"><div class="wrap">{label("Six steps")}<ol>{st}</ol></div></section>'
        + own_strip()
        + split("Built where you trust", "Your fab, your line, your country.", "After the pilot, the next thousand units can be built by any qualified manufacturer you choose, in the Gulf, in Pakistan, in the United States or anywhere else you trust.", panel_video("robot-lab"), side="left")
        + split("Traceable by default", "Every part with its maker and its origin.", "Each bill of materials we hand over names the maker of every part and where it was made, so your security team can audit the device the way it audits code.", panel_video("chip-macro"), side="right")
        + cta()
    )
    page("/supply-chain/", "Supply chain", "How Arab American Instruments hands customers their design files, parts list, firmware and keys so they own their hardware supply chain.", body, "/supply-chain/")


LEADERS = [
    {"slug": "muhammad-umar-bilal", "name": "Muhammad Umar", "title": "Founder",
     "bio": "Muhammad Umar is a founder of Arab American Instruments and one of the co-founders of CodeNinja, the parent company of Arab American Instruments. He works on Hyper Ontologies, the memory and interpretability layer underneath CodeNinja's enterprise AI deployments, and is the author of the Own the Loop research series.",
     "link": "https://www.linkedin.com/in/muhammadumargiki/"},
    {"slug": "mukhtar-ahmad-baig", "name": "Mukhtar Ahmad Baig", "title": "Co-Founder and Chief Executive Officer",
     "bio": "Mr. Baig is the Chief Executive Officer of Arab American Instruments and one of the co-founders of CodeNinja, its parent company, where he holds the same office. He leads the company's direction, its relationships with governments and enterprises in the Gulf and the United States, and the growth of the group's hardware business.",
     "link": "https://www.linkedin.com/in/mukhtarahmadbaig/"},
    {"slug": "adil-khalil", "name": "Adil Khalil", "title": "Co-Founder and Chief Technology Officer",
     "bio": "Mr. Khalil is the Chief Technology Officer of Arab American Instruments and one of the co-founders of CodeNinja, its parent company, where he holds the same office. He leads the engineering behind the devices, from schematic and firmware to the models that run on them, and their deployment inside the customer's perimeter.",
     "link": "https://www.linkedin.com/in/adilkhalil/"},
    {"slug": "ibrar-hussain", "name": "Ibrar Hussain", "title": "Co-Founder and Chief Product Officer",
     "bio": "Mr. Hussain is the Chief Product Officer of Arab American Instruments and one of the co-founders of CodeNinja, its parent company, where he holds the same office. He leads the product line and the roadmap of the devices, from a single pilot to a national fleet, and the experience of the teams who operate them.",
     "link": "https://pk.linkedin.com/in/helloibrar"},
]

BOARD = [
    {"slug": "ahsan-jamil", "name": "Ahsan Jamil", "title": "Board Member. Managing General Partner, sAi Venture Capital",
     "bio": "Mr. Jamil is the Managing General Partner of sAi Venture Capital, a Lahore based technology venture investor backing frontier technology companies that serve large global enterprises. He joined the CodeNinja board in December 2023, when sAi led the company's investment round.",
     "link": "https://saiventurecap.com/our-team/"},
]

ABOUT_FAQ = [
    ("What is Arab American Instruments?", "Arab American Instruments is a technology company headquartered in Riyadh and Dallas. It builds low power edge devices for sensing, satellite links and real time control that run vision and language models inside the customer's perimeter."),
    ("Who owns Arab American Instruments?", "Arab American Instruments is a fully owned subsidiary of CodeNinja. The AI platform on its devices is CodeNinja's: Praxis, Hyper Ontology, Hyper Pragma and Hyper Engram."),
    ("Where does Arab American Instruments work?", "From Riyadh and Dallas, with teams across the Gulf, Pakistan and the United States, for commercial and national buyers."),
    ("What does Arab American Instruments offer?", "Edge AI devices for fleets, people and sites: the Fleet Vision Unit, Vehicle Interface Module, Field Band, Guide Hub, Patrol Gateway, Solar Relay, Charging Dock and Site Camera, deployed inside your perimeter and owned outright."),
]

MISSION = [
    "The most important assets of nation states, governments and enterprises, our national institutions, our energy grids, our border controls, our oil and gas facilities, all exist in the physical world. Every one of them is now watched, connected and controlled by hardware: cameras, gateways, radios and controllers, and the models that run on them.",
    "While we are passionate about instrumenting all this physical infrastructure, we cannot simply outsource the devices it runs on to one or two extremely centralised hardware vendors, with sealed firmware and supply chains nobody in the room can see. The only way to defend these institutions and this critical infrastructure is to own the hardware stack: the design, the parts, the firmware, the models and the keys.",
    "And that is the mission of Arab American Instruments.",
]


def about():
    head = film_head("alula", "About", "A technology company for sovereign hardware.", "Riyadh. Dallas. One stack.", e(TAGLINE))
    mission = '<section class="mission paper"><div class="wrap"><div class="mgrid">' + label("Our mission") + '<div>' + "".join(f'<p class="stmt">{e(x)}</p>' for x in MISSION) + '</div></div></div></section>'
    rows = ""
    for i, L in enumerate(LEADERS):
        fig = f'<figure><img src="{u("/assets/img/team/" + L["slug"] + ".jpg")}" alt="{e(L["name"])}" loading="lazy" width="900" height="750"></figure>'
        pan = f'<div class="lpanel"><h3>{e(L["name"])}</h3><p class="role">{e(L["title"])}</p><p class="bio">{e(L["bio"])}</p><a class="in" href="{L["link"]}" rel="noopener" target="_blank">LinkedIn</a></div>'
        rows += f'<div class="leader{" flip" if i % 2 else ""}">{fig}{pan}</div>'
    team = f'<section class="team"><div class="wrap"><div class="head">{label("Founding team")}</div>{rows}</div></section>'
    brows = ""
    for L in BOARD:
        fig = f'<figure><img src="{u("/assets/img/team/" + L["slug"] + ".jpg")}" alt="{e(L["name"])}" loading="lazy" width="900" height="750"></figure>'
        pan = f'<div class="lpanel"><h3>{e(L["name"])}</h3><p class="role">{e(L["title"])}</p><p class="bio">{e(L["bio"])}</p><a class="in" href="{L["link"]}" rel="noopener" target="_blank">sAi Venture Capital</a></div>'
        brows += f'<div class="leader">{fig}{pan}</div>'
    board = f'<section class="team"><div class="wrap"><div class="head">{label("Board")}<h2>Backed by sAi Venture Capital.</h2><p class="lede">sAi Venture Capital led CodeNinja\'s investment round in December 2023 and holds a seat on the board.</p></div>{brows}</div></section>'
    faq_html = "".join(f'<div class="qa"><h2>{e(q)}</h2><p class="lede">{e(a)}</p></div>' for q, a in ABOUT_FAQ)
    faq = f'<section class="faq"><div class="wrap">{label("In brief")}{faq_html}</div></section>'
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ABOUT_FAQ]}
    body = (
        head
        + faq
        + mission
        + split("What we do", "Purpose built hardware that runs AI, owned by the customer.", "We design edge devices for sensing, satellite and mesh links, and real time control, run vision and language models on them, and deploy them inside the perimeter so that the customer owns the design and the supply chain, not us and not anyone else. We keep reference designs, publish what we learn, and build for each customer from a single pilot to a national fleet.", panel_img("/assets/img/stock/technician-solder.jpg", "Schematic, layout, firmware, models and shell under one roof."), side="right")
        + team
        + board
        + f'<section class="hq"><div class="wrap">{label("Headquarters")}<div class="grid2 even">{panel_video("riyadh-day", "Riyadh, Saudi Arabia")}{panel_video("dallas-sunset", "Dallas, Texas, United States")}</div></div></section>'
        + split("Ownership", "A fully owned subsidiary of CodeNinja.", "Arab American Instruments brings hardware into the CodeNinja group, alongside its work on sovereign AI systems for governments and enterprises. The AI platform that runs on our devices is CodeNinja\'s.", panel_video("engineer-scope"), side="right")
        + cta()
    )
    page("/about/", "About", "Arab American Instruments is a technology company in Riyadh and Dallas that builds sovereign edge AI devices. A fully owned subsidiary of CodeNinja.", body, "/about/", [ld_org(), ld_faq])


def build_page():
    opts = "".join(f'<option value="{e(p["name"])}">{e(p["name"])} ({e(p["kind"])})</option>' for p in PRODUCTS)
    qty = [("Pilot run, 10 to 100 units (recommended first step)", True), ("Prototype, under 10 units", False), ("Production, 100 to 1,000 units", False), ("Fleet or national scale, over 1,000 units", False)]
    qopts = "".join(f'<label class="opt"><input type="radio" name="Quantity" value="{e(q)}"{" checked" if c else ""}><span>{e(q)}</span></label>' for q, c in qty)
    env = [("Air gapped: nothing may leave the site (recommended default)", True), ("Private network or private cloud", False), ("Public cellular or satellite is acceptable", False), ("Not known yet", False)]
    eopts = "".join(f'<label class="opt"><input type="radio" name="Connectivity" value="{e(q)}"{" checked" if c else ""}><span>{e(q)}</span></label>' for q, c in env)
    form = f'''<section class="formwrap paper"><div class="wrap grid2">
<div class="col text">{label("Request a deployment")}<h2>Describe the requirement. We scope the deployment.</h2>
<p class="lede">No prices on this site, because every deployment is scoped to the site it will run on. Send the outline and an engineer replies with questions, a deployment outline and a plan for a pilot.</p>
{panel_video("print-timelapse")}</div>
<div class="col"><form id="buildform">
<div class="two"><label>Name<input name="Name" required autocomplete="name"></label><label>Organisation<input name="Organisation" required autocomplete="organization"></label></div>
<div class="two"><label>Work email<input type="email" name="Email" required autocomplete="email"></label><label>Country<input name="Country" placeholder="Saudi Arabia, United States, ..."></label></div>
<label>Closest device<select name="Platform"><option value="Not yet decided">Not yet decided, recommend one</option>{opts}<option value="Command platform">Command platform</option><option value="Other controller">Other controller</option></select></label>
<label>What must it sense, send or control?<textarea name="Requirement" rows="4" required placeholder="For example: cab and road cameras for a heavy truck fleet, vehicle data from the fleet port, events over cellular."></textarea></label>
<fieldset><legend>Where will the data go?</legend>{eopts}</fieldset>
<fieldset><legend>How many units to start?</legend>{qopts}</fieldset>
<label>Timeline<input name="Timeline" placeholder="For example: pilot in Q1 2027"></label>
<button class="btn" type="submit">Send the request</button>
<p class="fine">This opens your email app with the request filled in, addressed to {CONTACT}. Nothing is stored on this site.</p>
<p class="sent" hidden>Your email app should now be open. If it did not open, write to {CONTACT}.</p>
</form></div></div></section>
<script>(function(){{var m=location.search.match(/platform=([a-z-]+)/);if(!m)return;var map={json.dumps({p["slug"]: p["name"] for p in PRODUCTS})};var s=document.querySelector('select[name=Platform]');if(map[m[1]])s.value=map[m[1]];}})();</script>'''
    head = page_head("Deployments", "Request a deployment.", "From a single pilot to a national fleet, built inside your perimeter. You keep the design, the parts list and the keys.")
    page("/build/", "Request a deployment", "Request a deployment of Arab American Instruments edge devices.", head + form, "")



INDEXNOW_KEY = "5e2f8c1a9b4d47e3a6c0d8f1b2e9a7c4"


def last_change():
    """Date of the last commit that touched build.py (the site's data), never today. None outside git."""
    try:
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "build.py"], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        return d or None
    except Exception:
        return None


def llms():
    """llms.txt (an index for AI readers) and llms-full.txt (every page as Markdown) at the root."""
    head = (f"# Arab American Instruments\n\n> {TAGLINE} A technology company headquartered in Riyadh and Dallas, "
            "working from the Gulf, Pakistan and the United States, and a fully owned subsidiary of CodeNinja. "
            "The devices run open weight vision and language models inside the customer's perimeter.\n\n")
    groups = [("Company", lambda p: p in ("/", "/about/", "/platform/", "/supply-chain/", "/build/")),
              ("Hardware", lambda p: p.startswith("/hardware/")),
              ("Products", lambda p: p.startswith("/products/")),
              ("Solutions", lambda p: p.startswith("/solutions/") or p.startswith("/industries/")),
              ("Design Lab", lambda p: p.startswith("/lab/"))]
    out, seen = [head], set()
    for name, f in groups:
        rows = [(p, t, d) for p, t, d, _ in MD if f(p) and p not in seen]
        if not rows:
            continue
        out.append(f"## {name}\n\n")
        for p, t, d in rows:
            seen.add(p)
            out.append(f"- [{t}]({SITE_URL}{p}index.md): {d}\n")
        out.append("\n")
    rest = [(p, t, d) for p, t, d, _ in MD if p not in seen]
    if rest:
        out.append("## Other\n\n" + "".join(f"- [{t}]({SITE_URL}{p}index.md): {d}\n" for p, t, d in rest))
    with open(os.path.join(OUT, "llms.txt"), "w") as fh:
        fh.write("".join(out))
    with open(os.path.join(OUT, "llms-full.txt"), "w") as fh:
        fh.write(head + "\n\n---\n\n".join(m for _, _, _, m in MD))


def extras():
    with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        lastmod = last_change()
        for p in PAGES:
            lm = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
            fh.write(f"<url><loc>{SITE_URL}{p}</loc>{lm}</url>\n")
        fh.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    with open(os.path.join(OUT, f"{INDEXNOW_KEY}.txt"), "w") as fh:
        fh.write(INDEXNOW_KEY)
    llms()
    with open(os.path.join(OUT, GOOGLE_VERIFY_FILE), "w") as fh:
        fh.write(f"google-site-verification: {GOOGLE_VERIFY_FILE}")
    with open(os.path.join(OUT, "BingSiteAuth.xml"), "w") as fh:
        fh.write(f'<?xml version="1.0"?>\n<users>\n\t<user>{BING_VERIFY}</user>\n</users>\n')
    with open(os.path.join(OUT, "CNAME"), "w") as fh:
        fh.write(DOMAIN + "\n")
    redirect("/platforms/", "/products/")
    OLD = {"drivesense": "fleet-vision-unit", "vim": "vehicle-interface-module", "vehicle-gateway": "patrol-gateway"}
    for p in PRODUCTS:
        redirect(f"/platforms/{p['slug']}/", f"/hardware/{p['slug']}/")
    for o, n in OLD.items():
        redirect(f"/platforms/{o}/", f"/hardware/{n}/")
        redirect(f"/hardware/{o}/", f"/hardware/{n}/")


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"), ignore=shutil.ignore_patterns("CREDITS.md"))
    home(); platform_page(); products(); hardware(); solutions()
    for c in CATEGORIES:
        category_page(c)
    for p in PRODUCTS:
        product_page(p)
    for s in SOLUTIONS:
        solution_page(s)
    industries(); lab(); supply(); about(); build_page(); extras()
    print(f"built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
