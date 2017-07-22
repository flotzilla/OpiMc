OpiMc
=======
Media center for Orange Pi Zero written in Python

Requirements
==========
- ds18b20 sensor
- 16*2 HD44780 display with i2c adapter
- 4 buttons and resistor for them
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
Python modules `smbus, python-vlc, pyA20`

Module `pyA20` was wrote for python version 2, so Python2 only 
   
Preparations
======
- Add stream radio sources to `stations.json` file
- Change `temp_sensor_file` variable value in `main.py` file to your ds18b20 sensor w1 address
- Change lcd i2c address in `I2C_LCD_driver.py` file from 0x3F to your address
  
Source for lcd driver was found [here](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d) 
  