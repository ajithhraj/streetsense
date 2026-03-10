# src/crowdmap.py — Build live crowdsourced map from all reports

import folium
from folium.plugins import MarkerCluster, HeatMap
from src.database import get_all_reports
from src.hazard_taxonomy import HAZARDS

SEVERITY_COLORS = {
    "None":     "green",
    "Low":      "lightgreen",
    "Moderate": "orange",
    "High":     "red",
    "Critical": "darkred",
}

def build_crowdmap(center_lat: float = 12.9716, center_lon: float = 77.5946) -> folium.Map:
    reports = get_all_reports()
    geo_reports = [r for r in reports if r.get("lat") and r.get("lon")]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter"
    )

    # Heatmap layer
    if geo_reports:
        heat_data = [
            [r["lat"], r["lon"], r["severity_score"] / 10]
            for r in geo_reports
        ]
        HeatMap(heat_data, radius=25, blur=15, min_opacity=0.4).add_to(m)

    # Clustered markers
    cluster = MarkerCluster(name="Reports").add_to(m)

    for r in geo_reports:
        color = SEVERITY_COLORS.get(r.get("severity_label", "Low"), "orange")
        hazards = r.get("hazards", [])
        hazard_icons = " ".join([
            HAZARDS.get(h, {}).get("icon", "⚠️") for h in hazards[:3]
        ])

        popup_html = f"""
        <div style='font-family:sans-serif;min-width:220px;padding:4px'>
            <div style='font-weight:600;font-size:14px;margin-bottom:6px'>
                {hazard_icons} {r.get('primary_hazard','Unknown').replace('_',' ').title()}
            </div>
            <div style='color:#666;font-size:12px;margin-bottom:4px'>
                {r.get('location') or 'Unknown location'} · {r.get('created_at','')[:10]}
            </div>
            <div style='margin-bottom:6px'>
                <span style='background:{"#ff4444" if r["severity_score"]>=7.5 else "#ff8800" if r["severity_score"]>=5 else "#88cc00"};
                    color:white;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600'>
                    {r.get('severity_label','?')} · {r.get('severity_score',0):.1f}/10
                </span>
            </div>
            <div style='font-size:12px;color:#333;font-style:italic;line-height:1.5'>
                {(r.get('civic_report') or '')[:120]}...
            </div>
            <div style='margin-top:6px;font-size:11px;color:#999'>
                via {r.get('source','web')}
            </div>
        </div>
        """

        folium.Marker(
            [r["lat"], r["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{r.get('severity_label')} — {r.get('primary_hazard','?').replace('_',' ').title()}",
            icon=folium.Icon(color=color, icon="warning-sign", prefix="glyphicon")
        ).add_to(cluster)

    folium.LayerControl().add_to(m)
    return m, len(reports), len(geo_reports)
