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
    pass






if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969)
