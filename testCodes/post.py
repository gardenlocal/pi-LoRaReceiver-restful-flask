import requests
import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import json
# Flask init
app = Flask(__name__)
CORS(app)

next_time = datetime.now();
delta = timedelta(seconds=60);

def report_weather():
    headers= {'content-type' : 'application/json'}
    timestamp_str = datetime.now(timezone.utc).isoformat()[:-6]+'Z';
    deviceId = 1;
    temperature = random.randrange(20, 40);
    humidity = random.randrange(30, 50);
    co2 = int(random.randrange(600, 1000));
    rssi = int(random.randrange(8, 11));
    pushData = {
        'temperature' : temperature,
        'humidity' : humidity,
        'co2' : co2,
        'timestamp' : timestamp_str,
        'charging' : True,
        'rssi' : rssi
    }
    print("jsondump: ", json.dumps(pushData)); 
    res = requests.post('https://garden-local-dev.hoonyland.workers.dev/weather', headers=headers, data=json.dumps(pushData));

    print ("response from server: ", res.text)

while True:
    period = datetime.now()

    if period >= next_time:
        print(period)
        report_weather();
        next_time += delta;
