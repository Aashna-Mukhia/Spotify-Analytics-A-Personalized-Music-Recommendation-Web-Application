import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

DATASET = "spotify_dataset.csv"

df = pd.read_csv(DATASET)

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
    n_neighbors=30,
    metric="euclidean"
)

knn.fit(scaled_data)


def get_knn_recommendations(
    top_tracks,
    top_artists
):

    spotify_tracks = {
        track["name"].lower()
        for track in top_tracks
    }

    spotify_artists = [
        artist["name"]
        for artist in top_artists[:5]
    ]

    recommendations = []
    used_tracks = set()

    # ---------------------------------
    # STEP 1
    # One song from each favorite artist
    # ---------------------------------

    artist_song_tables = []

    for artist_name in spotify_artists:

        artist_songs = df[
            df["artists"]
            .str.lower()
            .str.contains(
                artist_name.lower(),
                na=False
            )
        ]

        artist_songs = artist_songs.sort_values(
            "popularity",
            ascending=False
        )

        artist_song_tables.append(
            artist_songs
        )

    round_num = 0

    while len(recommendations) < 5:

        added = False

        for artist_songs in artist_song_tables:

            if round_num >= len(artist_songs):
                continue

            row = artist_songs.iloc[round_num]

            track_name = str(
                row["track_name"]
            )

            if track_name.lower() in spotify_tracks:
                continue

            if track_name.lower() in used_tracks:
                continue

            used_tracks.add(
                track_name.lower()
            )

            recommendations.append({
                "track_name": track_name,
                "artists": row["artists"],
                "track_genre": row["track_genre"],
                "popularity": int(
                    row["popularity"]
                )
            })

            added = True

            if len(recommendations) >= 5:
                break

        if not added:
            break

        round_num += 1

    # ---------------------------------
    # STEP 2
    # KNN Similar Songs
    # ---------------------------------

    if top_artists:

        favorite_artist = top_artists[0]["name"]

        seed_songs = df[
            df["artists"]
            .str.lower()
            .str.contains(
                favorite_artist.lower(),
                na=False
            )
        ]

        if not seed_songs.empty:

            for _, seed_song in seed_songs.head(3).iterrows():

                song_index = seed_song.name

                distances, indices = knn.kneighbors(
                    [scaled_data[song_index]]
                )

                for i in indices[0]:

                    track_name = str(
                        df.iloc[i]["track_name"]
                    )

                    if track_name.lower() in spotify_tracks:
                        continue

                    if track_name.lower() in used_tracks:
                        continue

                    used_tracks.add(
                        track_name.lower()
                    )

                    recommendations.append({
                        "track_name": track_name,
                        "artists": df.iloc[i]["artists"],
                        "track_genre": df.iloc[i]["track_genre"],
                        "popularity": int(
                            df.iloc[i]["popularity"]
                        )
                    })

                    if len(recommendations) >= 10:
                        return recommendations

    return recommendations[:10]