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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=6969,use_reloader=False)
