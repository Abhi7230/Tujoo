# from transformers import TFBertForSequenceClassification, BertTokenizer

# # Assuming you have a model trained or loaded already
# model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")  # Or your model path
# tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")  # Or your tokenizer path

# # Save the model and tokenizer to your desired path
# model.save_pretrained("./bert_sentiment_model")
# tokenizer.save_pretrained("./bert_sentiment_model")

from transformers import TFBertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments
import tensorflow as tf
import numpy as np

# Define model path
model_name = "bert_sentiment_model"

# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define label mapping
label_mapping = {
    "sadness": 0, "happiness": 1, "anger": 2, "neutral": 3,
    "love": 4, "joy": 5, "fear": 6, "surprise": 7
}

# Load dataset function
def load_data(file_path):
    texts, labels = [], []
    with open(file_path, "r") as file:
        for line in file:
            if ";" in line:  # Ensure valid formatting
                text, label = line.strip().split(";")
                texts.append(text)
                labels.append(label_mapping[label])
    return texts, np.array(labels)

# Load training data
train_texts, train_labels = load_data("train.txt")

# Tokenize dataset
train_encodings = tokenizer(
    train_texts, truncation=True, padding=True, max_length=128, return_tensors="tf"
)

# Convert to TensorFlow dataset
train_dataset = tf.data.Dataset.from_tensor_slices((dict(train_encodings), train_labels)).batch(16)

# Initialize the model with 8 labels
model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=8)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer=optimizer, loss=loss_fn, metrics=["accuracy"])

# Train the model
model.fit(train_dataset, epochs=3)  # Adjust epochs based on dataset size

# Save the trained model
model.save_pretrained(model_name)
tokenizer.save_pretrained(model_name)

print("✅ Model training complete and saved!")
