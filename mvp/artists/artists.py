#appending parent directory
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from kafka import KafkaConsumer, KafkaProducer
import json
from resources.spotify_auth import Spotify_Auth
import time


auth = Spotify_Auth()

consumer = KafkaConsumer("dbtest", \
    bootstrap_servers="localhost:9092", \
    value_deserializer=lambda x: json.loads(x.decode('utf-8')), \
    auto_offset_reset="latest")

producer = KafkaProducer(bootstrap_servers='localhost:9092', \
    value_serializer=lambda x: json.dumps(x).encode("ascii"))


def do_nice_stuff(track_art_map,artist_store):

    artists_string = ",".join(artist_store)
    params = {
        "ids": artists_string
    }

    print("sending request with",len(artist_store),"artists")
    response = auth.get("https://api.spotify.com/v1/artists/", params=params)
    if response.status_code == 200:
        result = json.loads(response.content)
        #create artists + artist-track relationship
        for artist in result["artists"]:
            for trackid in track_art_map[artist["id"]]:
                message = {
                    "id": artist["id"],
                    "name": artist["name"],
                    "popularity": artist["popularity"],
                    "followers": artist["followers"]["total"],
                    "genres": ",".join(artist["genres"]),
                    "trackid":trackid
                }

                producer.send("createArtistandRel", value=message)
        producer.flush()

    elif response.status_code == 429:
        print("Too Many Requests, RATE LIMIT")

track_art_map = dict()
artist_store = list()

for message in consumer:
    message = message.value
    if message["meta"]["operation"] == "created":
        if message["payload"]["type"] == "node":
            if "Track" in message["payload"]["after"]["labels"]:
                message_values = message["payload"]["after"]["properties"]

                artists = message_values["artists"].split(",")
                trackid = message_values["id"]

                for artistid in artists:
                    if artistid not in track_art_map.keys():
                        track_art_map[artistid] = list()
                        artist_store.append(artistid)
    
                    if trackid not in track_art_map[artistid]:
                        track_art_map[artistid].append(trackid)

                if len(artist_store) > 45:
                    do_nice_stuff(track_art_map.copy(),artist_store.copy())
                    track_art_map = dict()
                    artist_store = list()
             

do_nice_stuff(track_art_map, artist_store)






