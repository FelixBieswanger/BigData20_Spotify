#appending parent directory
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resources.spotify_auth import Spotify_Auth
from resources.kafka_factory import Kafka_factory
import json
from datetime import datetime
from threading import Timer

auth = Spotify_Auth()
kafka_factory = Kafka_factory()

consumer = kafka_factory.get_consumer()
producer = kafka_factory.get_producer()

def do_nice_stuff(track_art_map, artist_store):

    #Timer(15, do_nice_stuff).start()

    if len(artist_store) > 0:
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
        else:
            print(response.status_code,"Error",response.content)

#Timer(15, do_nice_stuff).start()

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

                if len(artist_store) > 48:
                    do_nice_stuff(track_art_map.copy(), artist_store.copy())
                    track_art_map = dict()
                    artist_store = list()
                
                








