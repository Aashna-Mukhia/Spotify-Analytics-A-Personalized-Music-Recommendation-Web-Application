import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATASET = "spotify_dataset.csv"


def train_random_forest(top_tracks):

    df = pd.read_csv(DATASET)

    df["liked"] = 0

    spotify_track_names = [
        track["name"].lower()
        for track in top_tracks
    ]

    df.loc[
        df["track_name"]
        .str.lower()
        .isin(spotify_track_names),
        "liked"
    ] = 1

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
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model, df


def get_rf_recommendations(top_tracks):

    model, df = train_random_forest(
        top_tracks
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

    spotify_track_names = [
        track["name"].lower()
        for track in top_tracks
    ]

    recommendations = (
        df[
            ~df["track_name"]
            .str.lower()
            .isin(spotify_track_names)
        ]
        .sort_values(
            "score",
            ascending=False
        )
        .head(10)
    )

    return recommendations[
        [
            "track_name",
            "artists",
            "track_genre",
            "popularity"
        ]
    ].to_dict("records")