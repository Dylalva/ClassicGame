# Firebase Setup Guide

This guide will walk you through setting up Firebase for the Donkey Kong Classic Game.

## Prerequisites

- Google account
- Firebase project access

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter project name: `classicgame-dk` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to **Authentication**
2. Click "Get started"
3. Go to **Sign-in method** tab
4. Enable the following providers:
   - **Email/Password**: Enable
   - **Google**: Enable and configure OAuth consent screen

### Google OAuth Configuration

1. Click on **Google** provider
2. Enable the toggle
3. Add your project support email
4. Save the configuration
5. Note down the **Web client ID** and **Web client secret**

## Step 3: Setup Realtime Database

1. Go to **Realtime Database** in Firebase Console
2. Click "Create Database"
3. Choose location (preferably closest to your users)
4. Start in **test mode** (you can secure it later)
5. Your database URL will be: `https://your-project-id-default-rtdb.firebaseio.com/`

## Step 4: Get Configuration Credentials

### Web API Key
1. Go to **Project Settings** (gear icon)
2. In the **General** tab, scroll to "Your apps"
3. If no web app exists, click "Add app" and select web (</>) icon
4. Register your app with a nickname
5. Copy the **API Key** from the config object

### Service Account (Optional - for admin operations)
1. Go to **Project Settings** > **Service accounts**
2. Click "Generate new private key"
3. Download the JSON file
4. Store it securely (never commit to version control)

## Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your credentials:
```env
# Firebase Configuration
FIREBASE_API_KEY=your_api_key_here
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Step 6: Database Structure

The game will automatically create the following structure in your Realtime Database:

```json
{
  "leaderboard": {
    "user_id_1": {
      "user_id": "user_id_1",
      "email": "player@example.com",
      "best_score": 1500,
      "timestamp": 1640995200
    }
  },
  "cloud_saves": {
    "user_id_1": {
      "save_data": {
        "level": 3,
        "score": 1200,
        "lives": 2
      },
      "last_updated": 1640995200
    }
  }
}
```

## Step 7: Security Rules (Production)

For production, update your Realtime Database rules:

```json
{
  "rules": {
    "leaderboard": {
      ".read": true,
      "$uid": {
        ".write": "$uid === auth.uid"
      }
    },
    "cloud_saves": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"API key not valid"**
   - Verify your API key in `.env`
   - Check if the API key is enabled for your project

2. **"Permission denied"**
   - Check your database security rules
   - Ensure user is authenticated

3. **"Network error"**
   - Verify your database URL
   - Check internet connection

### Testing Connection

Run this simple test to verify your Firebase connection:

```python
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Test database connection
database_url = os.getenv('FIREBASE_DATABASE_URL')
test_url = f"{database_url}/test.json"

try:
    response = requests.get(test_url)
    print(f"Connection successful: {response.status_code}")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Support

If you encounter issues:

1. Check the [Firebase Documentation](https://firebase.google.com/docs)
2. Verify all credentials are correctly set
3. Ensure your Firebase project has the necessary services enabled
4. Check the browser console for detailed error messages

## Security Best Practices

1. **Never commit** `.env` file to version control
2. **Use environment variables** for all sensitive data
3. **Implement proper security rules** for production
4. **Regularly rotate** API keys and secrets
5. **Monitor usage** in Firebase Console