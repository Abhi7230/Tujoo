import pandas as pd
import random

# Define moods and activities with detailed recommendations
mood_activities = {
    "Sadness": [
        "Listen to calming music and allow yourself to feel your emotions. Sometimes, soothing melodies can provide comfort and help process feelings.",
        "Write down your feelings in a journal, letting your thoughts flow freely. This can be a great way to release emotions and gain clarity.",
        "Watch a comforting movie that brings warmth and nostalgia, reminding you that difficult times will pass.",
        "Take a peaceful walk in nature, breathing in the fresh air and allowing the serenity of your surroundings to ease your mind.",
        "Call a friend or family member and open up about what you're feeling. Talking to someone who cares can provide support and perspective.",
        "Try meditation or mindfulness exercises to help ground yourself and bring a sense of calm to your thoughts.",
        "Engage in a creative hobby like painting, writing, or playing music to channel your emotions into something meaningful."
    ],
    "Happiness": [
        "Celebrate this joyful moment with friends or loved ones. Sharing happiness makes it even more special.",
        "Write about this moment in a gratitude journal, capturing the details of what made you happy so you can reflect on it later.",
        "Go for a fun outing—visit a favorite place, try a new activity, or simply enjoy being in the moment.",
        "Share your happiness on social media or with close friends, spreading positivity to others.",
        "Practice gratitude by listing things you're thankful for. Recognizing the good in life helps maintain long-term happiness.",
        "Listen to upbeat music and let yourself dance freely, embracing the joy in movement.",
        "Take time to do something you love, whether it's enjoying your favorite treat, playing a game, or watching a feel-good movie."
    ],
    "Anger": [
        "Try deep breathing exercises to regain control over your emotions. A few slow, deep breaths can help you feel centered.",
        "Go for a run or do an intense workout to release pent-up frustration in a healthy way.",
        "Write down your frustrations in a journal, allowing yourself to express everything without holding back.",
        "Listen to relaxing music to shift your focus away from anger and bring a sense of calm.",
        "Practice mindfulness by focusing on the present moment instead of dwelling on what made you angry.",
        "Vent to a trusted friend or family member who can listen and offer a different perspective.",
        "Engage in a calming activity like painting, reading, or playing an instrument to redirect your energy."
    ],
    "Neutral": [
        "Explore a new hobby or skill to add excitement to your routine. It’s a great time to learn something new!",
        "Read an interesting book that expands your knowledge and keeps your mind engaged.",
        "Try learning a new language, cooking a new recipe, or picking up a DIY project to challenge yourself.",
        "Go for a casual walk, enjoying the simplicity of the day without any rush.",
        "Watch an inspiring documentary to gain new perspectives and fuel your curiosity.",
        "Organize your workspace or living area for a fresh and productive environment.",
        "Plan your week ahead, setting goals that will bring structure and motivation."
    ],
    "Love": [
        "Write a heartfelt message to someone special, expressing your appreciation and affection.",
        "Spend quality time with loved ones, creating meaningful memories together.",
        "Express gratitude by acknowledging the small acts of love and kindness you receive.",
        "Do something kind for someone—small gestures go a long way in strengthening bonds.",
        "Reminisce on happy memories with loved ones, looking through old photos or sharing stories.",
        "Watch a romantic movie and enjoy the beauty of love stories.",
        "Surprise someone with a thoughtful gift or a handwritten letter, brightening their day."
    ],
    "Joy": [
        "Capture this moment in a journal, writing about what made you so happy today.",
        "Express gratitude for the joy you’re feeling, acknowledging the people and experiences that contributed to it.",
        "Enjoy your favorite treat as a small celebration of this wonderful moment.",
        "Plan a small celebration, even if it's just treating yourself to something nice.",
        "Sing your favorite song out loud, embracing the happiness within you.",
        "Share your happiness with others, spreading joy and positivity around you.",
        "Engage in a fun activity like playing a game, trying a new experience, or exploring creativity."
    ],
    "Fear": [
        "Talk to someone about your fear, sharing your worries and seeking reassurance.",
        "Practice deep breathing to calm your mind and reduce anxiety.",
        "Write down your thoughts, analyzing what’s causing your fear and how you can address it.",
        "Engage in positive affirmations, reminding yourself of your strengths and capabilities.",
        "Distract yourself with a light activity, like watching a comedy or reading an uplifting book.",
        "Listen to calming music to soothe your nerves and bring a sense of peace.",
        "Watch an uplifting movie that inspires hope and courage."
    ],
    "Surprise": [
        "Embrace the unexpected moment with an open mind, seeing it as an opportunity for growth.",
        "Write about how you feel, capturing the emotions and excitement of the surprise.",
        "Share the surprise with a friend, discussing how it impacted you.",
        "Take a deep breath and process the situation, allowing yourself to absorb the unexpected event.",
        "Celebrate a good surprise, whether it’s a kind gesture, unexpected news, or an exciting opportunity.",
        "Learn from an unexpected situation, taking valuable insights from surprises in life.",
        "Reflect on how surprises impact you, understanding your reactions and adaptability."
    ]
}

# Generating 500+ synthetic diary entries with longer content
diary_entries = []
for mood, activities in mood_activities.items():
    for _ in range(70):  # Generating approx. 70 diary entries per mood
        diary_entry = (
            f"{random.choice(['Lately, I have been reflecting a lot.', 'Today was an interesting day.', 'I find myself feeling', 'At this moment, I am experiencing'])} "
            f"{mood.lower()}. {random.choice(['It’s been a strange mix of emotions, and I am trying to navigate through it.', 'I’m not quite sure why, but these feelings have been lingering.', 'Life has its ups and downs, and I guess this is one of those phases.', 'Emotions can be tricky, but I hope to manage them well.'])} "
            f"{random.choice(['I know that taking care of myself is important, so I will try something that might help.', 'Finding balance is key, and I want to focus on that.', 'Acknowledging my emotions is the first step, and I am working on it.', 'It’s a learning process, but I want to embrace it.'])}"
        )
        suggested_activity = random.choice(activities)
        diary_entries.append([diary_entry, mood, suggested_activity])

# Convert to DataFrame
df = pd.DataFrame(diary_entries, columns=["Diary Entry", "Detected Mood", "Suggested Activity"])

# Save to CSV
df.to_csv("recommendations.csv", index=False)
print("Dataset with longer diary entries generated and saved as recommendations.csv")
