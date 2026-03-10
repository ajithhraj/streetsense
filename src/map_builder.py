# src/map_builder.py
import folium

def build_map(lat: float, lon: float, result: dict) -> folium.Map:
    severity_color = {
        "None": "green", "Low": "lightgreen",
        "Moderate": "orange", "High": "red", "Critical": "darkred"
    }.get(result.get("severity_label", "Low"), "orange")

    m = folium.Map(location=[lat, lon], zoom_start=17, tiles="OpenStreetMap")

    hazards = result.get("hazards_detected", [])
    popup_html = f"""
    <div style='font-family:sans-serif;min-width:200px'>
        <b style='font-size:14px'>{result.get('primary_hazard','Unknown').replace('_',' ').title()}</b><br>
        <span style='color:{result.get("severity_color","#888")}'>
            ● {result.get('severity_label','Unknown')} Severity ({result.get('severity_score',0):.1f}/10)
        </span><br><br>
        <b>Road Condition:</b> {result.get('road_condition','N/A')}<br>
        <b>Hazards:</b> {', '.join(hazards)}<br><br>
        <i>{result.get('civic_report','')}</i>
    </div>
    """

    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{result.get('severity_label')} hazard detected",
        icon=folium.Icon(color=severity_color, icon="warning-sign", prefix="glyphicon")
    ).add_to(m)

    folium.Circle(
        [lat, lon], radius=20,
        color=severity_color, fill=True, fill_opacity=0.15
    ).add_to(m)

    return m
