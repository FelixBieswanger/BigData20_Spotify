from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, render_template, Response, request, Blueprint, url_for
from flask_restplus import Resource, Api
import json


app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/doc')
app.register_blueprint(blueprint)

@app.route("/")
def index():
    return render_template("index.html")

@api.route("/parameters")
class Producer1(Resource):
    def post(self):
        #form data to python dict

        try:
            producer = KafkaProducer(bootstrap_servers="localhost:9092",
                                     value_serializer=lambda x: json.dumps(x).encode("ascii"))
            data = request.form.to_dict()
            print(request.form.to_dict())
            keys = list(data.keys())[0]
            messages = json.loads(keys)
            print(messages)
            for message in messages:
                producer.send("current_Parameters", message)
            producer.flush()
            return str(messages)
        except Exception as e:
            return str(e)

@app.route("/currentSong", methods=["POST"])
def producer2():
    #form data to python dict
    try:
        producer = KafkaProducer(bootstrap_servers="localhost:9092",
                                value_serializer=lambda x: json.dumps(x).encode("ascii"))
        data = request.form.to_dict()
        keys = list(data.keys())[0]
        message = json.loads(keys)
        producer.send("current_Song", message)
        producer.flush()
        return "Done"
    except Exception as e:
        return str(e)



@app.route("/recomendations")
def consumer():
    consumer = KafkaConsumer("recommendations", bootstrap_servers="localhost:9092",
                             value_deserializer=lambda x: x, auto_offset_reset="latest")

    #Using Yield create an Generator
    def events():
        for message in consumer:
            yield 'data:{0}\n\n'.format(str(message.value))

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="localhost", debug=True, port=6969)
