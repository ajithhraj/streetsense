# src/hazard_taxonomy.py
# Custom hazard taxonomy built for Indian road conditions

HAZARDS = {
    "pothole": {
        "description": "Hole or depression in road surface",
        "severity_weight": 0.8,
        "color": "#ff4444",
        "icon": "⚠️"
    },
    "waterlogging": {
        "description": "Standing water or flooded road section",
        "severity_weight": 0.9,
        "color": "#4444ff",
        "icon": "🌊"
    },
    "broken_road": {
        "description": "Cracked, crumbling, or severely damaged road surface",
        "severity_weight": 0.7,
        "color": "#ff8800",
        "icon": "🛣️"
    },
    "missing_manhole": {
        "description": "Open or missing manhole cover",
        "severity_weight": 1.0,
        "color": "#ff0000",
        "icon": "🕳️"
    },
    "debris": {
        "description": "Rocks, garbage, or objects on the road",
        "severity_weight": 0.6,
        "color": "#888800",
        "icon": "🪨"
    },
    "broken_divider": {
        "description": "Damaged or missing road divider/median",
        "severity_weight": 0.5,
        "color": "#ff6600",
        "icon": "🚧"
    },
    "faded_markings": {
        "description": "Faded or missing road markings and zebra crossings",
        "severity_weight": 0.4,
        "color": "#aaaaaa",
        "icon": "〰️"
    },
    "broken_signage": {
        "description": "Damaged, missing, or obscured road signs",
        "severity_weight": 0.5,
        "color": "#aa00aa",
        "icon": "🚫"
    },
    "encroachment": {
        "description": "Illegal structures or vendors on road/footpath",
        "severity_weight": 0.4,
        "color": "#00aaaa",
        "icon": "🏪"
    },
    "speed_breaker": {
        "description": "Unmarked or poorly constructed speed breaker",
        "severity_weight": 0.5,
        "color": "#ffaa00",
        "icon": "〽️"
    },
    "no_hazard": {
        "description": "Road appears safe and well-maintained",
        "severity_weight": 0.0,
        "color": "#00cc44",
        "icon": "✅"
    }
}

SEVERITY_LEVELS = {
    (0.0, 0.0): ("None", "#00cc44"),
    (0.1, 3.0): ("Low", "#88cc00"),
    (3.1, 5.0): ("Moderate", "#ffaa00"),
    (5.1, 7.5): ("High", "#ff6600"),
    (7.6, 10.0): ("Critical", "#ff0000"),
}

def get_severity_label(score: float):
    for (low, high), (label, color) in SEVERITY_LEVELS.items():
        if low <= score <= high:
            return label, color
    return "Unknown", "#888888"
