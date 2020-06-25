#appending parent directory
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from resources.kafka_factory import Kafka_factory
from resources.spotify_auth import Spotify_Auth


auth = Spotify_Auth()
kafka_factory = Kafka_factory()

consumer = kafka_factory.get_consumer()
produce = kafka_factory.get_producer()

