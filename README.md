OpiMc
=======
Media center for Orange Pi Zero written in Python

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

Dependencies
=========
Python modules `smbus, python-vlc, pyA20, pyyaml`

Module `pyA20` was wrote for python version 2, so Python2 only 
   
Preparations
======
- Add stream radio sources to `stations.json` file
- Change `temp_sensor_file` value in `classes/MediaCenter.py` file to your ds18b20 sensor w1 address
- Change lcd i2c address in `devices/I2C_LCD_driver.py` file from __0x3F__ to your address
  
---  

Source of the lcd driver was found [here](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d) 

---

To run app on system startup (systemd) copy `opimc.service` to `/lib/systemd/system/` directory  
and run `chmod 644 opimc.service`

Then run `sudo systemctl daemon-reload` and ` sudo systemctl enable myscript.service`.  
 App will start on next reboot.   
To run immediately type `sudo systemctl start myscript.service` 
