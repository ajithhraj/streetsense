# src/database.py — SQLite storage for all reports

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/streetsense.db")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at  TEXT NOT NULL,
            location    TEXT,
            lat         REAL,
            lon         REAL,
            hazards     TEXT,
            primary_hazard TEXT,
            severity_score REAL,
            severity_label TEXT,
            road_condition TEXT,
            confidence  REAL,
            passable    INTEGER,
            civic_report TEXT,
            immediate_action TEXT,
            affected_area_percent INTEGER,
            source      TEXT DEFAULT 'web'
        )
    """)
    conn.commit()
    conn.close()

def save_report(result: dict, gps: dict | None, location: str = "", source: str = "web") -> int:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        INSERT INTO reports (
            created_at, location, lat, lon, hazards, primary_hazard,
            severity_score, severity_label, road_condition, confidence,
            passable, civic_report, immediate_action, affected_area_percent, source
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(),
        location,
        gps["lat"] if gps else None,
        gps["lon"] if gps else None,
        json.dumps(result.get("hazards_detected", [])),
        result.get("primary_hazard"),
        result.get("severity_score"),
        result.get("severity_label"),
        result.get("road_condition"),
        result.get("confidence"),
        1 if result.get("passable") else 0,
        result.get("civic_report"),
        result.get("immediate_action"),
        result.get("affected_area_percent"),
        source
    ))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return report_id

def get_all_reports() -> list[dict]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    conn.close()
    reports = []
    for row in rows:
        r = dict(row)
        r["hazards"] = json.loads(r["hazards"] or "[]")
        reports.append(r)
    return reports

def get_stats() -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    avg_severity = conn.execute("SELECT AVG(severity_score) FROM reports").fetchone()[0] or 0
    critical = conn.execute("SELECT COUNT(*) FROM reports WHERE severity_score >= 7.5").fetchone()[0]
    most_common = conn.execute("""
        SELECT primary_hazard, COUNT(*) as cnt FROM reports
        WHERE primary_hazard IS NOT NULL
        GROUP BY primary_hazard ORDER BY cnt DESC LIMIT 1
    """).fetchone()
    conn.close()
    return {
        "total": total,
        "avg_severity": round(avg_severity, 2),
        "critical": critical,
        "most_common_hazard": most_common[0] if most_common else "N/A"
    }
