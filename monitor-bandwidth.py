from urllib2 import urlopen
from time import sleep
from json import dumps
from kafka import KafkaProducer
import argparse
import psutil
import time
from collections import deque
import threading

KAFKA = ""
PUB_IP = urlopen('http://ip.42.pl/raw').read()
PRODUCER = None
INTERFACE = None





def get_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', help='kafka IP address', type=str, required=True)
    parser.add_argument('-i', help='interface to get the TX from', type=str, required=True)
    parser.add_argument('-s', help='sleep time', type=int, required=True)
    return parser.parse_args()


def calc_ul_dl(rate, dt=3, interface='eth0'):
    t0 = time.time()
    counter = psutil.net_io_counters(pernic=True)[interface]
    tot = (counter.bytes_sent, counter.bytes_recv)

    while True:
        last_tot = tot
        time.sleep(dt)
        counter = psutil.net_io_counters(pernic=True)[interface]
        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [(now - last) / (t1 - t0) / 1000000.0
                  for now, last in zip(tot, last_tot)]
        rate.append((ul * 8, dl * 8))
        t0 = time.time()


def push_rate(rate):
    try:
        ul, dl = rate[-1]
        data = {'ip': PUB_IP, 'ul': ul, 'dl': dl}
        PRODUCER.send('mifeng', value=data)
    except Exception, e:
        print e


if __name__ == "__main__":
    results = get_argparse()
    KAFKA = results.k
    SLEEP = results.s
    INTERFACE = results.i
    server = KAFKA + ':9092'
    PRODUCER = KafkaProducer(bootstrap_servers=[server], value_serializer=lambda x: dumps(x).encode('utf-8'),
                             api_version=(0, 10, 1))
    # Create the ul/dl thread and a deque of length 1 to hold the ul/dl- values
    transfer_rate = deque(maxlen=1)
    t = threading.Thread(target=calc_ul_dl, args=(transfer_rate,))
    # The program will exit if there are only daemonic threads left.
    t.daemon = True
    t.start()
    while True:
        push_rate(transfer_rate)
        sleep(SLEEP)