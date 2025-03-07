const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient, ObjectId } = require('mongodb');
const path = require('path');

const app = express();
const PORT = 3000;

// MongoDB Connection
const MONGO_URI = 'mongodb://127.0.0.1:27017';
const DATABASE_NAME = 'diaryAppDB';

let db;
MongoClient.connect(MONGO_URI, { useUnifiedTopology: true })
    .then(client => {
        db = client.db(DATABASE_NAME);
        console.log(`Connected to MongoDB: ${DATABASE_NAME}`);
    })
    .catch(err => {
        console.error('Failed to connect to MongoDB:', err);
        process.exit(1); // Stop the server if DB fails
    });

// Middleware
app.use(express.json()); // Parse JSON requests
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded data
app.use(express.static(__dirname)); // Serve static files like HTML

// Serve `home.html` after login
app.get('/home.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'home.html'));
});

// Serve `diaryentry.html`
app.get('/diaryentry.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'diaryentry.html'));
});

// Signup Endpoint
app.post('/signup', async (req, res) => {
  const { email, password, confirmPassword, profession, areaOfInterest, isAdmin } = req.body;

  console.log("Received Data:", req.body);  // Debugging step

  // Validate input
  if (!email || !password || !confirmPassword || !profession || !areaOfInterest) {
      return res.status(400).json({ message: 'All fields are required' });
  }

  if (password !== confirmPassword) {
      return res.status(400).json({ message: 'Passwords do not match' });
  }

  try {
      // Check if the user already exists
      const existingUser = await db.collection('users').findOne({ email });
      if (existingUser) {
          return res.status(400).json({ message: 'User already exists' });
      }

      // Set the user's role based on the isAdmin flag
      const role = isAdmin ? 'admin' : 'user';

      // Insert the new user into the database
      await db.collection('users').insertOne({ email, password, profession, areaOfInterest, role });
      res.status(200).json({ message: 'Signup successful' });
  } catch (error) {
      console.error('Error during signup:', error);
      res.status(500).json({ message: 'Internal server error' });
  }
});

// Fetch User Details Endpoint
app.get('/fetch-user', async (req, res) => {
    let { email } = req.query;

    if (!email) {
        return res.status(400).json({ message: 'Email is required' });
    }

    email = email.toLowerCase(); // Convert to lowercase for case-insensitive search

    try {
        const user = await db.collection('users').findOne(
            { email },
            { projection: { _id: 0, email: 1, profession: 1, areaOfInterest: 1, role: 1 } }
        );

        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }

        res.status(200).json(user);
    } catch (error) {
        console.error('Error fetching user details:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Login Endpoint
app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ success: false, message: 'Email and password are required' });
    }

    try {
        const user = await db.collection('users').findOne({ email });

        if (!user || user.password !== password) {
            return res.status(401).json({ success: false, message: 'Invalid email or password' });
        }

        res.status(200).json({ success: true, message: 'Login successful', role: user.role || 'user' });
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).json({ success: false, message: 'Internal server error' });
    }
});

// Fetch All Users (Admin Only)
app.get('/admin/users', async (req, res) => {
    try {
        const users = await db.collection('users').find({}).project({ password: 0 }).toArray(); // Exclude passwords
        res.status(200).json(users);
    } catch (error) {
        console.error('Error fetching users:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Delete a User (Admin Only)
app.delete('/admin/users/:email', async (req, res) => {
    const { email } = req.params;

    try {
        const result = await db.collection('users').deleteOne({ email });

        if (result.deletedCount === 0) {
            return res.status(404).json({ message: 'User not found' });
        }

        res.status(200).json({ message: 'User deleted successfully' });
    } catch (error) {
        console.error('Error deleting user:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Fetch All Diary Entries (Admin Only)
app.get('/admin/entries', async (req, res) => {
    try {
        const entries = await db.collection('entries').find({}).toArray();
        res.status(200).json(entries);
    } catch (error) {
        console.error('Error fetching entries:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Delete a Diary Entry (Admin Only)
app.delete('/admin/entries/:id', async (req, res) => {
    const { id } = req.params;

    try {
        const result = await db.collection('entries').deleteOne({ _id: new ObjectId(id) });

        if (result.deletedCount === 0) {
            return res.status(404).json({ message: 'Entry not found' });
        }

        res.status(200).json({ message: 'Entry deleted successfully' });
    } catch (error) {
        console.error('Error deleting entry:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Generate Reports (Admin Only)
app.get('/admin/reports', async (req, res) => {
    try {
        // Example: Fetch the number of users and entries
        const userCount = await db.collection('users').countDocuments();
        const entryCount = await db.collection('entries').countDocuments();

        res.status(200).json({
            userCount,
            entryCount,
            // Add more report data as needed
        });
    } catch (error) {
        console.error('Error generating reports:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Check if an entry exists for the given date
app.get('/checkEntry', async (req, res) => {
    const date = req.query.date;
    const searchDate = new Date(date);
    searchDate.setHours(0, 0, 0, 0);
    const nextDay = new Date(searchDate.getTime() + 24 * 60 * 60 * 1000);

    try {
        const existingEntry = await db.collection('entries').findOne({
            date: { $gte: searchDate, $lt: nextDay },
        });

        if (existingEntry) {
            res.json({ exists: true, entry: existingEntry.entry });
        } else {
            res.json({ exists: false });
        }
    } catch (error) {
        console.error('Error checking entry:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

app.post('/saveEntry', async (req, res) => {
    const { date, entry, user_email } = req.body;

    if (!date || !entry || !user_email) {
        return res.status(400).json({ message: 'Date, entry content, and user email are required' });
    }

    try {
        // Use the user's email to create a unique collection name
        const userCollection = db.collection(`entries_${user_email.replace(/[^a-zA-Z0-9]/g, '_')}`);

        // Save the new entry in the user's collection
        const result = await userCollection.insertOne({
            date: new Date(date),
            entry,
            timestamp: new Date(),
        });

        res.status(200).json({ message: 'Entry saved successfully', entryId: result.insertedId });
    } catch (error) {
        console.error('Error saving entry:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

app.post('/updateEntry', async (req, res) => {
    console.log('Update entry endpoint called');
    const { date, entry } = req.body;

    if (!date || !entry) {
        return res.status(400).json({ message: 'Date and entry content are required' });
    }

    try {
        const searchDate = new Date(date);
        searchDate.setHours(0, 0, 0, 0); // Normalize to midnight
        const nextDay = new Date(searchDate.getTime() + 24 * 60 * 60 * 1000);

        // Find the existing entry
        const existingEntry = await db.collection('entries').findOne({
            date: { $gte: searchDate, $lt: nextDay },
        });

        if (!existingEntry) {
            return res.status(404).json({ message: 'No entry found for the given date' });
        }

        console.log('Found existing entry:', existingEntry);

        // Avoid duplicating content
        const existingText = existingEntry.entry.trim();
        const newText = entry.trim();
        console.log('Existing entry:', existingText);
        console.log('New Text:', newText);
        // Check if the new text is already part of the existing text
        const updatedEntry = existingText.includes(newText)
            ? existingText
            : `${existingText} ${newText}`.trim();

        console.log('Updated Entry:', newText);

        // Delete the old entry
        const deleteResult = await db.collection('entries').deleteOne({
            _id: existingEntry._id, // Use unique _id to avoid errors
        });
        console.log(`Deleted entry with _id: ${existingEntry._id}`);

        if (deleteResult.deletedCount === 0) {
            return res.status(500).json({ message: 'Failed to delete the existing entry.' });
        }

        // Save the updated entry
        const insertResult = await db.collection('entries').insertOne({
            date: searchDate,
            entry: newText,
            timestamp: new Date(),
        });

        console.log('New entry saved with _id:', insertResult.insertedId);

        res.status(200).json({ message: 'Entry updated successfully', entry: updatedEntry });
    } catch (error) {
        console.error('Error updating entry:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Fetch Diary Entries Endpoint
app.get('/fetch-entry', async (req, res) => {
    const { date, user_email } = req.query;

    if (!date || !user_email) {
        return res.status(400).json({ message: 'Date and user email are required' });
    }

    try {
        const searchDate = new Date(date);
        if (isNaN(searchDate)) {
            return res.status(400).json({ message: 'Invalid date format' });
        }

        searchDate.setHours(0, 0, 0, 0);
        const nextDay = new Date(searchDate.getTime() + 24 * 60 * 60 * 1000);

        // Use the user's email to access their collection
        const userCollection = db.collection(`entries_${user_email.replace(/[^a-zA-Z0-9]/g, '_')}`);

        // Fetch entries for the specific user and date
        const entries = await userCollection.find({
            date: { $gte: searchDate, $lt: nextDay },
        }).project({ entry: 1, mood: 1, _id: 0 }).toArray();

        if (entries.length > 0) {
            res.json({ entries });
        } else {
            res.json({ entries: [] });
        }
    } catch (error) {
        console.error('Error fetching entries:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});