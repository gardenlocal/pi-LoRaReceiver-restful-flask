# LoRa packet receiver & restful api

## requirement 
circuit Python이 업데이트됐는지, 새로 셋업시 3.6에서 동작안함. 3.7.0으로 업데이트해야함

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
$ python3 restful2.py
```

## Testing 
```
$ @GET: IP_ADDRESS_:3005/weather
```
