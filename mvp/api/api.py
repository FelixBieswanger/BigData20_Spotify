from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, render_template, Response, request
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={"/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Hello to Spotify API</h1>"

@app.route("/parameters", methods=["POST"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def producer1():
    #form data to python dict

    print(request)

    try:
        producer = KafkaProducer(bootstrap_servers="kafka:9092",value_serializer=lambda x: json.dumps(x).encode("ascii"))
        data = request.form.to_dict()
        keys = list(data.keys())[0]
        messages = json.loads(keys)  
        for message in messages:
            producer.send("current_Parameters", message)
        producer.flush()
        return str(messages)
    except Exception as e:
        return str(e)


@app.route("/currentSong", methods=["POST"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def producer2():
    #form data to python dict
    try:
        producer = KafkaProducer(bootstrap_servers="kafka:9092",
                                value_serializer=lambda x: json.dumps(x).encode("ascii"))
        data = request.form.to_dict()
        print(data,flush=True)
        keys = list(data.keys())[0]
        message = json.loads(keys)
        print(message, flush = True)
        producer.send("current_song", message)
        producer.flush()
        return str(message)
    except Exception as e:
        print(e)
        return str(e)



@app.route("/recomendations")
def consumer():
    consumer = KafkaConsumer("recommendations", bootstrap_servers="kafka:9092",
                             value_deserializer=lambda x: x, auto_offset_reset="latest")
    #Using Yield create an Generator
    def events():
        for message in consumer:
            print(message)
            yield 'data:{0}\n\n'.format(str(message.value))

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969, use_reloader=False)
