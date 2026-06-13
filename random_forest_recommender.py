import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATASET = "spotify_dataset.csv"


def train_random_forest():

    df = pd.read_csv(DATASET)

    df["liked"] = 0

    top_songs = df.nlargest(1000, "popularity")

    df.loc[top_songs.index, "liked"] = 1

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

def get_rf_recommendations():

    model, df = train_random_forest()

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
    )[:,1]

    df["score"] = scores

    recommendations = (
        df.sort_values(
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