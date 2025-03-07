from transformers import TFBertForSequenceClassification, BertTokenizer
import tensorflow as tf

# Use your saved model directory
model_name = "bert_sentiment_model"  # Folder where your fine-tuned model is saved
tokenizer = BertTokenizer.from_pretrained(model_name)
model = TFBertForSequenceClassification.from_pretrained(model_name)

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
    """Predicts the mood of a given text using the fine-tuned BERT model."""
    # Tokenize the input text
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

# Removed the command-line input block so that detect_mood can be imported and used elsewhere.
