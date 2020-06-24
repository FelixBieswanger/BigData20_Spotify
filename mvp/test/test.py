from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, render_template, Response
import json

app = Flask(__name__)

try:
    producer = KafkaProducer(bootstrap_servers="kafka:9092",
                            value_serializer=lambda x: json.dumps(x).encode("ascii"))

    producer.send("neo4j", value={"test":"test"})
    producer.flush()
except Exception as e:
    print(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/songs")
def songs():
    consumer = KafkaConsumer("createTrack", bootstrap_servers="kafka:9092",value_deserializer=lambda x: json.loads(x.decode('utf-8')),auto_offset_reset="earliest")

    #Using Yield create an Generator
    def events():
        for message in consumer:
            yield 'data:{0}\n\n'.format(message)

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")


@app.route("/neo4j")
def neo4jtest():
    consumer = KafkaConsumer("neo4j", bootstrap_servers="kafka:9092", value_deserializer=lambda x: json.loads(x.decode('utf-8')), auto_offset_reset="earliest")

    #Using Yield create an Generator
    def events():
        for message in consumer:
            yield 'data:{0}\n\n'.format(message)

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969)
