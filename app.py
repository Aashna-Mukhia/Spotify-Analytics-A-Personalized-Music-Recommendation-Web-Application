from __future__ import annotations

import json
import os
import secrets
import pandas as pd

from random_forest_recommender import get_rf_recommendations
from knn_recommender import get_knn_recommendations

from flask import Flask, flash, redirect, render_template, request, session, url_for

from analytics import (as_chart_labels_and_values, build_listening_insights, extract_audio_features_from_dataset, summarize_audio_features, extract_genres_from_dataset)

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
    get_track_image,
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

    try:
        dataset_df = pd.read_csv("spotify_dataset.csv")

        audio_features = extract_audio_features_from_dataset(
            top_tracks,
            dataset_df
        )

        print("Matched Tracks:", len(audio_features))

        audio_summary = summarize_audio_features(
            audio_features
        )

        print("Audio Summary:", audio_summary)

        genre_counts = extract_genres_from_dataset(
        top_tracks,
        dataset_df
        )

    except Exception as e:

        print("Audio Analysis Error:")
        print(e)

        audio_summary = {
            "danceability": 0.0,
            "energy": 0.0,
            "valence": 0.0,
            "acousticness": 0.0,
            "instrumentalness": 0.0,
            "speechiness": 0.0,
            "liveness": 0.0,
        }

    insights = build_listening_insights(
        audio_summary,
        top_artists,
        top_tracks
    )

    rf_recommendations = get_rf_recommendations(
        top_tracks,
        top_artists,
    )

    print(rf_recommendations[:2])

    for song in rf_recommendations:

        song["image_url"] = get_track_image(
            access_token,
            song["track_name"],
            song["artists"],
        )

    knn_recommendations = get_knn_recommendations(
        top_tracks,
        top_artists,
    )

    for song in knn_recommendations:

        song["image_url"] = get_track_image(
            access_token,
            song["track_name"],
            song["artists"]
        )

    mood = mood_label(audio_summary)

    labels, values = as_chart_labels_and_values(audio_summary)

    genre_labels = list(
        genre_counts.keys()
    )

    genre_values = list(
        genre_counts.values()
    )

    labels, values = as_chart_labels_and_values(audio_summary)

    print("GENRE COUNTS:")
    print(genre_counts)

    print("GENRE LABELS:")
    print(list(genre_counts.keys()))

    print("GENRE VALUES:")
    print(list(genre_counts.values()))

    chart_data = {
        "featureLabels": labels,
        "featureValues": values,

        "genreLabels": list(genre_counts.keys()),
        "genreValues": list(genre_counts.values()),
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
        genre_counts=genre_counts,
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
