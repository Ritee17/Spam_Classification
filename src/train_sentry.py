import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# 1. Path Handling (Moving up from src to data)
base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, '../data/master_dataset.csv')
model_save_path = os.path.join(base_path, '../models/sentry_model.pkl')
vec_save_path = os.path.join(base_path, '../models/tfidf_vectorizer.pkl')

print("🚀 Starting Production-Level Training...")

# 2. Load the Master Dataset
df = pd.read_csv(data_path)

# 3. Vectorization Upgrade: Using N-grams (1,2)
# This lets the model understand phrases like "Bank account" or "KYC update"
tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
X = tfidf.fit_transform(df['text'])
y = df['label']

# 4. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. The Production Model: Random Forest
# n_estimators=100 means 100 different decision trees voting on the result
# Add 'class_weight' to make the model focus more on the minority (Scam) class
model = RandomForestClassifier(
    n_estimators=150, 
    class_weight='balanced_subsample', # This auto-balances the 4800 vs 700 issue
    random_state=42, 
    n_jobs=-1
)
model.fit(X_train, y_train)

# 6. Evaluation
y_pred = model.predict(X_test)
print(f"🎯 Production Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\n📋 Full Classification Report:\n", classification_report(y_test, y_pred))

# 7. Save to the /models folder using the path variables defined at the top
joblib.dump(model, model_save_path)
joblib.dump(tfidf, vec_save_path) # Changed from hardcoded string to variable

print(f"✅ Production Brain saved to: {os.path.abspath(model_save_path)}")
print(f"✅ Vectorizer saved to: {os.path.abspath(vec_save_path)}")