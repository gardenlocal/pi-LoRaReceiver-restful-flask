#!/usr/bin/python3
import requests
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
from threading import Thread, Timer
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
	def __init__(self):
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
mode = 0		# default mode / 0: auto, 1: manual
spray = 5		# default spray for seconds : 5seconds in interval
interval = 60	# default spray interval in minutes : spray every 60 min 
running = 0		# default run in manual mode / 0: stop, 1: run

mode_ = []		# running mode_devices
spray_ = []		# spray_devices
interval_ = []	# spray_interval_mins_devices
running_ = []	# running_devices

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
		elif len(packet) is 15 :
			print(packet[1])
			prev_packet = packet
#			print('> New Packet!')

			if chr(packet[1]) is 'R':
				print("RADIO PACKET READ ::: ")
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

				devices[device_id-1].update(temp_val, humid_val, soil_val, timestamp_str, is_charging, rssi)

				#print packet information
				print("===============================================")
				print('received packet size is : %d' % len(packet));
		
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
		else :
			print("packet is not enough. bypassing....");
		display.show()
		
def report_weather():
	for i in range(number_of_devices):
		t_id = i+1
		print("=weather report=======================================" )
		print("DEVICE ID : %d" % t_id)
		print("Temp      : %0.2f C" % devices[i].temperature)
		print("Humid     : %0.2f %% " % devices[i].humidity)
		print("Soil	     : %d" % devices[i].soil)
		print("charge    : %r" % devices[i].charging)
		print("RSSI      : %d" % devices[i].rssi)

		headers = {'content-type' : 'application/json'}
		pushData = {
			'device_id' : t_id,
			'temperature' : devices[i].temperature,
			'humidity' : devices[i].humidity,
			'timestamp' : devices[i].timestamp,
			'soil' : devices[i].soil,
			'charging' : devices[i].charging,
			'rssi' : devices[i].rssi
		}
		res = requests.post('https://garden-local-dev.hoonyland.workers.dev/weather', headers = headers, data=json.dumps(pushData));
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> RESPONSE")
		print(res.content)

	t = Timer(120, report_weather)
	t.start()

# Flask routes
@app.route("/")
def index():
	return "<p>DWC2 WEATHER REPORT RESTFUL SERVER</p>"

@app.route("/weather", methods = ['GET'])
def return_weather_info():
	return jsonify({"temperature" : temp_val, "humidity" : humid_val, "timestamp" : timestamp_str, "charging" : is_charging, "rssi" : rssi})

@app.route("/interval", methods = ['GET'])
def get_interval():
	return_interval_info = []
	for i in range(number_of_devices):
		obj = {}
		obj["interval_minutes"] = interval_[i]
		return_interval_info.append(obj)
	return jsonify(return_interval_info)

@app.route("/interval", methods = ['POST'])
def set_interval():
	obj = request.get_json()
	interval_[obj['id']] = obj['interval']
	return jsonify(data=obj)


@app.route("/spray", methods = ['GET'])
def get_spray():
	return_interval_info = []
	for i in range(number_of_devices):
		obj = {}
		obj["spray"] = spray_[i]
		return_interval_info.append(obj)
	return jsonify(return_interval_info)

@app.route("/spray", methods = ['POST'])
def set_spray():
	obj = request.get_json()
	spray_[obj['id']] = obj['spray']
	return jsonify(data=obj)


@app.route("/mode", methods = ['GET'])
def get_mode():
	return_interval_info = []
	for i in range(number_of_devices):
		obj = {}
		obj["mode"] = mode_[i]
		return_interval_info.append(obj)
	return jsonify(return_interval_info)

@app.route("/mode", methods = ['POST'])
def set_mode():
	obj = request.get_json()
	mode_[obj['id']] = obj['mode']
	return jsonify(data=obj)

@app.route("/run", methods = ['GET'])
def get_running():
	return_running_info = []
	for i in range(number_of_devices):
		obj = {}
		obj["running"] = running_[i]
		return_running_info.append(obj)
	return jsonify(return_running_info)

@app.route("/run", methods = ['POST'])
def set_running():
	obj = request.get_json()
	running_[obj['id']] = obj['run']
	return jsonify(data=obj)

def main():
	# append list of weatherStation
	for i in range(number_of_devices):
		devices.append(weather_station())
		spray_.append(spray)
		interval_.append(interval)
		mode_.append(mode)
		running_.append(running)

#	threading.Timer(15, report_weather, args =()).start();
	report_weather()

	p = Thread(target=get_packet, args=( ))
	p.start()
	app.run(host='0.0.0.0', debug=True, use_reloader=False, port=3005)
	p.join()


if __name__ == "__main__":
	main()
