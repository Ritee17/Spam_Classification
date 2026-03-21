import os
import csv

def setup():
    folders = ['data', 'models']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Folder created: {folder}")

    log_path = 'data/production_logs.csv'
    if not os.path.exists(log_path):
        with open(log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'sender', 'text', 'verdict', 'route'])
        print("✅ production_logs.csv initialized")

if __name__ == "__main__":
    setup()