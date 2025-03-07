from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from training2 import detect_mood  # Import the updated function from training.py

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["diary_db"]
entries_collection = db["entries"]

@app.route("/add_entry", methods=["POST"])
def add_entry():
    data = request.json
    entry_text = data.get("entry", "")
    
    if not entry_text:
        return jsonify({"error": "Entry cannot be empty"}), 400

    # Detect mood using the fine-tuned BERT model
    mood = detect_mood(entry_text)

    # Save entry with detected mood
    entry_data = {
        "date": datetime.utcnow().date().isoformat(),
        "entry": entry_text,
        "mood": mood,
        "timestamp": datetime.utcnow()
    }
    entries_collection.insert_one(entry_data)

    return jsonify({"message": "Entry saved!", "mood": mood})

@app.route("/get_weekly_moods", methods=["GET"])
def get_weekly_moods():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=6)

    # Fetch the last 7 days' entries
    entries = entries_collection.find({"date": {"$gte": week_ago.isoformat()}})
    
    # Organize data (if multiple entries exist for the same date, you might consider aggregating)
    mood_data = {}
    for entry in entries:
        # For simplicity, we're storing the last mood of the day
        mood_data[entry["date"]] = entry["mood"]

    return jsonify(mood_data)

if __name__ == "__main__":
    app.run(debug=True)
