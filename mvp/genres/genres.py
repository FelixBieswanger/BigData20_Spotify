import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#appending parent directory
from threading import Timer
from datetime import datetime
import json
from resources.kafka_factory import Kafka_factory
from resources.spotify_auth import Spotify_Auth

auth = Spotify_Auth()
kafka_factory = Kafka_factory()

consumer = kafka_factory.get_consumer()
producer = kafka_factory.get_producer()


for message in consumer:
    message = message.value
    if message["meta"]["operation"] == "created":
        if message["payload"]["type"] == "node":
            if "Artist" in message["payload"]["after"]["labels"]:
                message_values = message["payload"]["after"]["properties"]

                genres = message_values["genres"].split(",")
                artistid = message_values["id"]

                for genre in genres:
                    message = {
                        "artistid":artistid,
                        "name":genre
                    }
                    producer.send("createGenre",value=message)
                    producer.flush()
