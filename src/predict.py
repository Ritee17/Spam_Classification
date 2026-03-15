import joblib
import re
import os
# Module-style import for Production
try:
    from src.investigator import investigate_url
except ImportError:
    from investigator import investigate_url

# --- Path Configuration ---
base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, '../models/sentry_model.pkl')
vec_path = os.path.join(base_path, '../models/tfidf_vectorizer.pkl')

model = joblib.load(model_path)
tfidf = joblib.load(vec_path)

def extract_url(text):
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None

# (Keep the analyze_message_pipeline function as it was)