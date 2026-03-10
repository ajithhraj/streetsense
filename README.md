# StreetSense v2.0 — AI Road Hazard Detector

<div align="center">

**🌍 Live Demo → [streetsense.streamlit.app](https://streetsense.streamlit.app)**

![Standalone](https://img.shields.io/badge/standalone-no%20signup%20needed-30d158?style=flat-square)
![Powered by](https://img.shields.io/badge/powered%20by-LLaMA%204%20Scout-2997ff?style=flat-square)
![Built with](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-white?style=flat-square)

AI-powered road hazard detection built specifically for Indian road conditions.  
Upload any road photo and get instant analysis — **no signup, no installation required.**

</div>

---

## 🚀 Try It Now

> **[streetsense.streamlit.app](https://streetsense.streamlit.app)** — fully standalone, works in any browser, no account needed.

Just open the link, upload a road photo, and get a complete hazard report in seconds.

---

## What It Does

StreetSense uses **LLaMA 4 Scout** (via Groq) to analyze road images and detect hazards common to Indian roads. It returns a severity score, formal civic report, and actionable advice for drivers — all in under 5 seconds.

### Detectable Hazards

| Icon | Hazard | Severity Weight |
|------|--------|----------------|
| ⚠️ | Pothole | 0.8 |
| 🌊 | Waterlogging | 0.9 |
| 🕳️ | Missing Manhole | 1.0 |
| 🛣️ | Broken Road | 0.7 |
| 🪨 | Debris | 0.6 |
| 🚧 | Broken Divider | 0.5 |
| 〰️ | Faded Markings | 0.4 |
| 🚫 | Broken Signage | 0.5 |
| 🏪 | Encroachment | 0.4 |
| 〽️ | Unmarked Speed Breaker | 0.5 |

---

## Features

### 📸 Image Analysis
Upload any road photo or dashcam frame. Get severity score (0–10), hazard tags, road condition label, confidence rating, immediate driver action, and a formal civic report ready to submit to municipal authorities.

### 📷 Live Camera
Use your webcam or phone camera to capture and analyze road conditions in real time.

### 🎬 Video Analysis
Upload a dashcam video. StreetSense extracts every Nth frame, analyzes each one, and produces a full timeline report — worst moment, average severity, safe vs critical sections.

### 🗺️ Crowd Map
Every submitted report is saved and plotted on a live OpenStreetMap heatmap. See hazard density across the city at a glance.

### 🔌 REST API
Integrate StreetSense into any civic dashboard, mobile app, or data pipeline.

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@road.jpg" \
  -F "location=MG Road, Bengaluru"
```

### 🤖 Telegram Bot
Send any road photo to the bot and receive a full hazard report instantly.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Vision + Language | LLaMA 4 Scout 17B via Groq API |
| Web App | Streamlit |
| Maps | Folium + OpenStreetMap |
| Database | SQLite |
| REST API | FastAPI + Uvicorn |
| Bot | python-telegram-bot |
| Image Processing | Pillow, OpenCV |
| GPS Extraction | ExifRead |

---

## Run Locally

```bash
git clone https://github.com/ajithhraj/streetsense.git
cd streetsense
pip install -r requirements.txt
streamlit run app.py
```

Add your Groq API key in the sidebar (free at [console.groq.com](https://console.groq.com)).

### Run API Server
```bash
export GROQ_API_KEY=your_key
uvicorn api:app --reload --port 8000
# Docs at http://localhost:8000/docs
```

### Run Telegram Bot
```bash
export GROQ_API_KEY=your_key
export TELEGRAM_TOKEN=your_token
python bot.py
```

---

## Project Structure

```
streetsense/
├── app.py                  # Streamlit web app (5 tabs)
├── api.py                  # FastAPI REST server
├── bot.py                  # Telegram bot
├── requirements.txt
└── src/
    ├── analyzer.py         # Groq vision + LLM pipeline
    ├── hazard_taxonomy.py  # 10 Indian road hazard types
    ├── gps_extractor.py    # EXIF GPS metadata reader
    ├── map_builder.py      # Single-report map
    ├── crowdmap.py         # Crowdsourced heatmap
    ├── database.py         # SQLite report storage
    └── video_analyzer.py   # Frame extraction + batch analysis
```

---

## Part of GSoC Profile

This project is part of a series of AI/ML projects built to demonstrate research-grade engineering:

| Project | Description | Link |
|---------|-------------|------|
| 🧠 Neural Network from Scratch | NumPy-only NN, 97.9% MNIST accuracy | [github](https://github.com/ajithhraj/neural-network-from-scratch) |
| 💬 Sentiment Monitor | YouTube comment NLP analyzer | [github](https://github.com/ajithhraj/sentiment-monitor) |
| 🔍 Sense AI | Chrome extension for YouTube sentiment | [github](https://github.com/ajithhraj/sense-ai) |
| 🛣️ StreetSense | Road hazard detection · **Live** | [streetsense.streamlit.app](https://streetsense.streamlit.app) |

---

## Author

**Ajith Raj** — [github.com/ajithhraj](https://github.com/ajithhraj)

---

## License

MIT
