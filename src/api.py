from datetime import datetime
import csv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
from src.predict import extract_url
from src.investigator import investigate_url

app = FastAPI(title="Sentry AI Production API")

# --- Load Models ---
base_path = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_path, '../models/sentry_model.pkl'))
tfidf = joblib.load(os.path.join(base_path, '../models/tfidf_vectorizer.pkl'))

class MessageRequest(BaseModel):
    text: str
    sender: str = "Unknown"

@app.get("/health")
def health():
    return {"status": "online", "server": "HP-Victus", "time": str(datetime.now())}

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    data = tfidf.transform([request.text])
    prob_scam = float(model.predict_proba(data)[0][1])
    
    verdict, reason = "SAFE", "Low scam confidence"

    if prob_scam > 0.85:
        verdict, reason = "SCAM", "High-confidence textual match"
    elif prob_scam > 0.35:
        url = extract_url(request.text)
        if url:
            report = await investigate_url(url)
            if report.get("is_malicious"):
                verdict, reason = "SCAM", f"Agent flagged: {report.get('reason')}"
            else:
                verdict, reason = "SAFE", "Agent cleared destination"
        else:
            verdict, reason = "SUSPICIOUS", "Bypassed Agent (No link found)"

    # --- THE PRODUCTION LOG ---
    log_file = os.path.join(base_path, '../data/production_logs.csv')
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'sender', 'message', 'verdict', 'reason'])
        writer.writerow([datetime.now(), request.sender, request.text.strip(), verdict, reason])

    return {"verdict": verdict, "confidence": f"{prob_scam:.2%}", "reason": reason}