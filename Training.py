from transformers import TFBertForSequenceClassification, BertTokenizer
import tensorflow as tf

# Load the pre-trained model and tokenizer
model_name = "bert_sentiment_model"  # Path to the saved model
tokenizer = BertTokenizer.from_pretrained(model_name)

model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=8)


# Parameters
batch_size = 16
max_length = 128

# Label Mapping
label_mapping = {
    "sadness": 0,
    "happiness": 1,
    "anger": 2,
    "neutral": 3,
    "love": 4,
    "joy": 5,
    "fear": 6,
    "surprise": 7
}

# Load dataset function
def load_data(file_path):
    texts = []
    labels = []
    with open(file_path, "r") as file:
        for line in file:
            if ";" in line:  # Ensure valid formatting
                text, label = line.strip().split(";")
                texts.append(text)
                labels.append(label_mapping[label])  # Map label strings to integers
    return texts, labels

# Tokenize dataset
def encode_data(texts, labels):
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors="tf"
    )
    dataset = tf.data.Dataset.from_tensor_slices((dict(encodings), labels))
    return dataset

# Load and preprocess test data
test_texts, test_labels = load_data("test.txt")
test_dataset = encode_data(test_texts, test_labels).batch(batch_size)

# Evaluate on test data
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
metric_fn = tf.keras.metrics.SparseCategoricalAccuracy()

test_loss, test_accuracy = 0, 0
batch_count = 0
for batch_data, batch_labels in test_dataset:
    predictions = model(batch_data, training=False).logits
    batch_loss = loss_fn(batch_labels, predictions)
    batch_accuracy = metric_fn(batch_labels, predictions)
    test_loss += batch_loss
    test_accuracy += batch_accuracy
    batch_count += 1

# Calculate average loss and accuracy
test_loss /= batch_count
test_accuracy /= batch_count
print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")

# Predict new text (Optional)
new_text = ["I am feeling quite low today!"]
encoded_input = tokenizer(
    new_text,
    truncation=True,
    padding=True,
    max_length=max_length,
    return_tensors="tf"
)

# Get predictions
output = model(encoded_input)
predicted_class = tf.argmax(output.logits, axis=-1).numpy()[0]
label_mapping_reverse = {v: k for k, v in label_mapping.items()}
predicted_label = label_mapping_reverse[predicted_class]

print(f"New Text: {new_text[0]}")
print(f"Predicted Class: {predicted_class} ({predicted_label})")