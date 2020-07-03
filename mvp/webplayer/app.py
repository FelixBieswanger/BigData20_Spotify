from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, render_template, Response, request
import json


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/parameters", methods=["POST"])
def producer1():
    #form data to python dict

    producer = KafkaProducer(bootstrap_servers="kafka:9092",value_serializer=lambda x: json.dumps(x).encode("ascii"))
    data = request.form.to_dict()
    keys = list(data.keys())[0]
    message = json.loads(keys)
    print(message)  

    producer.send("current_Parameters", message)
    producer.flush()

    return "Done"


@app.route("/currentSong", methods=["POST"])
def producer2():
    #form data to python dict

    producer = KafkaProducer(bootstrap_servers="kafka:9092",
                             value_serializer=lambda x: json.dumps(x).encode("ascii"))
    data = request.form.to_dict()
    keys = list(data.keys())[0]
    message = json.loads(keys)
    print(message)

    producer.send("current_Song", message)
    producer.flush()

    return "Done"

@app.route("/recomendations")
def consumer():
    consumer = KafkaConsumer("recommendations", bootstrap_servers="kafka:9092",
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')), auto_offset_reset="earliest")

    #Using Yield create an Generator
    def events():
        for message in consumer:
            yield 'data:{0}\n\n'.format(message.value)

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=6969, use_reloader=False)
