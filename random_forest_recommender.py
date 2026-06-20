import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATASET = "spotify_dataset.csv"


def train_random_forest(
    top_tracks,
    top_artists
):

    df = pd.read_csv(DATASET)

    df["preference_score"] = 0

    spotify_tracks = [
        track["name"].lower()
        for track in top_tracks
    ]

    spotify_artists = [
        artist["name"].lower()
        for artist in top_artists
    ]

    # Top tracks get stronger weight

    df.loc[
        df["track_name"]
        .str.lower()
        .isin(spotify_tracks),
        "preference_score"
    ] += 2

    # Favourite artists get smaller weight

    for artist_name in spotify_artists:

        df.loc[
            df["artists"]
            .str.lower()
            .str.contains(
                artist_name,
                na=False
            ),
            "preference_score"
        ] += 1

    df["liked"] = (
        df["preference_score"] > 0
    ).astype(int)

    features = [
        "danceability",
        "energy",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "popularity"
    ]

    X = df[features]

    y = df["liked"]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )

    model.fit(X, y)

    return model, df


def get_rf_recommendations(
    top_tracks,
    top_artists
):

    model, df = train_random_forest(
        top_tracks,
        top_artists
    )

    features = [
        "danceability",
        "energy",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "popularity"
    ]

    scores = model.predict_proba(
        df[features]
    )[:, 1]

    df["score"] = scores

    spotify_tracks = [
        track["name"].lower()
        for track in top_tracks
    ]

    candidate_songs = df[
        ~df["track_name"]
        .str.lower()
        .isin(spotify_tracks)
    ]

    candidate_songs = candidate_songs.sort_values(
        "score",
        ascending=False
    )

    recommendations = []

    used_artists = set()

    for _, row in candidate_songs.iterrows():

        artist = row["artists"]

        # Prevent artist spam

        if artist in used_artists:
            continue

        recommendations.append({
            "track_name": row["track_name"],
            "artists": artist,
            "track_genre": row["track_genre"],
            "popularity": int(row["popularity"])
        })

        used_artists.add(artist)

        if len(recommendations) == 10:
            break

    return recommendations