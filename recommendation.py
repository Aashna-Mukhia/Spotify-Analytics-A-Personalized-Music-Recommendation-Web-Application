from __future__ import annotations

from typing import Dict, List, Tuple

from analytics import derive_target_features
from spotify_service import fetch_recommendations


def choose_seeds(top_tracks: List[Dict], top_artists: List[Dict]) -> Tuple[List[str], List[str]]:
    seed_tracks = [track.get("id") for track in top_tracks[:5] if track.get("id")]
    seed_artists = [artist.get("id") for artist in top_artists[:5] if artist.get("id")]
    return seed_tracks, seed_artists


def build_recommendation_cards(recommended_tracks: List[Dict]) -> List[Dict]:
    cards = []
    for track in recommended_tracks:
        artists = ", ".join(artist.get("name", "") for artist in track.get("artists", []))
        cards.append(
            {
                "name": track.get("name", "Unknown track"),
                "artists": artists or "Unknown artist",
                "album": track.get("album", {}).get("name", "Unknown album"),
                "image": (track.get("album", {}).get("images") or [{}])[0].get("url", ""),
                "url": track.get("external_urls", {}).get("spotify", "#"),
                "popularity": track.get("popularity", 0),
            }
        )
    return cards


def generate_recommendations(access_token: str, top_tracks: List[Dict], top_artists: List[Dict], audio_summary: Dict[str, float]) -> List[Dict]:
    seed_tracks, seed_artists = choose_seeds(top_tracks, top_artists)
    target_features = derive_target_features(audio_summary)
    try:
        raw = fetch_recommendations(
            access_token=access_token,
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            target_features=target_features,
            limit=8,
        )
    except Exception as e:
        print("Recommendations unavailable:", e)
        raw = []
    if not raw:
        return []
    
    return build_recommendation_cards(raw)


def mood_label(audio_summary: Dict[str, float]) -> str:
    energy = audio_summary.get("energy", 0.0)
    valence = audio_summary.get("valence", 0.0)
    if energy >= 0.65 and valence >= 0.55:
        return "Bright & Hype"
    if energy >= 0.65:
        return "High-Energy"
    if valence >= 0.6:
        return "Warm & Happy"
    if energy <= 0.4 and valence <= 0.45:
        return "Soft & Reflective"
    return "Balanced Mix"
