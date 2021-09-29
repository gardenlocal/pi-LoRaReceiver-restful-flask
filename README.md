# LoRa packet receiver & restful api

## requirement 
### python >=3.6.0
```
$ wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
$ tar xf Python-3.6.5.tar.xz
$ cd Python-3.6.5
$ ./configure
$ make
$ sudo make altinstall
$ sudo ln -sf /usr/local/bin/python3.6 /usr/bin/python3
```

## circuit python setup in raspbian
```
$ sudo apt install python3-pip
$ sudo apt-get install python3-sysv-ipc
$ sudo pip3 install adafruit-circuitpython-ssd1306
$ sudo pip3 install adafruit-circuitpython-framebuf
$ sudo pip3 install adafruit-circuitpython-rfm9x
```
