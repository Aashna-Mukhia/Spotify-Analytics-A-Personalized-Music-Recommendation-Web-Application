# Spotify Analytics

A simple Flask web app that uses Spotify OAuth 2.0 to show a user's top tracks, top artists, listening insights, and personalized recommendations.

## Features
- Spotify OAuth login
- Top tracks and top artists
- Taste profile charts with Chart.js
- Listening insights
- Personalized recommendations based on listening history

## Run locally
1. Create a Spotify app in the Spotify Developer Dashboard.
2. Add the redirect URI exactly as:
   `http://127.0.0.1:5000/callback`
3. Copy `.env.example` to `.env` and fill in your values.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run:
   `python app.py`

## Branch plan for the group
- `main`: only final stable code
- `dev`: integration branch
- `feature/auth-backend`: Prajwal
- `feature/ui-login-dashboard`: Abishank
- `feature/charts-visuals`: Labisha
- `feature/recommendations`: Aashna
- `feature/tests-qa`: Aayushka

## Merge flow
1. Everyone branches from `dev`
2. Each person commits only to their branch
3. Open pull requests into `dev`
4. After testing, merge `dev` into `main`

## Notes
- This app uses the Spotify Authorization Code flow.
- The redirect URI must match the Spotify app settings exactly.
- User top items require the `user-top-read` scope.
