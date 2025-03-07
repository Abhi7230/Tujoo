from transformers import TFBertForSequenceClassification, BertTokenizer
import tensorflow as tf

# Load the pre-trained model and tokenizer
model_name = "bert_sentiment_model"  # Path to your saved model
tokenizer = BertTokenizer.from_pretrained(model_name)
model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=8)

# Label Mapping
label_mapping = {
    0: "sadness",
    1: "happiness",
    2: "anger",
    3: "neutral",
    4: "love",
    5: "joy",
    6: "fear",
    7: "surprise"
}

def detect_mood(text):
    """Predicts the mood of a given text using the trained BERT model."""
    encoded_input = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="tf"
    )
    
    # Get predictions
    output = model(encoded_input)
    predicted_class = tf.argmax(output.logits, axis=-1).numpy()[0]
    
    return label_mapping.get(predicted_class, "unknown")  # Return detected mood

if __name__ == "__main__":
    user_text = input("Enter a diary entry: ")
    mood = detect_mood(user_text)
    print(f"Detected Mood: {mood}")
