from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import asyncio
from src.predict import extract_url
from src.investigator import investigate_url

app = FastAPI(title="Sentry AI Production API")

# --- Path Configuration ---
base_path = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_path, '../models/sentry_model.pkl'))
tfidf = joblib.load(os.path.join(base_path, '../models/tfidf_vectorizer.pkl'))

# Define the data format the API expects
class MessageRequest(BaseModel):
    text: str
    sender: str = "Unknown"

@app.post("/analyze")
async def analyze_message(request: MessageRequest):
    # 1. ML Analysis
    data = tfidf.transform([request.text])
    prob_scam = float(model.predict_proba(data)[0][1])
    
    verdict = "SAFE"
    reason = "ML confidence low"

    with open("data/api_logs.csv", "a") as f:
        f.write(f"{request.sender},{request.text},{verdict}\n")

    # 2. Multi-Stage Logic
    if prob_scam > 0.85:
        verdict = "SCAM"
        reason = "High-confidence textual match"
    
    elif prob_scam > 0.35:
        url = extract_url(request.text)
        if url:
            report = await investigate_url(url)
            if report.get("is_malicious"):
                verdict = "SCAM"
                reason = f"Agent flagged link: {report.get('reason', 'Malicious content')}"
            else:
                verdict = "SAFE"
                reason = "Agent cleared the link destination"
        else:
            verdict = "SUSPICIOUS"
            reason = "Suspicious text patterns found"

    return {
        "message": request.text,
        "verdict": verdict,
        "confidence": f"{prob_scam:.2%}",
        "reason": reason
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)