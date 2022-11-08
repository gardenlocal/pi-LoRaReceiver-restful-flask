# LoRa packet receiver & restful api
-> [related repo](https://github.com/gardenlocal/feather-weatherReportLoRa)
1. read weather/environment information from stations through RFM9x LoRa
2. report to cloud server
3. get fog machine command from cloud server (need to implement.)

## requirement 
- circuit Python이 업데이트됐는지, 새로 셋업시 3.6에서 동작안함. 3.7.0으로 업데이트해야함
- 이전 정상 작동 디바이스의 경우 기존대로 3.5.0 사용가능

### python 3.7.0
```
$ wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
$ tar xvf Python-3.7.0.tgz
$ cd Python-3.7.0
$ ./configure
$ make
$ sudo make altinstall
$ sudo ln -sf /usr/local/bin/python3.7 /usr/bin/python3
```

## circuit python setup in raspbian
```
$ sudo apt install python3-pip
$ sudo apt-get install python3-sysv-ipc
$ sudo pip3 install adafruit-circuitpython-ssd1306
$ sudo pip3 install adafruit-circuitpython-framebuf
$ sudo pip3 install adafruit-circuitpython-rfm9x
$ pip3 install -U Flask
$ pip3 install -U flask-cors
```

## Running
```
$ python3 report2Server.py
```

## Editding 
edit `number_of_devices` [here](https://github.com/gardenlocal/pi-LoRaReceiver-restful-flask/blob/4e1f8578ff4c174b044cdaa9ba1ab422f90da5b6/report2Server.py#L40), depends on weather station number
```
```
## Testing 
```
$ @GET: IP_ADDRESS_:3005/weather
```
