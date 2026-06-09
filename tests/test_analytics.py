from analytics import build_genre_counts, derive_target_features, summarize_audio_features


def test_summarize_audio_features():
    features = [
        {"energy": 0.8, "valence": 0.6, "danceability": 0.7},
        {"energy": 0.4, "valence": 0.2, "danceability": 0.5},
    ]
    summary = summarize_audio_features(features)
    assert summary["energy"] == 0.6
    assert summary["valence"] == 0.4
    assert summary["danceability"] == 0.6


def test_build_genre_counts():
    artists = [
        {"genres": ["pop", "dance pop"]},
        {"genres": ["pop", "edm"]},
    ]
    counts = build_genre_counts(artists)
    assert counts["pop"] == 2
    assert counts["dance pop"] == 1


def test_derive_target_features():
    targets = derive_target_features({"energy": 0.9, "valence": 0.2})
    assert targets["energy"] == 0.9
    assert targets["valence"] == 0.2
