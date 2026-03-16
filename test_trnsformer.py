from transformers import pipeline

print("⌛ Loading DistilBERT... (This might take a minute the first time)")
classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

test_text = "WINNER! You have won a free gift card. Click here to claim."
result = classifier(test_text)

print("\n🚀 Model is LIVE!")
print(f"Test Text: {test_text}")
print(f"Result: {result}")