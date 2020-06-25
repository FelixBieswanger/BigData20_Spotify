#appending parent directory
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resources.kafka_factory import Kafka_factory
from resources.spotify_auth import Spotify_Auth
from kafka import KafkaProducer
import json
import time


import random

auth = Spotify_Auth()
kafka_factory = Kafka_factory()
producer = kafka_factory.get_producer()

"""
SEED GENRES

'acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal', 'bluegrass', 'blues', 'bossanova', 
'brazil', 'breakbeat', 'british', 'cantopop', 'chicago-house', 'children', 'chill', 'classical', 'club', 'comedy', 'country', 
'dance', 'dancehall', 'death-metal', 'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 'dubstep',
'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 
'groove', 'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop', 'holidays', 'honky-tonk', 
'house', 'idm', 'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 
'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal', 'metal-misc', 'metalcore', 'minimal-techno', 'movies', 'mpb', 'new-age', 
'new-release', 'opera', 'pagode', 'party', 'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop', 'progressive-house', 
'psych-rock', 'punk', 'punk-rock', 'r-n-b', 'rainy-day', 'reggae', 'reggaeton', 'road-trip', 'rock', 'rock-n-roll', 'rockabilly', 'romance',
'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul', 'soundtracks', 'spanish', 
'study', 'summer', 'swedish', 'synth-pop', 'tango', 'techno', 'trance', 'trip-hop', 'turkish', 'work-out', 'world-music']

"""

recommendations_seach_settings = {
    "limit":100,
    "seed_genres": "pop"
}

response_recomendations = json.loads(auth.get(
    "https://api.spotify.com/v1/recommendations", params=recommendations_seach_settings).content)


tracks = {}
for recoomandation in response_recomendations["tracks"]:

    tracks[recoomandation["id"]] = {
        "name": recoomandation["name"],
        "duration_ms": recoomandation["duration_ms"],
        "explicit": recoomandation["explicit"],
        "artists": ",".join([n["id"] for n in recoomandation["artists"]])
    }

track_ids_string = ",".join(tracks.keys())

response_audioanalysis = json.loads(auth.get(
    "https://api.spotify.com/v1/audio-features?ids="+track_ids_string).content)

for analysis in response_audioanalysis["audio_features"]:

    track = tracks[analysis["id"]]
    track["id"] = analysis["id"]

    analysis_store = {
        "danceability": analysis["danceability"],
        "energy": analysis["energy"],
        "key" : analysis["key"],
        "loudness" : analysis["loudness"],
        "mode" : analysis["mode"],
        "speechiness" : analysis["speechiness"],
        "acousticness" : analysis["acousticness"],
        "instrumentalness" : analysis["instrumentalness"],
        "liveness" : analysis["liveness"],
        "valence" : analysis["valence"],
        "tempo" : analysis["tempo"],
        "time_signature" : analysis["time_signature"]
    }

    for name in analysis_store.keys():
        if analysis_store[name] == None:
            analysis_store[name] = "nA"

        track[name] = analysis_store[name]

    try:
        producer.send("createTrack", value=track)
        producer.flush()
        print("sent")
    except Exception as e:
        print(e)

