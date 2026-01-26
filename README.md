# 🍯 Agentic Honey-Pot API

> AI-powered honeypot that detects scams, engages fraudsters, and extracts intelligence — built for GUVI Hackathon 2026.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Gemini](https://img.shields.io/badge/AI-Gemini_Flash-orange)

---

## 🎯 Problem Statement

Scammers target vulnerable users via SMS, WhatsApp, and calls with fake bank alerts, KYC threats, and prize notifications. This project creates an **AI agent** that:
1. **Detects** scam intent using NLP and pattern matching
2. **Engages** scammers with a believable "victim" persona to waste their time
3. **Extracts** intelligence (UPI IDs, phone numbers, phishing links)
4. **Reports** findings to a central callback endpoint

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Scam Detection** | Keyword + regex pattern matching (English + Hindi) |
| 🤖 **AI Agent "Ramesh"** | Gemini-powered persona that acts confused and asks questions |
| 🛡️ **Ethical Safety** | Agent never uses abusive language, even when provoked |
| 📊 **Intelligence Extraction** | Captures bank accounts, UPI IDs, phone numbers, links |
| 💾 **Session Persistence** | JSON-based storage survives server restarts |
| ⚡ **Rate Limiting** | 60 requests/minute per IP to prevent abuse |
| 🔐 **CORS + API Auth** | Restricted origins + API key authentication |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scammer   │────▶│  FastAPI    │────▶│   Gemini    │
│  (Attacker) │     │   Server    │     │   AI Agent  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Scam    │ │  Intel   │ │  GUVI    │
        │ Detector │ │ Extractor│ │ Callback │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
# Edit .env with your keys
```

| Variable | Description |
|----------|-------------|
| `API_KEY` | Secret key for API authentication |
| `GOOGLE_API_KEY` | Gemini API key ([Get Free](https://aistudio.google.com/app/apikey)) |
| `GUVI_CALLBACK_URL` | Endpoint for result submission |

### 3. Run Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Test
```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"1.0.0"}
```

---

## 📡 API Reference

### `POST /analyze`
Analyze a message and get AI response.

**Headers:**
```
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked. Share OTP now!",
    "timestamp": "2026-01-26T10:00:00Z"
  },
  "conversationHistory": []
}
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Oh no sir! Which account? I have SBI and PNB...",
  "engagementMetrics": {
    "engagementDurationSeconds": 120,
    "totalMessagesExchanged": 5
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phoneNumbers": [],
    "phishingLinks": [],
    "suspiciousKeywords": ["blocked", "otp", "urgent"]
  },
  "agentNotes": "Scammer used urgency tactics, threatening language"
}
```

### Other Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/session/{id}` | Get session details |
| `DELETE` | `/session/{id}` | End session & trigger callback |

---

## 🔐 Security Features

- ✅ **API Key Authentication** — All endpoints protected
- ✅ **CORS Restriction** — Only trusted origins allowed
- ✅ **Rate Limiting** — 60 req/min per IP
- ✅ **Ethical AI Guidelines** — Agent cannot be toxic
- ✅ **Session Persistence** — Data survives restarts
- ✅ **.gitignore** — Secrets excluded from git

---

## 📦 Deployment

### Render (Recommended)
1. Push to GitHub
2. Create Web Service on [Render](https://render.com)
3. Set environment variables
4. Deploy with `render.yaml`

### Docker
```bash
docker build -t honeypot .
docker run -p 8000:8000 --env-file .env honeypot
```

---

## � Project Structure

```
HoneyPot/
├── app/
│   ├── main.py           # FastAPI app + endpoints
│   ├── agent.py          # Gemini AI agent ("Ramesh")
│   ├── scam_detector.py  # Keyword/pattern detection
│   ├── intelligence.py   # UPI/phone/link extraction
│   ├── session.py        # Session management + persistence
│   ├── callback.py       # GUVI callback handler
│   └── models.py         # Pydantic schemas
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container config
├── render.yaml           # Render deployment config
└── README.md             # This file
```

---

## 🧪 Testing

Run the test suite:
```bash
python test_100_messages.py
```

---

## 👥 Team

Built with ❤️ for **GUVI Hackathon 2026**

---

## 📄 License

MIT License - Feel free to use and modify!
