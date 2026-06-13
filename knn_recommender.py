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
scaled_data = scaler.fit_transform(df[features])

knn = NearestNeighbors(
    n_neighbors=6,
    metric="euclidean"
)

knn.fit(scaled_data)

def get_knn_recommendations(song_name=None):

    if song_name is None:
        song_name = df.iloc[0]["track_name"]

    song = df[
        df["track_name"].str.lower()
        == song_name.lower()
    ]

    if song.empty:
        song = df.iloc[[0]]

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
            "popularity": df.iloc[i]["popularity"]
        })

    return recommendations

