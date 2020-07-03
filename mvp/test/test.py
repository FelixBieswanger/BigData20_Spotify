from kafka import KafkaConsumer, KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers="kafka:9092",
                         value_serializer=lambda x: json.dumps(x).encode("ascii"))

messages = [
    {"parameter": "danceability", "alpha": 1, "weight": 1},
    {"parameter": "loudness", "alpha": 1, "weight": 2},
    {"parameter": "tempo", "alpha": -1, "weight": 1},
    {"parameter": "distance", "alpha": 1, "weight": 2}
]

try:
    for m in messages:
        producer.send("current_Parameters", m)

    producer.flush()
except Exception as e:
    print(e)
