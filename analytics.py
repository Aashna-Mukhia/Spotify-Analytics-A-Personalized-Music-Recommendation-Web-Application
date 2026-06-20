from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, List, Tuple

import pandas as pd


FEATURE_KEYS = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def extract_audio_features_from_dataset(
    top_tracks,
    dataset_df
):
    audio_features = []

    if dataset_df.empty:
        return audio_features

    dataset_df = dataset_df.copy()

    dataset_df["track_name_clean"] = (
        dataset_df["track_name"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    dataset_df["artist_clean"] = (
        dataset_df["artists"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    for track in top_tracks:

        track_name = (
            track.get("name", "")
            .lower()
            .strip()
        )

        artists = track.get("artists", [])

        artist_name = ""

        if artists:
            artist_name = (
                artists[0]
                .get("name", "")
                .lower()
                .strip()
            )

        match = dataset_df[
            (dataset_df["track_name_clean"] == track_name)
            &
            (dataset_df["artist_clean"].str.contains(artist_name, na=False))
        ]

        if match.empty:
            match = dataset_df[
                dataset_df["track_name_clean"] == track_name
            ]

        if match.empty:
            continue

        row = match.iloc[0]

        audio_features.append({
            feature: float(row.get(feature, 0))
            for feature in FEATURE_KEYS
        })

    return audio_features


def extract_genres_from_dataset(
    top_tracks,
    dataset_df
):
    genre_counter = Counter()

    if dataset_df.empty:
        return {}

    dataset_df = dataset_df.copy()

    dataset_df["track_name_clean"] = (
        dataset_df["track_name"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    for track in top_tracks:

        track_name = (
            track.get("name", "")
            .lower()
            .strip()
        )

        match = dataset_df[
            dataset_df["track_name_clean"] == track_name
        ]

        if match.empty:
            continue

        genre = match.iloc[0].get("track_genre")

        if pd.notna(genre):
            genre_counter[str(genre)] += 1

    return dict(
        genre_counter.most_common(8)
    )


def summarize_audio_features(
    audio_features: List[Dict]
) -> Dict[str, float]:

    summary = {}

    for key in FEATURE_KEYS:

        values = [
            float(item.get(key, 0))
            for item in audio_features
            if item.get(key) is not None
        ]

        summary[key] = round(mean(values), 3) if values else 0.0

    return summary


def build_listening_insights(
    audio_summary: Dict[str, float],
    top_artists: List[Dict],
    top_tracks: List[Dict]
) -> List[str]:

    insights = []

    if not top_tracks:
        return [
            "No top tracks available yet."
        ]

    energy = audio_summary.get("energy", 0)
    valence = audio_summary.get("valence", 0)
    acousticness = audio_summary.get("acousticness", 0)

    if energy >= 0.65:
        insights.append(
            "Your listening profile is highly energetic and upbeat."
        )
    elif energy <= 0.40:
        insights.append(
            "Your music taste leans toward relaxed and mellow tracks."
        )
    else:
        insights.append(
            "You enjoy a balanced mix of energetic and laid-back music."
        )

    if valence >= 0.60:
        insights.append(
            "You generally prefer positive and uplifting songs."
        )
    else:
        insights.append(
            "You tend to enjoy emotional or introspective music."
        )

    if acousticness >= 0.50:
        insights.append(
            "Acoustic and organic sounds appear frequently in your listening habits."
        )
    else:
        insights.append(
            "You seem to gravitate toward more produced and electronic sounds."
        )

    if top_artists:
        artist_name = top_artists[0].get("name", "your favorite artist")
        insights.append(
            f"Your strongest artist preference right now is {artist_name}."
        )

    return insights[:4]


def derive_target_features(
    audio_summary: Dict[str, float]
) -> Dict[str, float]:

    return {
        "danceability": clamp(audio_summary.get("danceability", 0)),
        "energy": clamp(audio_summary.get("energy", 0)),
        "valence": clamp(audio_summary.get("valence", 0)),
        "acousticness": clamp(audio_summary.get("acousticness", 0)),
        "instrumentalness": clamp(audio_summary.get("instrumentalness", 0)),
        "speechiness": clamp(audio_summary.get("speechiness", 0)),
        "liveness": clamp(audio_summary.get("liveness", 0)),
    }


def as_chart_labels_and_values(
    feature_summary: Dict[str, float]
) -> Tuple[List[str], List[float]]:

    labels = [
        key.replace("_", " ").title()
        for key in FEATURE_KEYS
    ]

    values = [
        round(float(feature_summary.get(key, 0)), 3)
        for key in FEATURE_KEYS
    ]

    return labels, values