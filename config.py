import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv(
        "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5000/callback")
    SPOTIFY_DEFAULT_TIME_RANGE: str = os.getenv(
        "SPOTIFY_DEFAULT_TIME_RANGE", "medium_term")
    SPOTIFY_AUTH_URL: str = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL: str = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE: str = "https://api.spotify.com/v1"
    SCOPES: str = "user-read-email user-read-private user-top-read user-read-currently-playing user-read-playback-state user-read-recently-played"


config = Config()
