# Spotify Analytics

A simple Flask web app that uses Spotify OAuth 2.0 to show a user's top tracks, top artists, listening insights, and personalized recommendations.

## Features
- Spotify OAuth login
- Top tracks and top artists
- Taste profile charts and Favorite Genres chart with Chart.js
- Listening insights
- Personalized KNN and Random Forest recommendations based on listening history

## Run locally
1. Create a Spotify app in the Spotify Developer Dashboard.
2. Add the redirect URI exactly as:
   `http://127.0.0.1:5000/callback`
3. Make a `.env` file and fill in your values.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run:
   `python app.py`

## Notes
- This app uses the Spotify Authorization Code flow.
- The redirect URI and spotify SECRET must match the Spotify app settings exactly.
- User top items require the `user-top-read` scope.
