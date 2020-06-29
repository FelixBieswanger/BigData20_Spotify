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

    message = {
        "currentsong":"bla",
        "parameters":[
            {"parametername":"alpha"},
            {"parametername":"alpha"}
        ]
    }


    producer.send("topicname",data=message)


@app.route("/consumer")
def consumer():
    pass






if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969)
