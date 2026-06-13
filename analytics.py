from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, List, Tuple


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
        "speechiness": clamp(audio_summary.get("speechiness", 0.05)),
        "liveness": clamp(audio_summary.get("liveness", 0.2)),
    }


def as_chart_labels_and_values(feature_summary: Dict[str, float]) -> Tuple[List[str], List[float]]:
    labels = [k.replace("_", " ").title() for k in FEATURE_KEYS]
    values = [round(float(feature_summary.get(k, 0.0)), 3) for k in FEATURE_KEYS]
    return labels, values
