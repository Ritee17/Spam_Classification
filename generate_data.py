import pandas as pd
import random
import os

# Ensure data directory exists
if not os.path.exists('data'): 
    os.makedirs('data')

# --- 1. CORE VARIABLES FOR VARIETY ---
banks = ["SBI", "HDFC", "ICICI", "Axis", "Paytm", "Kotak"]
docs = ["KYC", "PAN", "Aadhar", "Verification"]
names = ["Shubhnag", "Ritee", "Aman", "Ravi", "Prof. Kumar"]
places = ["Room 541", "the Lab", "GLAU Campus", "Library", "GDG Room"]
subjects = ["NLP", "AIML", "IoT", "Blockchain", "Deep Learning", "Java", "Python"]
projects = ["Agentic Refactoring", "DNA-Diffusion", "Text Summarizer", "Churn Prediction"]
services = ["GitHub", "Zomato", "IRCTC", "Amazon", "Netflix"]

# --- 2. THE SCAMS (Label 1) ---
scam_templates = [
    "Your {bank} account is blocked. Update {doc} now to avoid suspension: {link}",
    "Earn ₹{amount} daily by liking YouTube videos. No experience needed! {link}",
    "Electricity bill overdue. Power will be cut at 9 PM tonight. Pay via: {link}",
    "WINNER! You won a ₹25 Lakhs lottery in KBC. WhatsApp your details to claim.",
    "Hi Mom, I lost my phone. Need ₹{amount} for an emergency. Send to UPI: 9876543210",
    "Selected for Amazon Part-time job. Earn ₹15,000/week. Join here: {link}",
    "Verify your {bank} credit card points before they expire tonight! {link}"
]

# --- 3. THE ENGINEERING & CAMPUS SAFE MESSAGES (Label 0) ---
# We are making this section heavy to stop the "False Positives"
engineering_safe_templates = [
    "Hey Ritee, did you check the Pull Request on GitHub for the {project}?",
    "Can you share the {subject} lab manual? I missed it in the GDG group.",
    "The {project} server is finally running on Ubuntu 22.04 in {place}.",
    "The documentation for the {subject} project is live on our GitHub repo.",
    "Ritee, Prof. Kumar is asking for the {project} status report by 5 PM.",
    "Are we meeting in {place} for the {subject} mini-project discussion?",
    "Check this technical debt audit report for our VS Code extension: {link}",
    "I've pushed the new GRU model for Next Word Prediction. Please review.",
    "Don't forget the GDG core team meeting today at {place}.",
    "Your OTP for {service} is {otp}. Valid for 10 minutes.",
    "Hey, the link for the Google Meet is: https://meet.google.com/abc-defg-hij",
    "Bro, send me the {subject} assignment. I'm in {place} right now."
]

data = []

# Generate 300 SCAMS (Label 1)
for _ in range(300):
    msg = random.choice(scam_templates).format(
        bank=random.choice(banks), 
        doc=random.choice(docs),
        link="https://bit.ly/"+str(random.randint(1000,9999)),
        amount=random.randint(2000, 10000)
    )
    data.append({"text": msg, "label": 1})

# Generate 500 SAFE MESSAGES (Label 0)
# We generate more Safe than Scam to create a 'Safe-Leaning' bias
for _ in range(500):
    msg = random.choice(engineering_safe_templates).format(
        name=random.choice(names), 
        place=random.choice(places),
        project=random.choice(projects), 
        subject=random.choice(subjects),
        service=random.choice(services), 
        otp=random.randint(1000, 9999),
        link="https://github.com/ritee/project-"+str(random.randint(1,50))
    )
    data.append({"text": msg, "label": 0})

df = pd.DataFrame(data)
df.to_csv("data/synthetic_scams_v2.csv", index=False)

print(f"✅ Data Generation Complete!")
print(f"📊 Total Synthetic Messages: {len(df)}")
print(f"💡 High-Volume Engineering context added to Label 0 (Safe).")