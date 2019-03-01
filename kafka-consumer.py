from kafka import KafkaConsumer
from json import loads
from elasticsearch import Elasticsearch
import argparse

es = Elasticsearch()


def get_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', help='kafka IP address', type=str, required=True)


def consume(consumer):
    for message in consumer:
        value = message.value
        ip = value["ip"]
        ip = int(ip.replace('.', '0'))
        es.index(index="test-index", doc_type='mifeng', id=ip, body=value)



if __name__ == "__main__":
    results = get_argparse()
    KAFKA = results.k
    consumer = KafkaConsumer(
        'mifeng',
        bootstrap_servers=[KAFKA + ':9092'],
        value_deserializer=lambda x: loads(x.decode('utf-8')),
        api_version=(0, 10, 1))
    consume(consumer)

