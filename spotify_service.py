from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from config import config


class SpotifyAPIError(RuntimeError):
    pass


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("utf-8")


def build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": config.SPOTIFY_CLIENT_ID,
        "scope": config.SCOPES,
        "redirect_uri": config.SPOTIFY_REDIRECT_URI,
        "state": state,
        "show_dialog": "true",
    }
    return f"{config.SPOTIFY_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> Dict[str, Any]:
    headers = {
        "Authorization": _basic_auth_header(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.SPOTIFY_REDIRECT_URI,
    }
    response = requests.post(config.SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=15)
    if response.status_code != 200:
        raise SpotifyAPIError(f"Token exchange failed: {response.status_code} {response.text}")
    return response.json()


def _spotify_get(path: str, access_token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.get(
        f"{config.SPOTIFY_API_BASE}{path}",
        headers={"Authorization": f"Bearer {access_token}"},
        params=params,
        timeout=15,
    )
    if response.status_code != 200:
        raise SpotifyAPIError(f"GET {path} failed: {response.status_code} {response.text}")
    return response.json()


def fetch_profile(access_token: str) -> Dict[str, Any]:
    return _spotify_get("/me", access_token)


def fetch_top_tracks(access_token: str, limit: int = 10, time_range: str = "medium_term") -> List[Dict[str, Any]]:
    return _spotify_get("/me/top/tracks", access_token, {"limit": limit, "time_range": time_range}).get("items", [])


def fetch_top_artists(access_token: str, limit: int = 10, time_range: str = "medium_term") -> List[Dict[str, Any]]:
    return _spotify_get("/me/top/artists", access_token, {"limit": limit, "time_range": time_range}).get("items", [])


def fetch_recently_played(access_token: str, limit: int = 10) -> List[Dict[str, Any]]:
    return _spotify_get("/me/player/recently-played", access_token, {"limit": limit}).get("items", [])


def fetch_currently_playing(access_token: str) -> Optional[Dict[str, Any]]:
    response = requests.get(
        f"{config.SPOTIFY_API_BASE}/me/player/currently-playing",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if response.status_code == 204:
        return None
    if response.status_code != 200:
        raise SpotifyAPIError(f"Currently playing failed: {response.status_code} {response.text}")
    return response.json()


def fetch_audio_features(access_token: str, track_ids: List[str]) -> List[Dict[str, Any]]:
    track_ids = [tid for tid in track_ids if tid]
    if not track_ids:
        return []
    data = _spotify_get("/audio-features", access_token, {"ids": ",".join(track_ids)})
    return [item for item in data.get("audio_features", []) if item]


def fetch_recommendations(
    access_token: str,
    seed_tracks: List[str],
    seed_artists: List[str],
    target_features: Optional[Dict[str, float]] = None,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {"limit": limit}
    if seed_tracks:
        params["seed_tracks"] = ",".join(seed_tracks[:5])
    if seed_artists:
        params["seed_artists"] = ",".join(seed_artists[:5])
    if target_features:
        for key, value in target_features.items():
            params[f"target_{key}"] = round(float(value), 3)

    data = _spotify_get("/recommendations", access_token, params)
    return data.get("tracks", [])

def fetch_artist(access_token: str, artist_id: str) -> Dict[str, Any]:
    return _spotify_get(f"/artists/{artist_id}", access_token)


def fetch_track(access_token: str, track_id: str) -> Dict[str, Any]:
    return _spotify_get(f"/tracks/{track_id}", access_token)


def get_track_image(
    access_token,
    track_name,
    artist_name
):
    import requests

    url = "https://api.spotify.com/v1/search"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "q": f"track:{track_name} artist:{artist_name}",
        "type": "track",
        "limit": 1
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    if response.status_code != 200:
        return ""

    data = response.json()

    items = (
        data.get("tracks", {})
        .get("items", [])
    )

    if not items:
        return ""

    images = (
        items[0]
        .get("album", {})
        .get("images", [])
    )

    if not images:
        return ""

    return images[0]["url"]