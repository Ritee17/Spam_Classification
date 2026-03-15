```markdown
# Sentry AI: Agentic Spam & Phishing Detection System
**Category:** 5th Semester Mini-Project | CSE AIML & IoT  
**Developer:** Ritee & Team  

Sentry AI is a hybrid security system that moves beyond simple text classification. It uses a **Random Forest** model to detect spam patterns and an **Agentic URL Investigator** (powered by Playwright) to analyze live website destinations for phishing threats.

---

## 🏗️ System Architecture
The project is built as a **Decoupled API Service**, allowing Android apps and Chrome extensions to connect to a centralized "AI Brain."

1. **Sentry (ML Layer):** TF-IDF + Random Forest Classifier trained on Hinglish and Global spam datasets.
2. **Investigator (Agent Layer):** A headless Chromium agent that follows suspicious links to audit page metadata in real-time.
3. **The Bridge (FastAPI):** A production-ready API that logs every request for future "Active Learning" retraining.

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **ML Framework:** Scikit-Learn (Random Forest)
- **Agentic Engine:** Playwright (Chromium)
- **Backend:** FastAPI & Uvicorn
- **OS:** Ubuntu 22.04 (HP Victus)

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and set up the environment:
```bash
# Create Virtual Environment
python3 -m venv spam
source spam/bin/activate

# Install Dependencies
pip install -r requirements.txt
playwright install chromium

```

### 2. Training the Model

To ensure the vectorizer is fitted to the latest dataset:

```bash
python3 src/train_sentry.py

```

### 3. Launching the API

To host the service on your local network (for teammates to connect):

```bash
export PYTHONPATH=$PYTHONPATH:.
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

```

---

## 📡 API Endpoints

### **Health Check**

`GET /health`

Used to verify if the server is online.

### **Analyze Message**

`POST /analyze`

**Payload:**

```json
{
  "text": "Your message with a link [http://example.com](http://example.com)",
  "sender": "User_ID_or_Device"
}

```

**Response:**

```json
{
  "verdict": "SCAM",
  "confidence": "92.50%",
  "reason": "Agent flagged: Phishing keywords found in page title"
}

```

---

## 📊 Features

* **N-Gram Analysis:** Understands phrases like "Bank account" instead of just single words.
* **Active Logging:** All production traffic is saved to `data/production_logs.csv` for auditing.
* **Network Ready:** Configured to allow cross-device communication over Wi-Fi.

---

## 📂 Project Structure

* `src/`: Core logic (API, Predictor, Investigator, Trainer)
* `models/`: Saved `.pkl` files (Brain & Vectorizer)
* `data/`: Datasets and live production logs
* `requirements.txt`: Project dependencies

```
