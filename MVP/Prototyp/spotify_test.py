from pykafka import KafkaClient

client = KafkaClient("localhost:9092")
topic = client.topics["songids"]

for i in range(10):
    producer = topic.get_sync_producer()
    producer.produce("Hello".encode("ascii"))
