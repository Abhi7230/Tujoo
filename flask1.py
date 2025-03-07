# flask1.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
import random

app = Flask(__name__)
CORS(app)

# -------------------------------
# MongoDB Connection Setup
# -------------------------------
client = MongoClient("mongodb://127.0.0.1:27017")
db = client["diaryAppDB"]
users_collection = db["users"]
entries_collection = db["entries"]

# -------------------------------
# Load the Trained Mood Classifier
# -------------------------------
class MoodClassifier(nn.Module):
    def __init__(self, num_moods):
        super(MoodClassifier, self).__init__()
        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.fc = nn.Linear(768, num_moods)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        return self.fc(outputs.pooler_output)

# Set the number of moods as per your training (we assume 8 moods)
num_moods = 8
mood_classifier = MoodClassifier(num_moods)
# Load your trained mood detection model
mood_classifier.load_state_dict(torch.load("mood_classifier.pth", map_location=torch.device('cpu')))
mood_classifier.eval()

# Load the tokenizer that matches your training
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define a complete mood mapping (ensure this matches your training order)
mood_mapping = {
    0: "Sadness",
    1: "Happiness",
    2: "Anger",
    3: "Neutral",
    4: "Love",
    5: "Joy",
    6: "Fear",
    7: "Surprise"
}

# -------------------------------
# Real-Time Recommendation Function
# -------------------------------
def generate_recommendation(mood, area_of_interest, previous_entries):
    """
    Generates a personalized recommendation based on:
    - The detected mood
    - The user's area of interest
    - (Optional) Their previous diary entries (to adapt the message)
    """
    # Baseline recommendations for each mood:
    baseline = {
        "Sadness": "Maybe try listening to your favorite calming music or watch a comforting movie.",
        "Happiness": "Keep celebrating your happiness—sharing that joy with a friend might be great!",
        "Anger": "Take a deep breath, perhaps go for a short walk, or try a few relaxation techniques.",
        "Neutral": "You might enjoy exploring a new hobby or activity to spark some excitement.",
        "Love": "Consider expressing your feelings or spending quality time with someone special.",
        "Joy": "Your energy is contagious! Perhaps channel it into something creative.",
        "Fear": "Take a moment to reflect and consider talking to someone you trust about your worries.",
        "Surprise": "Embrace the unexpected—maybe try something new or spontaneous today."
    }
    # Add a history note if similar mood entries exist
    history_note = ""
    if previous_entries:
        history_note = " Also, based on your past experiences when you felt this way, you might consider similar activities."
    
    recommendation_text = baseline.get(mood, "Take a moment for yourself.")
    # Optionally, if the user's area of interest isn't mentioned, add it to the message.
    if area_of_interest and area_of_interest.lower() not in recommendation_text.lower():
        recommendation_text += f" Since you enjoy {area_of_interest}, perhaps you can incorporate that too."
    
    return recommendation_text + history_note

# -------------------------------
# Recommendation Endpoint
# -------------------------------
@app.route("/get_personalized_recommendation", methods=["POST"])
def get_personalized_recommendation():
    """
    Expects a JSON payload with:
      - "entry": the diary entry text
      - "email": the user's email
    """
    data = request.get_json()
    diary_entry = data.get("entry", "")
    email = data.get("email", "")
    
    if not diary_entry:
        return jsonify({"error": "Diary entry is required"}), 400
    if not email:
        return jsonify({"error": "User email is required"}), 400

    # Retrieve user details from MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    area_of_interest = user.get("areaOfInterest", "general")

    # Use the mood classifier to predict the mood from the diary entry
    inputs = tokenizer(diary_entry, padding="max_length", truncation=True, max_length=64, return_tensors="pt")
    with torch.no_grad():
        outputs = mood_classifier(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        predicted_idx = torch.argmax(outputs, dim=1).item()
    detected_mood = mood_mapping.get(predicted_idx, "Neutral")
    
    # Optionally, retrieve previous diary entries by this user with the same mood
    previous_entries = list(entries_collection.find({"user_email": email, "mood": detected_mood}))
    
    # Generate a personalized recommendation
    recommendation = generate_recommendation(detected_mood, area_of_interest, previous_entries)
    personalized_message = f"It's okay to feel {detected_mood.lower()}. {recommendation}"
    
    return jsonify({
        "mood": detected_mood,
        "recommendation": recommendation,
        "personalized_message": personalized_message
    })

# -------------------------------
# Run the Flask App on Port 5001
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)

