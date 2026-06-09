from __future__ import annotations

import json
import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

from analytics import as_chart_labels_and_values, build_genre_counts, build_listening_insights, summarize_audio_features
from config import config
from recommendation import generate_recommendations, mood_label
from spotify_service import (
    SpotifyAPIError,
    build_authorize_url,
    exchange_code_for_token,
    fetch_audio_features,
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
    error = request.args.get("error")
    if error:
        flash(f"Spotify login stopped with: {error}", "error")
        return redirect(url_for("index"))

    state = request.args.get("state")
    if not state or state != session.get("oauth_state"):
        flash("Login state did not match. Please try again.", "error")
        return redirect(url_for("index"))

    code = request.args.get("code")
    if not code:
        flash("No authorization code received from Spotify.", "error")
        return redirect(url_for("index"))

    try:
        token_data = exchange_code_for_token(code)
    except SpotifyAPIError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))

    session.pop("oauth_state", None)
    session["access_token"] = token_data["access_token"]
    session["refresh_token"] = token_data.get("refresh_token")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    access_token = session["access_token"]

    try:
        profile = fetch_profile(access_token)
        top_tracks = fetch_top_tracks(
            access_token, limit=10, time_range=config.SPOTIFY_DEFAULT_TIME_RANGE)
        top_artists = fetch_top_artists(
            access_token, limit=10, time_range=config.SPOTIFY_DEFAULT_TIME_RANGE)
        audio_features = fetch_audio_features(
            access_token, [track.get("id") for track in top_tracks[:5]])
        recently_played = fetch_recently_played(access_token, limit=10)
        currently_playing = fetch_currently_playing(access_token)
    except SpotifyAPIError as exc:
        flash(str(exc), "error")
        return redirect(url_for("logout"))

    audio_summary = summarize_audio_features(audio_features)
    genre_counts = build_genre_counts(top_artists)
    insights = build_listening_insights(audio_summary, top_artists, top_tracks)
    recommendations = generate_recommendations(
        access_token, top_tracks, top_artists, audio_summary)
    mood = mood_label(audio_summary)

    labels, values = as_chart_labels_and_values(audio_summary)
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
        recommendations=recommendations,
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
