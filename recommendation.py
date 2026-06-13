import pandas as pd

from sklearn.preprocessing import StandardScaler

from sklearn.neighbors import NearestNeighbors


# Load dataset

df = pd.read_csv("dataset.csv")


# Features used for recommendation

features = [

    "danceability",

    "energy",

    "acousticness",

    "instrumentalness",

    "liveness",

    "valence",

    "tempo"

]


# Remove missing values

df = df.dropna(subset=features)


# Scale features

scaler = StandardScaler()

scaled_data = scaler.fit_transform(df[features])


# Train KNN model

knn = NearestNeighbors(

    n_neighbors=6,

    metric='euclidean'

)

knn.fit(scaled_data)



# Recommendation function

def recommend_song(song_name):


    song = df[

        df["track_name"]

        .str.lower()

        == song_name.lower()

    ]


    if song.empty:

        print("Song not found!")

        return


    song_index = song.index[0]


    distances, indices = knn.kneighbors(

        [scaled_data[song_index]]

    )


    print("\n")
    
    print("✨"*15)
    
    print("🎶 YOUR SONG RECOMMENDATIONS 🎶")
    
    print("✨"*15)


    for i in indices[0][1:]:

        print("\n" + "="*50)

        print("🎵 SONG       :", df.iloc[i]["track_name"])

        print("🎤 ARTIST     :", df.iloc[i]["artists"])

        print("🎧 GENRE      :", df.iloc[i]["track_genre"])

        print("🔥 POPULARITY :", df.iloc[i]["popularity"])

        print("="*50)



# Main program

if __name__ == "__main__":


    song_name = input("Enter song name: ")


    recommend_song(song_name)