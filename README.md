# 🛡️ Sentry AI: Hybrid Multi-Stage Phishing Detection System
**Category:** IIT Kanpur Hackathon Project | CSE AIML & IoT  
**Developer:** Ritee & Team

Sentry AI is a high-performance security engine that moves beyond simple text classification. It utilizes a **Cascading Hybrid Architecture**—combining a Fast-Path Random Forest model with a Deep-Path DistilBERT Transformer—to detect sophisticated phishing attempts that traditional models miss.

---

## 🏗️ System Architecture
The project is built as a **Decoupled API Service**, allowing multi-device connectivity (Mobile/Web) to a centralized "AI Brain."

1. **Adversarial Shield (Pre-processor):** Uses `unidecode` and regex to neutralize "Leet-speak," homoglyphs, and Unicode-based obfuscation.
2. **Sentry ML (Fast-Path):** N-Gram Tfidf + Random Forest Classifier for instant, low-latency detection of known scam patterns.
3. **Transformer (Deep-Path):** A DistilBERT-based Deep Learning layer that analyzes the *contextual intent* and *urgency* of subtle phishing messages.
4. **Intelligence Audit:** A real-time WHOIS investigator that audits domain registration dates to flag "Zero-Day" infrastructure.

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Deep Learning:** Hugging Face Transformers (DistilBERT)
- **ML Framework:** Scikit-Learn (Random Forest)
- **Backend:** FastAPI & Uvicorn (Asynchronous)
- **OS:** Ubuntu 22.04 (HP Victus Optimized)

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the advanced dependency stack:

```bash
# Create Virtual Environment
python3 -m venv spam
source spam/bin/activate

# Install Dependencies
pip install fastapi uvicorn joblib scikit-learn transformers torch python-whois unidecode

```

### 2. Training the "Fast-Path"

To ensure the vectorizer is fitted to the latest N-gram dataset:

```bash
python3 src/train_sentry.py

```

### 3. Launching the API

To host the service on your local network for cross-device testing:

```bash
export PYTHONPATH=$PYTHONPATH:.
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

```

---

## 📡 API Endpoints

### Analyze Message

`POST /analyze`

**Request Payload:**

```json
{
  "text": "Urg€nt: Your @ccount is flаggеd. Vеrify hеrе: [http://secure-check.in](http://secure-check.in)",
  "sender": "Security-Dept"
}

```

**Response (Hybrid Verdict):**

```json
{
  "verdict": "SCAM",
  "confidence": "94.20%",
  "logic_route": "Hybrid Ensemble + Intel Audit",
  "metadata": {
    "cleaned_text": "urgent: your account is flagged...",
    "domain_age_days": 4
  }
}

```

---

## 📊 Elite Features

* **Ensemble Fusion:** Combines classical ML and NLP Transformers for a balanced Accuracy-Latency trade-off.
* **Zero-Day Protection:** Automatically flags any domain registered in the last 30 days.
* **Adversarial Resilience:** Immune to character-replacement tricks (e.g., swapping 'o' with '0').
* **Active Logging:** Every request is logged to `data/production_logs.csv` for future model retraining.

---

## 📂 Project Structure

* `src/`: Core logic (API, Normalizer, Trainer)
* `models/`: Saved `.pkl` files (RF Brain & Vectorizer)
* `data/`: Datasets and live production logs
* `requirements.txt`: Project dependencies
