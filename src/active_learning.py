import pandas as pd
import os
import subprocess

# Paths
base_path = os.path.dirname(__file__)
logs_path = os.path.join(base_path, '../data/production_logs.csv')
dataset_path = os.path.join(base_path, '../data/master_dataset.csv')

def run_active_learning():
    if not os.path.exists(logs_path):
        print("❌ No production logs found yet.")
        return

    # Load logs and dataset
    logs_df = pd.read_csv(logs_path)
    
    if logs_df.empty:
        print("📭 Logs are empty. Nothing to learn from.")
        return

    print(f"🧐 Found {len(logs_df)} production interactions.")
    print("Let's verify suspicious or low-confidence entries...\n")

    new_entries = []
    
    for index, row in logs_df.iterrows():
        # We focus on things the model wasn't 100% sure about
        print("-" * 50)
        print(f"Sender: {row['sender']}")
        print(f"Message: {row['message']}")
        print(f"AI Verdict: {row['verdict']} (Reason: {row['reason']})")
        
        user_input = input("Is this a SCAM? (y for Yes, n for No, s to Skip): ").lower()
        
        if user_input == 'y':
            new_entries.append({'text': row['message'], 'label': 1})
        elif user_input == 'n':
            new_entries.append({'text': row['message'], 'label': 0})
        
    if new_entries:
        # Append to Master Dataset
        new_data_df = pd.DataFrame(new_entries)
        new_data_df.to_csv(dataset_path, mode='a', header=False, index=False)
        print(f"\n✅ Added {len(new_entries)} new labeled examples to master_dataset.csv")
        
        # Clear the logs so we don't process them again
        open(logs_path, 'w').close() 
        with open(logs_path, 'w') as f:
            f.write("timestamp,sender,message,verdict,reason\n") # Re-write header
            
        # Trigger Retraining
        print("🔄 Triggering model retraining...")
        subprocess.run(["python3", os.path.join(base_path, "train_sentry.py")])
    else:
        print("\n👋 No changes made.")

if __name__ == "__main__":
    run_active_learning()