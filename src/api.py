from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import joblib
import os
import csv
import asyncio
import whois
import re
from transformers import pipeline

app = FastAPI(title="Sentry AI: Hackathon Final Build")

# --- 1. Load Models & Assets ---
base_path = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_path, '../models/sentry_model.pkl'))
tfidf = joblib.load(os.path.join(base_path, '../models/tfidf_vectorizer.pkl'))

# Load Transformer (mrm8488/bert-tiny-finetuned-sms-spam-detection)
# Mapping: LABEL_0 = SCAM | LABEL_1 = SAFE
deep_sentry = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

from src.predict import extract_url
from src.investigator import investigate_url

class MessageRequest(BaseModel):
    text: str
    sender: str = "Unknown"

# --- 2. Security Infrastructure Functions ---

from unidecode import unidecode

def normalize_text(text: str):
    """Elite Adversarial Shield: Converts 'Urg€nt' and 'héré' to 'urgent' and 'here'."""
    # 1. Convert to ASCII (handles accented chars like é, á, symbols like €)
    text = unidecode(text)
    
    # 2. Lowercase for consistency
    text = text.lower()
    
    # 3. Handle manual symbol-to-letter mapping (for things unidecode might miss)
    replacements = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b'}
    for char, rep in replacements.items():
        text = text.replace(char, rep)
        
    # 4. Remove hidden punctuation like W.I.N.N.E.R
    text = re.sub(r'(?<=[\w])[.!-](?=[\w])', '', text)
    
    return text

async def audit_domain_age(url: str):
    """Infrastructure Audit: Checks WHOIS data for new domains."""
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

# --- 3. The Core Analysis Engine ---

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    try:
        # Step A: Pre-processing
        clean_text = normalize_text(request.text)
        
        # Step B: Stage 1 - Random Forest (Keyword Check)
        data = tfidf.transform([clean_text])
        rf_prob = float(model.predict_proba(data)[0][1])
        
        # Step C: Stage 2 - Transformer Escalation (Context Check)
        loop = asyncio.get_event_loop()
        deep_res = await loop.run_in_executor(None, lambda: deep_sentry(clean_text)[0])
        
        # BERT Label Mapping: LABEL_0 is Scam
        is_scam_detected = "LABEL_0" in deep_res['label']
        deep_prob = deep_res['score'] if is_scam_detected else (1 - deep_res['score'])
        
        # Step D: Ensemble Fusion (Giving BERT 80% weight for context-heavy phishing)
        final_confidence = (rf_prob * 0.2) + (deep_prob * 0.8)
        route = "Hybrid Ensemble"

        # Step E: Stage 3 - Intelligence Audit (Infrastructure Check)
        url = extract_url(request.text)
        intel_report = {"is_new": False, "age": "N/A"}
        if url:
            intel_report = await audit_domain_age(url)
            if intel_report.get("is_new"):
                final_confidence = 1.0 # Intelligence Override
                route += " + Intel Audit (New Domain)"

        # Step F: Final Verdict (Sensitivity Tuned for Phishing)
        if final_confidence > 0.50: 
            verdict = "SCAM"
        elif final_confidence > 0.20:
            verdict = "SUSPICIOUS"
        else:
            verdict = "SAFE"

        # --- TERMINAL LOGGING FOR LIVE DEMO ---
        print(f"--- INCOMING: {request.sender} ---")
        print(f"Text: {clean_text[:50]}...")
        print(f"RF: {rf_prob:.2f} | BERT: {deep_prob:.2f} | Final: {final_confidence:.2f}")
        print(f"Verdict: {verdict} ({route})")

        return {
            "verdict": verdict,
            "confidence": f"{final_confidence:.2%}",
            "logic_route": route,
            "metadata": {
                "cleaned_text": clean_text,
                "domain_age_days": intel_report.get("age"),
                "rf_raw": f"{rf_prob:.4f}",
                "bert_raw": f"{deep_prob:.4f}"
            }
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return {"error": str(e)}