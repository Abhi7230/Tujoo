import pandas as pd
import random
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
from training3 import detect_mood  # Ensure this imports your mood detection function
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://127.0.0.1:27017")
db = client["diaryAppDB"]
entries_collection = db["entries"]
@app.route("/get_recommendation", methods=["POST"])
def get_recommendation():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    entry_text = data.get("entry", "")
    if not entry_text:
        return jsonify({"error": "Entry cannot be empty"}), 400
    
    # Detect mood using your existing function
    mood = detect_mood(entry_text)
    
    # Make sure mood is lowercase for consistent matching
    mood = mood.lower()
    
    # Define fallback recommendations if file isn't found
    fallback_recommendations = {
        "sadness": ["Listen to calming music", "Take a walk in nature", "Call a friend"],
        "happiness": ["Celebrate with friends", "Practice gratitude", "Dance freely"],
        "anger": ["Try deep breathing exercises", "Go for a run", "Listen to relaxing music"],
        "neutral": ["Explore a new hobby", "Read an interesting book", "Go for a walk"],
        "love": ["Write a heartfelt message", "Spend time with loved ones", "Express gratitude"],
        "joy": ["Capture this moment in a journal", "Enjoy your favorite treat", "Share your happiness"],
        "fear": ["Talk to someone about your fear", "Practice deep breathing", "Write down your thoughts"],
        "surprise": ["Embrace the unexpected moment", "Share the surprise with a friend", "Take a deep breath"]
    }
    
    try:
        # Try to load the CSV file with absolute path
        import os
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recommendations.csv")
        
        if os.path.exists(file_path):
            recommendations_df = pd.read_csv(file_path)
            
            # Convert column and mood to lowercase for case-insensitive matching
            recommendations_df["Detected Mood"] = recommendations_df["Detected Mood"].str.lower()
            
            # Filter recommendations by detected mood
            mood_recommendations = recommendations_df[recommendations_df["Detected Mood"] == mood]
            
            if not mood_recommendations.empty:
                # Randomly select one recommendation
                recommendation = random.choice(mood_recommendations["Suggested Activity"].tolist())
            else:
                # Use fallback if mood not found in dataset
                recommendation = random.choice(fallback_recommendations.get(mood, ["Take some time for yourself today."]))
        else:
            # File doesn't exist, use fallback
            recommendation = random.choice(fallback_recommendations.get(mood, ["Take some time for yourself today."]))
    except Exception as e:
        print(f"Error fetching recommendation: {e}")
        # Use fallback recommendations if file can't be loaded
        recommendation = random.choice(fallback_recommendations.get(mood, ["Take some time for yourself today."]))
    
    return jsonify({"mood": mood, "recommendation": recommendation})

@app.route("/add_entry", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        # Support both JSON and form data submissions
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        entry_text = data.get("entry", "")
        if not entry_text:
            return jsonify({"error": "Entry cannot be empty"}), 400

        # Detect mood using the trained model
        mood = detect_mood(entry_text)

        # Save entry with detected mood; store date as ISO string ("YYYY-MM-DD")
        entry_data = {
            "date": datetime.now().date().isoformat(),  # e.g., "2025-02-21"
            "entry": entry_text,
            "mood": mood,
            "timestamp": datetime.now()  # Full timestamp if needed
        }
        result = entries_collection.insert_one(entry_data)

        return jsonify({"message": "Entry saved!", "mood": mood, "id": str(result.inserted_id)})
    return render_template("diaryentry1.html")

@app.route("/fetch-entry", methods=["GET"])
def fetch_entry():
    # Get the date from query parameters, expecting format 'YYYY-MM-DD'
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Date is required"}), 400

    try:
        # Validate the date format
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Query for entries matching the date (stored as ISO string)
    entries = list(entries_collection.find({"date": date_str}))
    for entry in entries:
        entry.pop('_id', None)  # Remove MongoDB _id field for JSON serialization
    return jsonify({"entries": entries})

@app.route("/get_weekly_moods", methods=["GET"])
def get_weekly_moods():
    # Define the mood-to-index mapping (order must match your moodLabels in mood.html)
    mood_to_index = {
        "sadness": 0,
        "happiness": 1,
        "anger": 2,
        "neutral": 3,
        "love": 4,
        "joy": 5,
        "fear": 6,
        "surprise": 7
    }
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    
    # Query for entries within the last 7 days
    entries = list(entries_collection.find({
        "date": {"$gte": week_ago.isoformat(), "$lte": today.isoformat()}
    }))
    
    # Aggregate mood indices by date (if multiple entries exist, average them)
    mood_sum = {}
    count = {}
    for entry in entries:
        date_val = entry.get("date")
        mood_str = entry.get("mood")
        if date_val and mood_str in mood_to_index:
            idx = mood_to_index[mood_str]
            mood_sum[date_val] = mood_sum.get(date_val, 0) + idx
            count[date_val] = count.get(date_val, 0) + 1

    # Prepare a list for the last 7 days in order with average mood index.
    result = []
    for i in range(7):
        d = week_ago + timedelta(days=i)
        d_str = d.isoformat()
        if d_str in mood_sum:
            avg_index = mood_sum[d_str] / count[d_str]
        else:
            avg_index = None  # or set to a default neutral value, e.g., 3
        result.append({
            "date": d_str,
            "mood_index": avg_index
        })
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
