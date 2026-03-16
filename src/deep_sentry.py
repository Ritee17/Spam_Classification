from transformers import pipeline

# Load a pre-trained spam detection model
# This model is already 'fitted' on millions of messages
deep_analyzer = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

def get_deep_verdict(text):
    result = deep_analyzer(text)[0]
    # Returns something like {'label': 'spam', 'score': 0.99}
    return result