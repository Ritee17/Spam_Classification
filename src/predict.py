import joblib
import asyncio
import re
import os
# Ensure this import works; your investigator.py must be in the same src folder
try:
    from investigator import investigate_url
except ImportError:
    print("❌ Error: investigator.py not found in the src folder.")

# --- Path Configuration ---
base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, '../models/sentry_model.pkl')
vec_path = os.path.join(base_path, '../models/tfidf_vectorizer.pkl')

# --- Load Production Brain ---
try:
    model = joblib.load(model_path)
    tfidf = joblib.load(vec_path)
except FileNotFoundError:
    print(f"❌ Error: Model files not found at {model_path}. Did you run train_sentry.py?")
    exit()

def extract_url(text):
    """Finds the first URL in a string."""
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None

async def analyze_message_pipeline(text):
    # 1. Text Transformation
    data = tfidf.transform([text])
    
    # 2. ML Probability (Random Forest)
    # probabilities[0] is Safe (0), probabilities[1] is Scam (1)
    prob_scam = model.predict_proba(data)[0][1]
    
    print(f"\n--- 🛡️ Production Sentry Analysis ---")
    print(f"Message: {text}")
    print(f"Scam Confidence: {prob_scam:.2%}")

    # 3. Multi-Stage Decision Logic
    if prob_scam > 0.85:
        print("Verdict: 🚩 SCAM (High-Confidence Textual Match)")
    
    elif prob_scam > 0.35:
        print("Verdict: ⚠️ SUSPICIOUS - Deploying Investigator Agent...")
        url = extract_url(text)
        
        if url:
            # Trigger the Agent
            report = await investigate_url(url)
            
            # SAFE ACCESS: Use .get() to avoid KeyErrors if the agent crashed
            is_malicious = report.get("is_malicious", False)
            final_dest = report.get("final_url", url)
            reason = report.get("reason", "N/A")

            if is_malicious:
                print(f"FINAL VERDICT: 🚨 SCAM")
                print(f"Reason: Agent flagged destination or link failed ({reason})")
                print(f"Target: {final_dest}")
            else:
                print(f"FINAL VERDICT: ✅ SAFE")
                print(f"Reason: Agent cleared the destination: {final_dest}")
        else:
            # Suspicious text but no link to investigate
            print("FINAL VERDICT: ⚠️ UNCERTAIN (No link found to verify, proceed with caution)")
    
    else:
        print("Verdict: ✅ SAFE")

if __name__ == "__main__":
    print("Sentry Online. Ready for real-world testing.")
    while True:
        msg = input("\nEnter message to analyze (or 'exit'): ")
        if msg.lower() == 'exit':
            break
        if not msg.strip():
            continue
        # Run the async pipeline
        asyncio.run(analyze_message_pipeline(msg))