from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt

FEATURE_KEYS = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", "liveness"]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def summarize_audio_features(audio_features: List[Dict]) -> Dict[str, float]:
    summary = {}
    for key in FEATURE_KEYS:
        values = [float(item.get(key, 0.0)) for item in audio_features if item.get(key) is not None]
        summary[key] = round(mean(values), 3) if values else 0.0
    return summary


def build_genre_counts(top_artists: List[Dict]) -> Dict[str, int]:
    counter = Counter()
    for artist in top_artists:
        for genre in artist.get("genres", []):
            counter[genre] += 1
    return dict(counter.most_common(8))


def build_listening_insights(audio_summary: Dict[str, float], top_artists: List[Dict], top_tracks: List[Dict]) -> List[str]:
    insights: List[str] = []

    if not top_tracks:
        insights.append("No top tracks yet, so the dashboard is waiting for fresh listening data.")
        return insights

    if audio_summary.get("energy", 0) >= 0.65:
        insights.append("Your taste leans energetic, so high-tempo tracks will probably fit your vibe.")
    elif audio_summary.get("energy", 0) <= 0.4:
        insights.append("Your listening history looks calmer and more mellow overall.")
    else:
        insights.append("Your music taste sits in the middle, with a balanced energy profile.")

    if audio_summary.get("valence", 0) >= 0.6:
        insights.append("You seem to enjoy brighter, happier-sounding songs.")
    else:
        insights.append("You tend toward a more reflective or emotional sound palette.")

    if top_artists:
        first_artist = top_artists[0].get("name", "your top artist")
        insights.append(f"One of your strongest anchors right now is {first_artist}.")

    if len(top_tracks) >= 3:
        first_three = ", ".join(track.get("name", "") for track in top_tracks[:3] if track.get("name"))
        insights.append(f"Your top tracks right now include {first_three}.")

    return insights[:4]


def derive_target_features(audio_summary: Dict[str, float]) -> Dict[str, float]:
    return {
        "danceability": clamp(audio_summary.get("danceability", 0.5)),
        "energy": clamp(audio_summary.get("energy", 0.5)),
        "valence": clamp(audio_summary.get("valence", 0.5)),
        "acousticness": clamp(audio_summary.get("acousticness", 0.2)),
        "instrumentalness": clamp(audio_summary.get("instrumentalness", 0.05)),
        "speechiness": clamp(audio_summary.get("speechiness", 0.05)),
        "liveness": clamp(audio_summary.get("liveness", 0.2)),
    }


def as_chart_labels_and_values(feature_summary: Dict[str, float]) -> Tuple[List[str], List[float]]:
    labels = [k.replace("_", " ").title() for k in FEATURE_KEYS]
    values = [round(float(feature_summary.get(k, 0.0)), 3) for k in FEATURE_KEYS]
    return labels, values


def load_dataset():

    df = pd.read_csv("dataset.csv")

    return df



def dataset_summary():

    df = load_dataset()

    total_tracks = len(df)

    total_artists = df["artists"].nunique()

    total_genres = df["track_genre"].nunique()

    avg_popularity = round(df["popularity"].mean(),2)

    return {

        "total_tracks": total_tracks,

        "total_artists": total_artists,

        "total_genres": total_genres,

        "average_popularity": avg_popularity

    }



def top_genres():

    df = load_dataset()

    genres = df["track_genre"].value_counts().head(10)

    return genres.to_dict()



def top_danceable_songs():

    df = load_dataset()

    songs = (

        df[["track_name","artists","danceability"]]

        .sort_values(

            by="danceability",

            ascending=False

        )

        .head(10)

    )

    return songs.to_dict(orient="records")

import pandas as pd

def load_dataset():
    df = pd.read_csv("dataset.csv")
    return df

def dataset_summary():
    df = load_dataset()

    total_tracks = len(df)
    total_artists = df["artists"].nunique()
    total_genres = df["track_genre"].nunique()

    print("Total Tracks:", total_tracks)
    print("Total Artists:", total_artists)
    print("Total Genres:", total_genres)

    print("\nTop 10 Genres:")
    print(df["track_genre"].value_counts().head(10))

    print("\nTop 10 Popular Songs:")
    print(
        df[["track_name", "artists", "popularity"]]
        .sort_values(by="popularity", ascending=False)
        .head(10)
    )

if __name__ == "__main__":
    dataset_summary()
    
def genre_chart():

    df = load_dataset()

    avg_popularity = (
        df.groupby("track_genre")["popularity"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(14, 7))

    colors = [
        "#1DB954",
        "#1ED760",
        "#1AA34A",
        "#17C653",
        "#39D98A",
        "#7CE7AC",
        "#00C896",
        "#00B96B",
        "#16A34A",
        "#22C55E"
    ]

    bars = plt.bar(
        avg_popularity.index,
        avg_popularity.values,
        color=colors,
        edgecolor="white",
        linewidth=1.5
    )

    plt.title(
        "🎵 Top 10 Genres by Average Popularity",
        fontsize=18,
        fontweight="bold"
    )

    plt.xlabel(
        "Genre",
        fontsize=12
    )

    plt.ylabel(
        "Average Popularity",
        fontsize=12
    )

    plt.xticks(
        rotation=35,
        fontsize=11
    )

    plt.yticks(fontsize=11)

    plt.grid(
        axis='y',
        linestyle='--',
        alpha=0.3
    )

    for bar in bars:

        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.3,
            f"{height:.1f}",
            ha='center',
            fontsize=10
        )

    plt.xticks(rotation=35, ha='right')

    plt.tight_layout()

    plt.show()

def popularity_histogram():

    df = load_dataset()

    plt.figure(figsize=(11,6))

    plt.hist(
        df["popularity"],
        bins=20,
        color="#1DB954",
        edgecolor="black",
        alpha=0.85
    )

    plt.title(
        "🎵 Distribution of Spotify Song Popularity",
        fontsize=22,
        fontweight="bold"
    )

    plt.xlabel(
        "Popularity Score",
        fontsize=14
    )

    plt.ylabel(
        "Number of Songs",
        fontsize=14
    )

    plt.grid(
        linestyle="--",
        alpha=0.3
    )

    plt.tight_layout()

    plt.show()

def pie_chart():

    df = load_dataset()

    top_genres = (
        df.groupby("track_genre")["popularity"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )

    labels = top_genres.index
    sizes = top_genres.values

    colors = [
        "#1DB954",
        "#1ED760",
        "#17A74A",
        "#66D98F",
        "#A8F0C6"
    ]

    plt.figure(figsize=(8,8))

    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        shadow=True,
        explode=(0.05,0.05,0.05,0.05,0.05),
        wedgeprops={"edgecolor":"white","linewidth":2}
    )

    plt.title(
        "Top 5 Genres by Average Popularity",
        fontsize=18,
        fontweight="bold"
    )

    plt.tight_layout()

    plt.show()

if __name__ == "__main__":

    dataset_summary()

    genre_chart()

    popularity_histogram()

    pie_chart()