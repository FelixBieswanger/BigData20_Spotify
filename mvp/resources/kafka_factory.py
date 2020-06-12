from kafka import KafkaConsumer, KafkaProducer
import time

class Kafka_factory:
    def get_util(self,util):
        if util == "consumer":
            consumer = None
            retrys = 0
            while consumer == None and retrys <= 5:
                try:
                    consumer = KafkaConsumer("dbtest",\
                        bootstrap_servers="localhost:9092",\
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')),\
                        auto_offset_reset="latest")
                    return consumer
                except:
                    retrys+=1
                    time.sleep(3)
                
                print("Could not connect to kafka server")
                return None

        if util == "poducer":
            producer = None
            retrys = 0
            while producer == None and retrys <= 5:
                try:
                    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                                            value_serializer=lambda x: json.dumps(x).encode("ascii"))
                    return producer
                except:
                    retrys += 1
                    time.sleep(3)

            print("Could not connect to kafka server")
            return None
        
        return None
            
           
