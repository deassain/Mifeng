import requests, time,sys,argparse

URL = ""
FILE = None
SLEEP_TIME = 20

def run(FILE_NAME):
    global FILE
    FILE = open(FILE_NAME,'w')
    FILE.write('epoch,response_time\n')
    while True:
        delay = measure_return()
        print delay
        insert_into_file(delay)
        time.sleep(SLEEP_TIME)

def measure_return():
     return float(requests.get(URL).elapsed.total_seconds())

def insert_into_file(response_time):
    global FILE
    epoch_time = int(time.time())
    FILE.write(str(epoch_time) + ', %s \n' % response_time)

def get_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='delay used for polling', type=int,required=True)
    parser.add_argument('-u',  help='url to poll', type=str, required=True)
    parser.add_argument('-o', help='output file name', type=str, required=True)
    return parser.parse_args()

if __name__ == "__main__":
    results = get_argparse()
    URL = results.u
    FILE_NAME = results.o
    SLEEP_TIME = results.t
    run(FILE_NAME)
