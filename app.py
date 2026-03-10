# app.py — StreetSense v2.0

import streamlit as st
from PIL import Image
from io import BytesIO
import json, time
from src.analyzer import analyze_image
from src.gps_extractor import extract_gps
from src.map_builder import build_map
from src.database import save_report, get_all_reports, get_stats
from src.crowdmap import build_crowdmap
from src.hazard_taxonomy import HAZARDS

st.set_page_config(page_title="StreetSense", page_icon="🛣️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', -apple-system, sans-serif !important; background-color: #000 !important; color: #f5f5f7 !important; }
.stApp { background: #000; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1100px; }
section[data-testid="stSidebar"] { background: #0a0a0a !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
section[data-testid="stSidebar"] * { color: #f5f5f7 !important; }
section[data-testid="stSidebar"] .stTextInput input { background: #1c1c1e !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #f5f5f7 !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }
.stFileUploader { background: #111 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 16px !important; }
.stButton > button { background: #2997ff !important; color: #fff !important; border: none !important; border-radius: 980px !important; padding: 0.55rem 2rem !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 14px !important; width: 100% !important; transition: opacity 0.15s !important; }
.stButton > button:hover { opacity: 0.85 !important; background: #2997ff !important; color: #fff !important; }
.stDownloadButton > button { background: transparent !important; color: #2997ff !important; border: 1px solid rgba(41,151,255,0.3) !important; border-radius: 980px !important; padding: 0.5rem 1.5rem !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 13px !important; width: auto !important; }
.stTabs [data-baseweb="tab-list"] { background: #111 !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; border: 1px solid rgba(255,255,255,0.07) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #636366 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; padding: 6px 16px !important; }
.stTabs [aria-selected="true"] { background: #1c1c1e !important; color: #f5f5f7 !important; }
.stNumberInput input, .stSelectbox select { background: #1c1c1e !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #f5f5f7 !important; }
.stProgress > div > div { background: #2997ff !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 16px'>
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>
            <div style='width:8px;height:8px;background:#2997ff;border-radius:50%;box-shadow:0 0 8px #2997ff'></div>
            <span style='font-size:16px;font-weight:600;letter-spacing:-0.3px'>StreetSense</span>
            <span style='font-size:10px;background:#1c1c1e;border:1px solid rgba(255,255,255,0.1);
                padding:2px 7px;border-radius:20px;color:#636366;letter-spacing:0.5px'>v2.0</span>
        </div>
        <p style='color:#48484a;font-size:12px;margin:0;padding-left:16px'>Road Hazard Detection</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...",
                            help="Get a free key at console.groq.com")
    st.markdown("<p style='color:#48484a;font-size:11px;margin-top:4px'>Free at console.groq.com</p>", unsafe_allow_html=True)
    st.divider()

    location_name = st.text_input("Location", placeholder="e.g. Koramangala, Bengaluru")
    st.divider()

    # Live stats
    stats = get_stats()
    st.markdown(f"""
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px'>
        <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:10px 12px'>
            <p style='color:#48484a;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin:0 0 3px'>Reports</p>
            <p style='font-size:1.3rem;font-weight:700;color:#f5f5f7;margin:0;letter-spacing:-0.5px'>{stats['total']}</p>
        </div>
        <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:10px 12px'>
            <p style='color:#48484a;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin:0 0 3px'>Critical</p>
            <p style='font-size:1.3rem;font-weight:700;color:#ff453a;margin:0;letter-spacing:-0.5px'>{stats['critical']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='color:#3a3a3c;font-size:11px'>by Ajith Raj · LLaMA 4 Scout via Groq</p>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:1.5rem 0 2rem;text-align:center'>
    <h1 style='font-size:2.4rem;font-weight:700;letter-spacing:-1.5px;color:#f5f5f7;margin-bottom:6px'>StreetSense</h1>
    <p style='color:#636366;font-size:14px;letter-spacing:-0.2px'>AI road hazard detection · Crowdsourced · Real-time</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Analyze", "Live Camera", "Video", "Crowd Map", "API"])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — ANALYZE
# ────────────────────────────────────────────────────────────────────────────

def show_result(result, gps, location_name):
    passable_color = "#30d158" if result.get("passable") else "#ff453a"
    passable_text  = "Passable" if result.get("passable") else "Impassable"

    st.markdown(f"""
    <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:20px;
        padding:24px 28px;margin:20px 0 12px;display:flex;align-items:center;justify-content:space-between'>
        <div>
            <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px'>Assessment</p>
            <h2 style='font-size:1.8rem;font-weight:700;letter-spacing:-0.8px;margin:0;color:{result["severity_color"]}'>{result.get("road_condition","Unknown")}</h2>
            <p style='color:#636366;font-size:13px;margin:4px 0 0'>{result.get("primary_hazard","").replace("_"," ").title()} · {result.get("location_in_frame","").title()}</p>
        </div>
        <div style='text-align:right'>
            <div style='font-size:2.8rem;font-weight:700;letter-spacing:-2px;color:{result["severity_color"]};line-height:1'>{result["severity_score"]:.1f}</div>
            <div style='color:#48484a;font-size:11px'>out of 10</div>
            <div style='margin-top:6px;background:rgba(255,255,255,0.05);border-radius:20px;padding:3px 12px;display:inline-block'>
                <span style='font-size:11px;font-weight:500;color:{passable_color}'>{passable_text}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    def mcard(label, val, sub):
        return f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px'>
            <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px'>{label}</p>
            <p style='font-size:1.5rem;font-weight:700;letter-spacing:-0.5px;color:#f5f5f7;margin:0'>{val}</p>
            <p style='color:#636366;font-size:11px;margin:3px 0 0'>{sub}</p>
        </div>"""
    with m1: st.markdown(mcard("Severity", result.get("severity_label","?"), f"Score {result['severity_score']:.1f}/10"), unsafe_allow_html=True)
    with m2: st.markdown(mcard("Confidence", f"{int(result.get('confidence',0)*100)}%", "Model confidence"), unsafe_allow_html=True)
    with m3: st.markdown(mcard("Area Affected", f"{result.get('affected_area_percent',0)}%", "of visible road"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    tags = "".join([f"<span style='background:#1c1c1e;border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:5px 14px;font-size:12px;font-weight:500;color:#f5f5f7;margin:3px'>{HAZARDS.get(h,{}).get('icon','⚠️')} {h.replace('_',' ').title()}</span>" for h in result.get("hazards_detected",[])])
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:16px'>{tags}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-left:3px solid #ff9f0a;border-radius:0 14px 14px 0;padding:16px 18px'>
            <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px'>Immediate Action</p>
            <p style='color:#f5f5f7;font-size:13px;line-height:1.7;margin:0;font-weight:500'>{result.get('immediate_action','')}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-left:3px solid #2997ff;border-radius:0 14px 14px 0;padding:16px 18px'>
            <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px'>Civic Report</p>
            <p style='color:#98989d;font-size:13px;line-height:1.7;margin:0;font-style:italic'>{result.get('civic_report','')}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if gps:
        from streamlit_folium import folium_static
        m = build_map(gps["lat"], gps["lon"], result)
        folium_static(m, width=None, height=360)

    export = {"location": location_name,"gps": gps,"hazards": result.get("hazards_detected"),
        "severity_score": result.get("severity_score"),"severity_label": result.get("severity_label"),
        "road_condition": result.get("road_condition"),"confidence": result.get("confidence"),
        "passable": result.get("passable"),"civic_report": result.get("civic_report")}
    st.download_button("Export Report as JSON", data=json.dumps(export, indent=2),
        file_name="streetsense_report.json", mime="application/json")

with tab1:
    uploaded_file = st.file_uploader("Upload a road image", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        col1, col2 = st.columns([1.1, 1], gap="large")
        with col1:
            st.image(image, use_column_width=True)
            gps = extract_gps(image_bytes)
            if gps:
                st.markdown(f"<div style='margin-top:8px;background:#1c1c1e;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:10px 14px;font-size:12px;color:#636366'>📍 GPS · <span style='color:#f5f5f7'>{gps['lat']:.5f}, {gps['lon']:.5f}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='margin-top:8px;background:#1c1c1e;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:10px 14px;font-size:12px;color:#3a3a3c'>No GPS metadata</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if not api_key:
                st.markdown("<div style='background:#1c1c1e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px;text-align:center;color:#48484a;font-size:13px'>Add your Groq API key in the sidebar</div>", unsafe_allow_html=True)
            else:
                if st.button("Analyze Road", key="analyze_btn"):
                    with st.spinner("Analyzing with LLaMA 4 Scout..."):
                        try:
                            result = analyze_image(image, api_key, location_name)
                            save_report(result, gps, location_name, source="web")
                            st.session_state["result"] = result
                            st.session_state["gps"] = gps
                        except Exception as e:
                            st.error(str(e))

        if "result" in st.session_state:
            show_result(st.session_state["result"], st.session_state.get("gps"), location_name)
    else:
        st.markdown("""<div style='text-align:center;padding:4rem 2rem;border:1px solid rgba(255,255,255,0.05);
            border-radius:20px;background:#080808;margin-top:1rem'>
            <div style='font-size:3rem;margin-bottom:1rem'>🛣️</div>
            <p style='font-size:15px;color:#3a3a3c;margin:0;font-weight:500'>Upload a road photo or dashcam frame</p>
            <p style='font-size:13px;color:#2c2c2e;margin-top:6px'>JPG · PNG · WEBP</p>
        </div>""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — LIVE CAMERA
# ────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("<p style='color:#636366;font-size:13px;margin-bottom:16px'>Capture a photo using your webcam or phone camera for instant analysis.</p>", unsafe_allow_html=True)

    camera_img = st.camera_input("Point camera at a road", label_visibility="collapsed")

    if camera_img:
        image_bytes = camera_img.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.image(image, use_column_width=True)
        with col2:
            if not api_key:
                st.markdown("<div style='background:#1c1c1e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px;text-align:center;color:#48484a;font-size:13px'>Add your Groq API key in the sidebar</div>", unsafe_allow_html=True)
            else:
                if st.button("Analyze Capture", key="cam_btn"):
                    with st.spinner("Analyzing..."):
                        try:
                            result = analyze_image(image, api_key, location_name)
                            save_report(result, None, location_name, source="camera")
                            st.session_state["cam_result"] = result
                        except Exception as e:
                            st.error(str(e))

        if "cam_result" in st.session_state:
            show_result(st.session_state["cam_result"], None, location_name)

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — VIDEO
# ────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("<p style='color:#636366;font-size:13px;margin-bottom:16px'>Upload a dashcam video. StreetSense will analyze every Nth frame and build a full road condition report.</p>", unsafe_allow_html=True)

    video_file = st.file_uploader("Upload dashcam video", type=["mp4","mov","avi"], label_visibility="collapsed")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        every_n = st.selectbox("Analyze every N frames", [3, 5, 10, 15, 30], index=1)

    if video_file and api_key:
        if st.button("Analyze Video", key="video_btn"):
            from src.video_analyzer import analyze_video, get_video_summary

            video_bytes = video_file.read()
            progress_bar = st.progress(0)
            status_text  = st.empty()
            frames_done  = st.empty()

            results = []

            def progress_cb(i, total, ts):
                pct = int((i / total) * 100)
                progress_bar.progress(pct)
                status_text.markdown(f"<p style='color:#636366;font-size:12px'>Analyzing frame at {ts:.1f}s...</p>", unsafe_allow_html=True)
                frames_done.markdown(f"<p style='color:#f5f5f7;font-size:12px'>{i}/{total} frames</p>", unsafe_allow_html=True)

            with st.spinner("Processing video..."):
                try:
                    results = analyze_video(video_bytes, api_key, every_n, location_name, progress_cb)
                    progress_bar.progress(100)
                    st.session_state["video_results"] = results
                except Exception as e:
                    st.error(str(e))

    if "video_results" in st.session_state:
        from src.video_analyzer import get_video_summary
        results = st.session_state["video_results"]
        summary = get_video_summary(results)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px'>Video Summary</p>", unsafe_allow_html=True)

        v1, v2, v3, v4 = st.columns(4)
        def vcard(label, val, color="#f5f5f7"):
            return f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 16px'>
                <p style='color:#48484a;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 4px'>{label}</p>
                <p style='font-size:1.4rem;font-weight:700;color:{color};margin:0;letter-spacing:-0.5px'>{val}</p>
            </div>"""

        with v1: st.markdown(vcard("Frames Analyzed", summary.get("total_frames_analyzed", 0)), unsafe_allow_html=True)
        with v2: st.markdown(vcard("Avg Severity", f"{summary.get('avg_severity',0):.1f}/10", "#ff9f0a"), unsafe_allow_html=True)
        with v3: st.markdown(vcard("Safe Sections", f"{summary.get('safe_pct',0)}%", "#30d158"), unsafe_allow_html=True)
        with v4: st.markdown(vcard("Critical Sections", f"{summary.get('critical_pct',0)}%", "#ff453a"), unsafe_allow_html=True)

        # Worst moment
        worst = summary.get("worst_moment")
        if worst:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div style='background:#111;border:1px solid rgba(255,69,58,0.2);border-left:3px solid #ff453a;border-radius:0 14px 14px 0;padding:16px 18px'>
                <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 6px'>Worst Moment — {worst.get('timestamp',0):.1f}s</p>
                <p style='color:#f5f5f7;font-size:14px;font-weight:600;margin:0'>{worst.get('road_condition','?')} — Severity {worst.get('severity_score',0):.1f}/10</p>
                <p style='color:#636366;font-size:12px;margin:4px 0 0'>{worst.get('civic_report','')}</p>
            </div>""", unsafe_allow_html=True)

        # Frame strip
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px'>Frame Analysis</p>", unsafe_allow_html=True)

        cols = st.columns(min(4, len(results)))
        for i, (col, r) in enumerate(zip(cols * (len(results)//len(cols)+1), results[:8])):
            with col:
                if "frame_image" in r:
                    st.image(r["frame_image"], use_column_width=True)
                score = r.get("severity_score", 0)
                color = "#30d158" if score < 3 else "#ff9f0a" if score < 7 else "#ff453a"
                st.markdown(f"<p style='text-align:center;font-size:11px;color:{color};margin:2px 0'>{score:.1f}/10 · {r.get('timestamp',0):.1f}s</p>", unsafe_allow_html=True)

    elif video_file and not api_key:
        st.markdown("<div style='background:#1c1c1e;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px;text-align:center;color:#48484a;font-size:13px'>Add your Groq API key in the sidebar</div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — CROWD MAP
# ────────────────────────────────────────────────────────────────────────────

with tab4:
    st.markdown("<p style='color:#636366;font-size:13px;margin-bottom:16px'>All reported hazards from the community plotted on a live map. Heatmap shows hazard density.</p>", unsafe_allow_html=True)

    stats = get_stats()
    cs1, cs2, cs3, cs4 = st.columns(4)
    def scard(label, val, color="#f5f5f7"):
        return f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 16px;text-align:center'>
            <p style='color:#48484a;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 4px'>{label}</p>
            <p style='font-size:1.4rem;font-weight:700;color:{color};margin:0;letter-spacing:-0.5px'>{val}</p>
        </div>"""

    with cs1: st.markdown(scard("Total Reports", stats["total"]), unsafe_allow_html=True)
    with cs2: st.markdown(scard("Avg Severity", f"{stats['avg_severity']}/10", "#ff9f0a"), unsafe_allow_html=True)
    with cs3: st.markdown(scard("Critical", stats["critical"], "#ff453a"), unsafe_allow_html=True)
    with cs4: st.markdown(scard("Top Hazard", stats["most_common_hazard"].replace("_"," ").title()), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if st.button("Refresh Map", key="refresh_map"):
        st.rerun()

    from streamlit_folium import folium_static
    crowd_map, total_reports, geo_reports = build_crowdmap()
    folium_static(crowd_map, width=None, height=500)

    st.markdown(f"<p style='color:#3a3a3c;font-size:11px;text-align:center;margin-top:8px'>{geo_reports} of {total_reports} reports have GPS coordinates</p>", unsafe_allow_html=True)

    # Reports table
    if total_reports > 0:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px'>Recent Reports</p>", unsafe_allow_html=True)
        reports = get_all_reports()
        for r in reports[:10]:
            hazards = r.get("hazards", [])
            icons = " ".join([HAZARDS.get(h, {}).get("icon", "⚠️") for h in hazards[:2]])
            color = "#ff453a" if r["severity_score"] >= 7.5 else "#ff9f0a" if r["severity_score"] >= 5 else "#30d158"
            st.markdown(f"""<div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:12px;
                padding:12px 16px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center'>
                <div>
                    <span style='font-size:13px;font-weight:500;color:#f5f5f7'>{icons} {r.get('primary_hazard','?').replace('_',' ').title()}</span>
                    <span style='font-size:11px;color:#48484a;margin-left:10px'>{r.get('location') or 'Unknown'} · {r.get('source','web')} · {r.get('created_at','')[:10]}</span>
                </div>
                <span style='font-size:13px;font-weight:600;color:{color}'>{r.get('severity_score',0):.1f}/10</span>
            </div>""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — API DOCS
# ────────────────────────────────────────────────────────────────────────────

with tab5:
    st.markdown("""
    <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:16px'>
        <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px'>Base URL</p>
        <code style='font-size:14px;color:#2997ff;background:#1c1c1e;padding:6px 12px;border-radius:8px'>http://localhost:8000</code>
        <p style='color:#636366;font-size:12px;margin-top:10px'>Start the API server: <code style='color:#f5f5f7'>uvicorn api:app --reload --port 8000</code></p>
    </div>
    """, unsafe_allow_html=True)

    endpoints = [
        ("POST", "/analyze", "Analyze a road image", "Multipart form: file (image) + location (str) + save (bool)"),
        ("GET",  "/reports", "List all reports", "Query param: limit (int, default 50)"),
        ("GET",  "/reports/{id}", "Get single report", "Path param: report ID"),
        ("GET",  "/stats", "Global statistics", "Returns totals, averages, most common hazard"),
        ("GET",  "/health", "Health check", "Returns API status"),
        ("GET",  "/docs", "Swagger UI", "Interactive API documentation"),
    ]

    for method, path, desc, params in endpoints:
        color = "#30d158" if method == "GET" else "#ff9f0a"
        st.markdown(f"""
        <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:12px;
            padding:14px 18px;margin-bottom:8px;display:flex;align-items:flex-start;gap:14px'>
            <span style='background:{color}22;color:{color};font-size:10px;font-weight:700;
                padding:3px 8px;border-radius:6px;letter-spacing:0.5px;flex-shrink:0;margin-top:1px'>{method}</span>
            <div>
                <code style='font-size:13px;color:#f5f5f7'>{path}</code>
                <p style='color:#636366;font-size:12px;margin:3px 0 0'>{desc} · <span style='color:#48484a'>{params}</span></p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#111;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:20px 24px'>
        <p style='color:#48484a;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin:0 0 12px'>Example — Python</p>
        <pre style='color:#f5f5f7;font-size:12px;margin:0;line-height:1.8'>import requests

with open("road.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        data={"location": "MG Road, Bengaluru", "save": True}
    )

result = response.json()
print(result["severity_score"])   # 7.5
print(result["hazards_detected"]) # ["pothole", "waterlogging"]
print(result["civic_report"])     # Formal report text</pre>
    </div>
    """, unsafe_allow_html=True)
