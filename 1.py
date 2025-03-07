import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertModel
from torch.utils.data import DataLoader, Dataset

# Load dataset
df = pd.read_csv("recommendations.csv")

# Encode moods as numerical labels
mood_labels = {mood: i for i, mood in enumerate(df["Detected Mood"].unique())}
df["Mood Label"] = df["Detected Mood"].map(mood_labels)

# Load BERT tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define dataset class
class DiaryDataset(Dataset):
    def __init__(self, entries, labels):
        self.entries = entries
        self.labels = labels

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        text = self.entries[idx]
        label = self.labels[idx]
        inputs = tokenizer(text, padding="max_length", truncation=True, max_length=64, return_tensors="pt")
        return {key: val.squeeze(0) for key, val in inputs.items()}, torch.tensor(label)

# Split dataset
train_texts, test_texts, train_labels, test_labels = train_test_split(df["Diary Entry"], df["Mood Label"], test_size=0.2, random_state=42)

# Create DataLoaders
train_dataset = DiaryDataset(train_texts.tolist(), train_labels.tolist())
test_dataset = DiaryDataset(test_texts.tolist(), test_labels.tolist())

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

# Define BERT-based model
class MoodClassifier(nn.Module):
    def __init__(self):
        super(MoodClassifier, self).__init__()
        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.fc = nn.Linear(768, len(mood_labels))  # Output size = number of moods

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        return self.fc(outputs.pooler_output)

# Initialize model, optimizer, and loss function
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MoodClassifier().to(device)
optimizer = optim.Adam(model.parameters(), lr=2e-5)
criterion = nn.CrossEntropyLoss()

# Train the model
def train_model():
    model.train()
    for epoch in range(5):  # Train for 5 epochs
        total_loss = 0
        for batch in train_loader:
            inputs, labels = batch
            input_ids, attention_mask = inputs["input_ids"].to(device), inputs["attention_mask"].to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
        print(f"Epoch {epoch + 1}: Loss = {total_loss / len(train_loader)}")

train_model()

# Save trained model
torch.save(model.state_dict(), "mood_classifier.pth")
print("Model training complete and saved as mood_classifier.pth!")

