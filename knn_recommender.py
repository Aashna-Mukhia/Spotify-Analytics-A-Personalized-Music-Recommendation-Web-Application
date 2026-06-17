import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("spotify_dataset.csv")

features = [
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

df = df.dropna(subset=features)

scaler = StandardScaler()

scaled_data = scaler.fit_transform(
    df[features]
)

knn = NearestNeighbors(
    n_neighbors=6,
    metric="euclidean"
)

knn.fit(scaled_data)


def get_knn_recommendations(top_tracks):

    if not top_tracks:
        return []

    spotify_song = top_tracks[0]["name"]

    song = df[
        df["track_name"].str.lower()
        == spotify_song.lower()
    ]

    if song.empty:
        return []

    song_index = song.index[0]

    distances, indices = knn.kneighbors(
        [scaled_data[song_index]]
    )

    recommendations = []

    for i in indices[0][1:]:

        recommendations.append({
            "track_name": df.iloc[i]["track_name"],
            "artists": df.iloc[i]["artists"],
            "track_genre": df.iloc[i]["track_genre"],
            "popularity": int(df.iloc[i]["popularity"])
        })

    return recommendations