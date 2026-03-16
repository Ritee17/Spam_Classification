import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, '../data/master_dataset.csv')
model_path = os.path.join(base_path, '../models/sentry_model.pkl')
vec_path = os.path.join(base_path, '../models/tfidf_vectorizer.pkl')

print("🚀 Retraining Sentry Brain with N-gram Intelligence...")

df = pd.read_csv(data_path)

# Upgrade: ngram_range=(1,2) picks up "lottery winner" or "bank account"
tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
X = tfidf.fit_transform(df['text'])
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=150, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, model_path)
joblib.dump(tfidf, vec_path)

print(f"✅ Best-in-class model saved. Accuracy: {model.score(X_test, y_test):.2%}")