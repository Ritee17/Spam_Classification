from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import joblib
import os
import csv
import asyncio
import whois
import re
import time
from collections import defaultdict
from unidecode import unidecode
from transformers import pipeline

app = FastAPI(title="Sentry AI: Final Winning Build")

# --- 1. Global Assets & Models ---
base_path = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_path, '../models/sentry_model.pkl'))
tfidf = joblib.load(os.path.join(base_path, '../models/tfidf_vectorizer.pkl'))
deep_sentry = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

# Import your helper functions
from src.predict import extract_url

# In-memory rate limiter (Security feature)
user_history = defaultdict(list)

class MessageRequest(BaseModel):
    text: str
    sender: str = "Unknown"

# --- 2. Security & Logic Functions ---

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Prevents API abuse: Max 20 requests per minute per IP."""
    client_ip = request.client.host
    now = time.time()
    user_history[client_ip] = [t for t in user_history[client_ip] if now - t < 60]
    if len(user_history[client_ip]) > 20:
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded (20 req/min)"})
    user_history[client_ip].append(now)
    return await call_next(request)

def normalize_text(text: str):
    """Adversarial Shield: Handles homoglyphs and accented characters."""
    text = unidecode(text)
    text = text.lower()
    replacements = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b'}
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    return re.sub(r'(?<=[\w])[.!-](?=[\w])', '', text)

def analyze_tactics(text: str):
    """Explainable AI (XAI): Identifies the scammer's psychological triggers."""
    tactics = []
    text_lower = text.lower()
    if any(w in text_lower for w in ['urgent', 'immediately', 'now', 'expire', 'lock', 'detect']):
        tactics.append("Urgency/Fear-Bait")
    if any(w in text_lower for w in ['winner', 'prize', 'cash', 'reward', 'offer', 'free']):
        tactics.append("Financial Incentive")
    if 'http' in text_lower:
        tactics.append("Malicious Redirection")
    return tactics

async def audit_domain_age(url: str):
    try:
        domain = url.split("//")[-1].split("/")[0]
        loop = asyncio.get_event_loop()
        w = await loop.run_in_executor(None, whois.whois, domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list): creation_date = creation_date[0]
        if creation_date:
            days_old = (datetime.now() - creation_date).days
            return {"is_new": days_old < 30, "age": days_old}
    except:
        return {"is_new": False, "age": "Unknown"}
    return {"is_new": False, "age": 999}

# --- 3. Endpoints ---

@app.get("/health")
async def health():
    return {"status": "Sentry AI Online", "engine": "Hybrid Ensemble (RF + BERT)", "time": datetime.now()}

@app.post("/feedback")
async def model_feedback(text: str, correct_label: int):
    """Active Learning: Log misclassifications for model retraining."""
    feedback_path = os.path.join(base_path, '../data/feedback_data.csv')
    with open(feedback_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), text, correct_label])
    return {"message": "Feedback received. This data will be used to improve the Sentry Brain."}

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    try:
        clean_text = normalize_text(request.text)
        
        # Stage 1: Random Forest
        data = tfidf.transform([clean_text])
        rf_prob = float(model.predict_proba(data)[0][1])
        
        # Stage 2: Transformer (BERT)
        loop = asyncio.get_event_loop()
        deep_res = await loop.run_in_executor(None, lambda: deep_sentry(clean_text)[0])
        is_scam_label = "LABEL_0" in deep_res['label']
        deep_prob = deep_res['score'] if is_scam_label else (1 - deep_res['score'])
        
        # Ensemble Fusion
        final_confidence = (rf_prob * 0.3) + (deep_prob * 0.7)
        route = "Hybrid Ensemble"

        # Stage 3: Intelligence Audit
        url = extract_url(request.text)
        intel_report = {"is_new": False, "age": "N/A"}
        if url:
            intel_report = await audit_domain_age(url)
            if intel_report.get("is_new"):
                final_confidence = 1.0
                route += " + Domain Audit"

        # Final Verdict Decision
        if final_confidence > 0.50: 
            verdict = "SCAM"
        elif final_confidence > 0.25:
            verdict = "SUSPICIOUS"
        else:
            verdict = "SAFE"

        # XAI: Tactics Extraction
        threats = analyze_tactics(clean_text)

        # Logging
        log_path = os.path.join(base_path, '../data/production_logs.csv')
        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), request.sender, request.text, verdict, route])

        return {
            "verdict": verdict,
            "confidence": f"{final_confidence:.2%}",
            "analysis": {
                "logic_route": route,
                "threat_profile": threats,
                "infrastructure_risk": "High (New Domain)" if intel_report.get("is_new") else "Low"
            },
            "metadata": {
                "cleaned_text": clean_text,
                "domain_age": intel_report.get("age"),
                "rf_score": f"{rf_prob:.4f}",
                "bert_score": f"{deep_prob:.4f}"
            }
        }

    except Exception as e:
        return {"error": str(e)}