#!/usr/bin/python3
from daemonize import Daemonize
import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM9x radio module.
import adafruit_rfm69
from flask import Flask, request, jsonify
from flask_cors import CORS
#from multiprocessing import Process, Value
from threading import Thread
from datetime import datetime, timezone

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
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)
prev_packet = None

#global variable

def pkt_int_to_float(pkt_val_1, pkt_val_2, pkt_val_3 = None):
	if pkt_val_3 is None:
		float_val = pkt_val_1 << 8 | pkt_val_2
	else :
		float_val = pkt_val_1 << 16 | pkt_val_2 | pkt_val_3
	return float_val/100

def send_packet():
	rfm69.send('/W');

def get_packet():
	global temp_val
	global humid_val
	global timestamp_str
	global is_charging
	global rssi

	while True:
		packet = None
	
		#check for packet rx
		packet = rfm69.receive()
		rssi = rfm69.last_rssi

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
			temp_val = pkt_int_to_float(packet[1], packet[2])
			humid_val = pkt_int_to_float(packet[3], packet[4])
			if packet[5] is 1 :
				is_charging = True
			else :
				is_charging = False

			# timestamp
#			now = datetime.datetime.now()	# current date and time
#			now = datetime.datetime.utcnow()
#			timestamp_str = now.strftime("%Y/%m/%d")+" "+now.strftime("%H:%M:%S")	// custom string format
			timestamp_str = datetime.now(timezone.utc).isoformat()[:-6]+'Z'

			#print packet information
			print("Temp    : %0.2f C" % temp_val)
			print("Humid   : %0.2f %% " % humid_val)
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
		


# Flask routes
@app.route("/")
def index():
	return "<p>DWC2 WEATHER REPORT RESTFUL SERVER</p>"

@app.route("/weather", methods = ['GET'])
def return_weather_info():
	return jsonify({"temperature" : temp_val, "humidity" : humid_val, "timestamp" : timestamp_str, "charging" : is_charging, "rssi" : rssi})

def main():
#	loop_on = Value('b', True)

	p = Thread(target=get_packet, args=( ))
	p.start()
	app.run(host='0.0.0.0', debug=True, use_reloader=False, port=3005)
	p.join()

if __name__ == "__main__":
    main()
