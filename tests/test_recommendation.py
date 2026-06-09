from recommendation import build_recommendation_cards, choose_seeds, mood_label


def test_choose_seeds():
    tracks = [{"id": "t1"}, {"id": "t2"}]
    artists = [{"id": "a1"}]
    seed_tracks, seed_artists = choose_seeds(tracks, artists)
    assert seed_tracks == ["t1", "t2"]
    assert seed_artists == ["a1"]


def test_build_recommendation_cards():
    cards = build_recommendation_cards([
        {
            "name": "Song A",
            "artists": [{"name": "Artist A"}],
            "album": {"name": "Album A", "images": [{"url": "https://example.com/a.jpg"}]},
            "external_urls": {"spotify": "https://open.spotify.com/track/123"},
            "popularity": 77,
        }
    ])
    assert cards[0]["name"] == "Song A"
    assert cards[0]["artists"] == "Artist A"
    assert cards[0]["popularity"] == 77


def test_mood_label():
    assert mood_label({"energy": 0.8, "valence": 0.7}) == "Bright & Hype"
