const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient } = require('mongodb');
const path = require('path');

const app = express();
const PORT = 3000;

// MongoDB Connection
const MONGO_URI = 'mongodb://127.0.0.1:27017';
const DATABASE_NAME = 'diaryAppDB';

let db;
MongoClient.connect(MONGO_URI, { useUnifiedTopology: true })
    .then((client) => {
        db = client.db(DATABASE_NAME);
        console.log(`Connected to MongoDB: ${DATABASE_NAME}`);
    })
    .catch((err) => console.error('Failed to connect to MongoDB:', err));

// Middleware
app.use(bodyParser.json());
app.use(express.static(__dirname)); // Serve static files like HTML

// Serve HTML pages
app.get('/home.html', (req, res) => res.sendFile(path.join(__dirname, 'home.html')));
app.get('/diaryentry.html', (req, res) => res.sendFile(path.join(__dirname, 'diaryentry.html')));
app.get('/mood.html', (req, res) => res.sendFile(path.join(__dirname, 'mood.html')));

// Signup Endpoint
app.post('/signup', async (req, res) => {
    const { email, password, confirmPassword, profession, areaOfInterest } = req.body;
    if (!email || !password || !confirmPassword || password !== confirmPassword) {
        return res.status(400).json({ message: 'Invalid input or passwords do not match' });
    }
    try {
        const existingUser = await db.collection('users').findOne({ email });
        if (existingUser) return res.status(400).json({ message: 'User already exists' });
        await db.collection('users').insertOne({ email, password, profession, areaOfInterest });
        res.status(200).json({ message: 'Signup successful' });
    } catch (error) {
        console.error('Error during signup:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Login Endpoint
app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ success: false, message: 'Email and password are required' });
    try {
        const user = await db.collection('users').findOne({ email });
        if (!user || user.password !== password) return res.status(401).json({ success: false, message: 'Invalid email or password' });
        res.status(200).json({ success: true, message: 'Login successful' });
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).json({ success: false, message: 'Internal server error' });
    }
});

// Save Diary Entry
app.post('/saveEntry', async (req, res) => {
    const { date, entry } = req.body;
    if (!date || !entry) return res.status(400).json({ message: 'Date and entry content are required' });
    try {
        const result = await db.collection('entries').insertOne({ date: new Date(date), entry, timestamp: new Date() });
        res.status(200).json({ message: 'Entry saved successfully', entryId: result.insertedId });
    } catch (error) {
        console.error('Error saving entry:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Fetch Mood Data
app.get('/get_mood_data', async (req, res) => {
    try {
        const texts = [
            "I'm feeling really down and unmotivated lately.",
            "It's another tough day; everything feels overwhelming.",
            "I feel stuck in a loop of negativity.",
            "Life feels too hard, and I can't find the motivation.",
            "I'm exhausted and upset about so many things.",
            "It's hard to stay positive when everything feels wrong.",
            "Feeling low and uninspired; this week has been tough."
        ];
        const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        const mood_scores = texts.map(text => {
            const analysis = require('sentiment')(text);
            return Math.round((analysis.score + 1) * 5);
        });
        res.json({ labels: days, scores: mood_scores });
    } catch (error) {
        console.error('Error fetching mood data:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Start the server
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
