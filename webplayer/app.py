from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, render_template, Response
import json


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/formdata")
def producer():
    #form data to python dict

    producer = KafkaProducer(bootstrap_servers="kafka:9092",
                             value_serializer=lambda x: json.dumps(x).encode("ascii"))

    message1 = {
        "current_song":"id",
        "current_song":"name"

    }

    message2 = {
        "current_song": "id",
        "parameters": [
            {"danceability": "alpha"},
            {"loudness": "alpha"},
            {"tempo": "alpha"},
        ]
    }

    producer.send("current_song",data=message1)
    producer.send("parameter", data=message2)


@app.route("/consumer")
def consumer():
    consumer = KafkaConsumer("app", bootstrap_servers="kafka:9092", value_deserializer=lambda x: json.loads(x.decode('utf-8')), auto_offset_reset="earliest")

    for message in consumer:
        message = message.value

    def readjson():
        # opening a json for now because kafka wont run on my computer :-)
        with open('message.json') as f:
            data = json.load(f)
            return data



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969)
