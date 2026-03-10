# StreetSense v2.0 — AI Road Hazard Detection

AI-powered road hazard detection for Indian roads. Crowdsourced, real-time, with REST API and Telegram bot.

## Features
- **Image Analysis** — upload any road photo, get instant AI analysis
- **Live Camera** — webcam capture + instant analysis  
- **Video Analysis** — dashcam video, analyzes every Nth frame
- **Crowd Map** — all reports on a live heatmap
- **REST API** — integrate into any app or civic dashboard
- **Telegram Bot** — send a photo, get a report instantly

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run API Server
```bash
export GROQ_API_KEY=your_key
uvicorn api:app --reload --port 8000
```

## Run Telegram Bot
```bash
export GROQ_API_KEY=your_key
export TELEGRAM_TOKEN=your_token
python bot.py
```

## Author
Ajith Raj — github.com/ajithhraj
