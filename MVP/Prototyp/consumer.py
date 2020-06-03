from pykafka import KafkaClient

client = KafkaClient("localhost:9092")
topic = client.topics["songids"]


for message in topic.get_simple_consumer():
    print(message.value)
