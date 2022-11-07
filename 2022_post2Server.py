#!/usr/bin/python3
from daemonize import Daemonize
import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM9x radio module.
import adafruit_rfm9x
from flask import Flask, request, jsonify
from flask_cors import CORS
#from multiprocessing import Process, Value
from threading import Thread
from datetime import datetime, timezone, timedelta
import json

# union in python
from ctypes import(
	Union, Array,
	c_byte, c_float, c_uint16,
	cdll, CDLL
)

class fbyte_array(Array):
	_type_ = c_byte
	_length_ = 4

class lbyte_array(Array):
	_type_ = c_byte
	_length_ = 2

class float32_type(Union):
	_fields_ = ("data", c_float), ("chunk", fbyte_array)

class uint16_type(Union):
	_fields_ = ("data", c_uint16), ("chunk", lbyte_array)

number_of_devices = 3
devices = []

# class of sensorData
class weather_station:
	def __init__(self, device_id):
		self.device_id= device_id
		self.temperature = 0
		self.humidity = 0
		self.soil = 9
		self.timestamp = "null"
		self.charging = 0
		self.rssi = 0

	def update(self, temperature, humidity, soil, timestamp, charging, rssi):
		self.temperature = temperature
		self.humidity = humidity
		self.soil = soil
		self.timestamp = timestamp
		self.charging = charging
		self.rssi = rssi

# Flask init
app = Flask(__name__)
CORS(app)

#pid = "/tmp/restful.pid"

# SET RFM9x RADIO FREQ
RADIO_FREQ_MHZ = 900.0
# init OLED with I2C
i2c = busio.I2C(board.SCL, board.SDA)
#LED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure RFM9x LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
prev_packet = None

#global variable

def send_packet():
	rfm9x.send('/W');

def get_packet():
	# global temp_val
	# global humid_val
	# global device_id
	# global soil_val
	# global timestamp_str
	# global is_charging
	# global rssi

	while True:
		packet = None
	
		#check for packet rx
		packet = rfm9x.receive()
		rssi = rfm9x.last_rssi

		display.fill(0)
		display.text("DWC2 WEATHER", 0, 0, 1)
		display.text("> packet wating ... ", 0, 20, 1);


		if packet is None :
#			display.fill(0)
#			display.show()
#			display.text('- Waiting for PKT -', 10, 20, 1)
			time.sleep(1);
		else:
			prev_packet = packet
#			print('> New Packet!')

			#Decode packet
			device_id = (packet[2])
			t_temp_val = float32_type()
			t_humid_val = float32_type()
			t_soil_val = uint16_type()

			t_temp_val.chunk[:] = (packet[3], packet[4], packet[5], packet[6])
			t_humid_val.chunk[:] = (packet[7], packet[8], packet[9], packet[10])
			t_soil_val.chunk[:] = (packet[11], packet[12])

			temp_val = t_temp_val.data
			humid_val = t_humid_val.data
			soil_val = t_soil_val.data

			if packet[13] is 1 :
				is_charging = True
			else :
				is_charging = False

			# timestamp
			timestamp_str = datetime.now(timezone.utc).isoformat()[:-6]+'Z'

			devices[device_id].update(temp_val, humid_val, soil_val, timestamp_str, is_charging, rssi)

			#print packet information
			print("===============================================")
			print("DEVICE  : %d" % device_id)
			print("Temp    : %0.2f C" % temp_val)
			print("Humid   : %0.2f %% " % humid_val)
			print("Soil	   : %d" % soil_val)
			print("charge  : %r" % is_charging)
			print("RSSI    : %d" % rssi)
			print("updated : " + timestamp_str)
			display.fill(0)
			display.text("DWC2 WEATHER     " + str(rssi), 0, 0, 1)
			
			if is_charging is True: 
				display.text('> ' + str(temp_val)+ "C / " + str(humid_val) + "%" + " + CHG", 0, 10, 1);
			else:
				display.text('> ' + str(temp_val)+ "C / " + str(humid_val) + "%", 0, 10, 1);
			
			display.text("> " + timestamp_str, 0, 20, 1);
			time.sleep(1)
		display.show()
		
def report_weather(device_id):
	print("=weather report=================")
	headers = {'content-type' : 'application/json'}
	pushData = {
		'co2' : 0,
		'temperature' : devices[device_id].temp_val,
		'humidity' : devices[device_id].humid_val,
		'deviceId' : devices[device_id].device_id,
		'timestamp' : devices[device_id].timestamp_str,
		'charging' : devices[device_id].is_charging,
		'rssi' : devices[device_id].rssi
	}
	res = request.post('https://garden-local-dev.hoonyland.workers.dev/weather', headers = headers, data=json.dumps(pushData));

# Flask routes
@app.route("/")
def index():
	return "<p>DWC2 WEATHER REPORT RESTFUL SERVER</p>"

@app.route("/weather", methods = ['GET'])
def return_weather_info():
	return jsonify({"temperature" : temp_val, "humidity" : humid_val, "timestamp" : timestamp_str, "charging" : is_charging, "rssi" : rssi})

def main():
	next_time = datetime.now();
	delta = timedelta(seconds = 60);

	for i in range(number_of_devices):
		devices.append(weather_station(i))

	while True:
		period = datetime.now()

		if period >= next_time:
			for i in range(number_of_devices)
				report_weather(devices[devide_id])


	p = Thread(target=get_packet, args=( ))
	p.start()
	app.run(host='0.0.0.0', debug=True, use_reloader=False, port=3005)
	p.join()

	q = Thread(target=report_weather, args=( ))
	q.start()
	q.join()

if __name__ == "__main__":
	main()