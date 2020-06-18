from kafka import KafkaConsumer, KafkaProducer
import json
import time
import socket
from py2neo import Graph

class Kafka_factory:

    def __init__(self):
        host = socket.gethostname()
        localhost = socket.gethostbyname(host)

        self.kafka_address = localhost+":9092"
        self.neo4j_adress = "bolt://"+localhost+":7687/db/data"



    def get_util(self,util):
        if util == "consumer":
            consumer = None
            graph = None
            retrys = 0
            while (consumer == None or graph == None) and retrys < 2:
                try:

                    # make ip dynamic
                    consumer = KafkaConsumer("dbtest",\
                        bootstrap_servers=self.kafka_address,\
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')),\
                        auto_offset_reset="earliest")

                    #is graphdatabase running?
                    graph = Graph(self.neo4j_adress,
                                  auth=("neo4j", "password"))
                    graph.run("Match () Return 1 Limit 1")
                except Exception as e:
                    retrys += 1
                    graph = None
                    print(e)
                    time.sleep(5)

                if consumer != None and graph != None:
                    print("connected consumer")
                    return consumer

            print("Could not connect")
            return None

        if util == "producer":
            producer = None
            graph = None
            retrys = 0
            while (producer == None or graph == None) and retrys < 2:
                try:
                    producer = KafkaProducer(bootstrap_servers=self.kafka_address,
                                            value_serializer=lambda x: json.dumps(x).encode("ascii"))

                    producer.send("avaiablity_check",{"t":1})
                    producer.flush() 

                    #is graphdatabase running?
                    graph = Graph(self.neo4j_adress,
                                  auth=("neo4j", "password"))
                    graph.run("Match () Return 1 Limit 1")
                except Exception as e:
                    retrys +=1
                    graph = None
                    print(e)
                    time.sleep(5)

                if producer != None and graph != None:
                    print("connected producer")
                    return producer
            
            print("Could not connect")
            return None
            
           
