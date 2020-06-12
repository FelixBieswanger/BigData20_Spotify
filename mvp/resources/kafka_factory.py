from kafka import KafkaConsumer, KafkaProducer

class Kafka_factory:
    def get_kafka_util(self,util):
        if util is None:
            return None
        if util == "consumer":
            consumer = KafkaConsumer("dbtest",\
                bootstrap_servers="localhost:9092",\
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),\
                auto_offset_reset="latest")
            return consumer
        if util == "poducer":
            producer = KafkaProducer(bootstrap_servers='localhost:9092',
                                     value_serializer=lambda x: json.dumps(x).encode("ascii"))
            return producer
