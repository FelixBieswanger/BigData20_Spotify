from kafka import KafkaProducer
import json
import random

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda x: json.dumps(x).encode("ascii"))

for i in range(50):

    person = {
        "name": "felix"+str(i),
        "surname": "boss"+str(i)
    }

    producer.send("mytopic",value=person)
    producer.flush()


for i in range(50):

    person = {
        "name": "david"+str(i),
        "surname": "boy"+str(i)
    }

    producer.send("othertopic", value=person)
    producer.flush()
