OpiMc
=======  
Internet-radio player for Orange Pi Zero written in Python2. 

Device use HD44780 display and sensor buttons to control it. 
Also, use build-in http server to handle request remotely via json-api, using https connection and basic http auth


Requirements
==========
- ds18b20 sensor
- 16*2 HD44780 display with i2c adapter
- 4 click buttons and resistor
- configured `spdif` kernel module for audio output
- configured `i2c` and `w1_therm`, `w1gpio`, `wire` kernel modules


Feautures
=========
- playing internet radio stations
- display time and date
- display temperature 
- display cpu and mem load
- build-in python http-server to handle commands from remote

Dependencies
=========
Python modules `smbus, python-vlc, pyA20, pyyaml`

Module `pyA20` was wrote for Python version 2, so Python2 only 
   
Preparations
======
- Add stream radio sources to `stations.json` file
- Change `temp_sensor_file` value in `config.yaml` file to your ds18b20 sensor w1 address
- Change lcd i2c address in `devices/I2C_LCD_driver.py` file from __0x3F__ to your address
- Generate ssl key for build-in http-server with command `openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes`
 and put `server.pem` file to `certfile` directory. Notice, that during running openssl command, you should specify parameter `common name` as your device local ip address.
 Or use better certificate  
- Change `server_user_name` and `server_user_password` params to yours for base http authentication 


--- 

Source of the lcd driver was found [here](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d)  

---

To run app on system startup (systemd) edit __WorkingDirectory__ and __ExecStart__ params  
in `opimc.service` and then copy file to `/lib/systemd/system/` directory  

`chmod 644 opimc.service`  
`sudo systemctl daemon-reload`   
`sudo systemctl enable opimc.service`  

App will start on next reboot.   
To run immediately type `sudo systemctl start opimc.service` 

Notes
===

Tested on Orange Pi Zero H2+ 256Mb edition
