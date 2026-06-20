from __future__ import annotations

import json
import os
import secrets

from random_forest_recommender import get_rf_recommendations
from knn_recommender import get_knn_recommendations

from flask import Flask, flash, redirect, render_template, request, session, url_for

from analytics import as_chart_labels_and_values, build_listening_insights
from config import config
from recommendation import mood_label
from spotify_service import (
    SpotifyAPIError,
    build_authorize_url,
    exchange_code_for_token,
    fetch_currently_playing,
    fetch_profile,
    fetch_recently_played,
    fetch_top_artists,
    fetch_top_tracks,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "access_token" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login")
def login():
    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        flash("Add your Spotify client ID and secret to the .env file first.", "error")
        return redirect(url_for("index"))

    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    return redirect(build_authorize_url(state))

@app.route("/callback")
def callback():

    print("STEP 1")

    error = request.args.get("error")
    if error:
        print("ERROR:", error)
        return redirect(url_for("index"))

    print("STEP 2")

    state = request.args.get("state")

    print("Received State:", state)
    print("Session State:", session.get("oauth_state"))

    if not state or state != session.get("oauth_state"):
        print("STATE FAILED")
        return redirect(url_for("index"))

    print("STEP 3")

    code = request.args.get("code")

    if not code:
        print("NO CODE")
        return redirect(url_for("index"))

    print("STEP 4")

    try:
        token_data = exchange_code_for_token(code)

        print("TOKEN RECEIVED")
        print(token_data)

    except Exception as e:

        print("TOKEN ERROR")
        print(e)

        return redirect(url_for("index"))

    print("STEP 5")

    session["access_token"] = token_data["access_token"]

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    access_token = session["access_token"]

    try:

        try:
            profile = fetch_profile(access_token)

            top_tracks = fetch_top_tracks(
                access_token,
                limit=10,
                time_range=config.SPOTIFY_DEFAULT_TIME_RANGE)

            top_artists = fetch_top_artists(
                access_token,
                limit=10,
                time_range=config.SPOTIFY_DEFAULT_TIME_RANGE
            )

            recently_played = fetch_recently_played(
                access_token,
                limit=10
            )

            currently_playing = fetch_currently_playing(
                access_token
            )

        except SpotifyAPIError as e:
            if "401" in str(e):
                session.clear()
                return redirect(url_for("login"))
            raise

    except Exception as e:

        print("FAILED HERE:")   
        print(e)

        raise

    audio_summary = {
        "danceability": 0.65,
        "energy": 0.72,
        "valence": 0.55,
        "acousticness": 0.30,
        "instrumentalness": 0.10,
        "speechiness": 0.08,
        "liveness": 0.18,
        "tempo": 120
    }

    insights = build_listening_insights(
        audio_summary,
        top_artists,
        top_tracks
    )

    rf_recommendations = get_rf_recommendations(
        top_tracks
    )

    knn_recommendations = get_knn_recommendations(
        top_tracks
    )

    mood = mood_label(audio_summary)

    labels, values = as_chart_labels_and_values(audio_summary)
    chart_data = {
        "featureLabels": labels,
        "featureValues": values,
    }

    return render_template(
        "dashboard.html",
        profile=profile,
        top_tracks=top_tracks,
        top_artists=top_artists,
        recently_played=recently_played,
        currently_playing=currently_playing,
        insights=insights,
        rf_recommendations=rf_recommendations,
        knn_recommendations=knn_recommendations,
        audio_summary=audio_summary,
        mood=mood,
        chart_data=json.dumps(chart_data),
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
