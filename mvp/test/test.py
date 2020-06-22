from pykafka import KafkaClient
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/songs")
def songs():
    client = KafkaClient(hosts="kafka:9092")
    topic = client.topics["createTrack"]

    #Using Yield create an Generator
    def events():
        for message in topic.get_simple_consumer():
            result = message.value.decode()
            yield 'data:{0}\n\n'.format(result)

    #Mimetype: Event-Stream takes an Generator
    return Response(events(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969)
