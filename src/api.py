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
import httpx
from collections import defaultdict
from unidecode import unidecode
from transformers import pipeline

app = FastAPI(title="Sentry AI: Final Competition Build")

# --- 1. Global Assets & Models ---
base_path = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_path, '../models/sentry_model.pkl'))
tfidf = joblib.load(os.path.join(base_path, '../models/tfidf_vectorizer.pkl'))
deep_sentry = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

from src.predict import extract_url

user_history = defaultdict(list)

class MessageRequest(BaseModel):
    text: str
    sender: str = "Unknown"

# --- 2. Advanced Security Logic ---

async def trace_url_chain(initial_url: str):
    """Tracer: Follows redirects to find the real destination."""
    if not initial_url.startswith(("http://", "https://")):
        initial_url = "https://" + initial_url
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(follow_redirects=True, timeout=5.0, headers=headers) as client:
            response = await client.get(initial_url)
            return str(response.url), len(response.history)
    except Exception:
        return initial_url, 0

def normalize_text(text: str):
    """Adversarial Shield: Detects and fixes 'Leet-speak'."""
    original = text.lower()
    text_decoded = unidecode(text).lower()
    replacements = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b'}
    for char, rep in replacements.items():
        text_decoded = text_decoded.replace(char, rep)
    
    clean_text = re.sub(r'(?<=[\w])[.!-](?=[\w])', '', text_decoded)
    return clean_text, (original != clean_text)

async def audit_domain_age(url: str):
    """Infrastructure Intelligence: Checks if domain is a Zero-Day threat."""
    try:
        domain = url.split("//")[-1].split("/")[0]
        # Hardcoded safe list for demo speed
        if any(d in domain for d in ["google.com", "github.com", "microsoft.com", "apple.com"]):
            return {"is_new": False, "age": 5000}
            
        loop = asyncio.get_event_loop()
        w = await loop.run_in_executor(None, whois.whois, domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list): creation_date = creation_date[0]
        
        if creation_date:
            days_old = (datetime.now() - creation_date).days
            return {"is_new": days_old < 30, "age": days_old}
        return {"is_new": True, "age": "Unverifiable"} # Fail-Shut: If we can't find it, assume it's new/shady
    except:
        return {"is_new": True, "age": "Lookup Failed"} # Fail-Shut

# --- 3. Core Analysis Endpoint ---

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    try:
        clean_text, detected_tricks = normalize_text(request.text)
        url = extract_url(request.text)
        
        # Stage 1: AI Inference
        data = tfidf.transform([clean_text])
        rf_prob = float(model.predict_proba(data)[0][1])
        
        loop = asyncio.get_event_loop()
        deep_res = await loop.run_in_executor(None, lambda: deep_sentry(clean_text)[0])
        is_scam_label = "LABEL_0" in deep_res['label']
        deep_prob = deep_res['score'] if is_scam_label else (1 - deep_res['score'])
        
        final_confidence = (rf_prob * 0.3) + (deep_prob * 0.7)
        route = "Hybrid Ensemble"

        # Stage 2: Adversarial & Intent Filters
        if detected_tricks:
            final_confidence = min(1.0, final_confidence + 0.3)
            route += " + Adversarial Detection"

        safe_keywords = ['meeting', 'timing', 'lunch', 'dinner', 'project', 'class', 'homework', 'bro', 'buddy', 'event']
        if any(word in clean_text for word in safe_keywords) and not url:
            final_confidence *= 0.2
            route += " + Casual Intent Filter"

        # Stage 3: THE HARD OVERRIDE (Infrastructure Kill-Shot)
        intel = {"is_new": False, "age": "N/A", "hops": 0, "final_url": "N/A"}
        if url:
            final_dest, hops = await trace_url_chain(url)
            age_data = await audit_domain_age(final_dest)
            intel.update(age_data)
            intel["final_url"], intel["hops"] = final_dest, hops
            
            # CRITICAL: If the domain is new OR lookup failed OR hops detected
            if intel["is_new"] or hops >= 1:
                final_confidence = 1.0 
                route += " + Infrastructure Kill-Shot"

        # Final Verdict Decision
        if final_confidence >= 0.60: verdict = "SCAM"
        elif final_confidence >= 0.35: verdict = "SUSPICIOUS"
        else: verdict = "SAFE"

        # Log Result
        with open(os.path.join(base_path, '../data/production_logs.csv'), 'a', newline='') as f:
            csv.writer(f).writerow([datetime.now(), request.sender, request.text, verdict, route])

        return {
            "verdict": verdict,
            "confidence": f"{final_confidence:.2%}",
            "analysis": {"logic_route": route, "redirect_hops": intel["hops"]},
            "metadata": {"final_dest": intel["final_url"], "domain_age": intel["age"]}
        }

    except Exception as e:
        return {"error": "Processing Failed", "details": str(e)}