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
## demonize with pm2
- install pm2
```
sudo npm install -g pm2
```
-  move to repo location and 
```
$ pm2 start report2Server.json
$ pm2 save
```

## autostart open tmux

### 1. install tmux
```
$ sudo apt install tmux
```

### 2. if system not using zsh, install it (also recommend to install [oh-my-zsh](https://github.com/ohmyzsh/ohmyzsh))
```
$ sudo apt install zsh
$ which zsh # zsh location
$ chsh -s /usr/bin/zsh # change default shell to zsh (using zsh location above result)
# try logout and login it works
```

### 3. add to `~/.zshrc`, end of lines
```
session_name="report2Server"

# 1. First you check if a tmux session exists with a given name.
tmux has-session -t=$session_name 2> /dev/null

# 2. Create the session if it doesn't exists.
if [[ $? -ne 0 ]]; then
  TMUX='' tmux new-session -d -s "$session_name"
fi

# 3. Attach if outside of tmux, switch if you're in tmux.
if [[ -z "$TMUX" ]]; then
  tmux attach -t "$session_name"
else
  tmux switch-client -t "$session_name"
fi
```
- reload script `source ~/.zshrc`

### 4. detach tmux session before exit
```
# press <Ctrl + B> - d 
$ exit # logout 
```

## checking logs
```
$ pm2 logs
```

# before deploy...
- set `number of devices`
edit `number_of_devices` [here](https://github.com/gardenlocal/pi-LoRaReceiver-restful-flask/blob/4e1f8578ff4c174b044cdaa9ba1ab422f90da5b6/report2Server.py#L40), depends on weather station number
```
number_of_devices = 3
```

## Testing 
```
$ @GET: IP_ADDRESS_:3005/weather
```
