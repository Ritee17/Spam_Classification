import pandas as pd
import os

def prepare_production_data():
    # Paths (Looking into the data folder from the root)
    uci_path = 'data/SMSSpamCollection'
    indian_path = 'data/synthetic_scams_v2.csv'
    output_path = 'data/master_dataset.csv'

    print("🛠️ Starting Data Merger...")

    # 1. Load UCI Data
    if os.path.exists(uci_path):
        real_df = pd.read_csv(uci_path, sep='\t', names=['label', 'text'])
        real_df['label'] = real_df['label'].map({'spam': 1, 'ham': 0})
    else:
        print(f"❌ Could not find {uci_path}")
        return

    # 2. Load Synthetic Indian Data
    if os.path.exists(indian_path):
        indian_df = pd.read_csv(indian_path)
    else:
        print(f"❌ Could not find {indian_path}")
        return

    # 3. Combine and Clean
    master_df = pd.concat([real_df, indian_df], ignore_index=True)
    
    # Remove duplicates (critical for production)
    before = len(master_df)
    master_df.drop_duplicates(subset=['text'], inplace=True)
    after = len(master_df)

    # 4. Save
    master_df.to_csv(output_path, index=False)
    
    print(f"✅ Master Dataset saved to {output_path}")
    print(f"📊 Total Samples: {after} (Cleaned {before - after} duplicates)")
    print(f"📈 Breakdown:\n{master_df['label'].value_counts()}")

if __name__ == "__main__":
    prepare_production_data()