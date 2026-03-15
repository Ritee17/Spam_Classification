import pandas as pd
import requests
import zipfile
import io
import os

def download_uci_data():
    if not os.path.exists('data'): os.makedirs('data')
    
    print("📡 Fetching UCI Spam Dataset...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
    
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('data')
    
    # UCI data is tab-separated and lacks headers
    df = pd.read_csv('data/SMSSpamCollection', sep='\t', names=['label', 'text'])
    
    # Convert labels: 'spam' -> 1, 'ham' -> 0
    df['label'] = df['label'].map({'spam': 1, 'ham': 0})
    
    df.to_csv('data/real_spam_base.csv', index=False)
    print(f"✅ Successfully downloaded {len(df)} real-world samples!")

if __name__ == "__main__":
    download_uci_data()