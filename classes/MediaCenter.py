import time
import threading

from pyA20.gpio import gpio
from pyA20.gpio import port
from classes import Player
from devices import I2C_LCD_driver
from classes import OpenWeatherMap


class MediaCenter:
    # lcs custom chars for dislay
    custom_chars = [
        # celsius char
        [0x06, 0x09, 0x09, 0x06, 0x00, 0x00, 0x00, 0x00],
        # thermometer char
        [0x04, 0x0a, 0x0a, 0x0a, 0x0e, 0x1f, 0x1f, 0x0e],
        # another thermometer char
        [0x04, 0x0a, 0x0a, 0x0a, 0x0a, 0x11, 0x1f, 0x0e],
        # clocks
        [0x00, 0x00, 0x0e, 0x15, 0x17, 0x11, 0x0e, 0x00],
        # bell
        [0x04, 0x0e, 0x11, 0x11, 0x11, 0x11, 0x1f, 0x04],
        # dynamic
        [0x02, 0x06, 0x0E, 0x1E, 0x1E, 0x0E, 0x06, 0x02]
    ]

    # gpio
    b1 = port.PA6  # play/pause button
    b2 = port.PA1  # prev track
    b3 = port.PA0  # next track
    b4 = port.PA3  # alternation mode for screen state

    # statements
    player = None
    lcd = None
    utils = None

    # hardware states
    button_states = {'b1': False, 'b2': False, 'b3': False, 'b4': False}
    prev_button_states = {'b1': False, 'b2': False, 'b3': False, 'b4': False}
    current_screen = 0  # 0 or 1 or 2

    logger = None

    # variables
    curr_temp = prev_temp = 0.00

    running_line = {
        'is_active': False,
        'current_station': '',
        'previous_station': '',
        'steps_index': 0
    }

    def __init__(self, utils, logger):
        self.logger = logger
        self.utils = utils

        logger.debug('Init gpio settings')
        gpio.init()
        gpio.setcfg(self.b1, gpio.INPUT)
        gpio.setcfg(self.b2, gpio.INPUT)
        gpio.setcfg(self.b3, gpio.INPUT)
        gpio.setcfg(self.b4, gpio.INPUT)

        gpio.pullup(self.b1, gpio.PULLUP)
        gpio.pullup(self.b2, gpio.PULLUP)
        gpio.pullup(self.b3, gpio.PULLUP)
        gpio.pullup(self.b4, gpio.PULLUP)

        self.lcd = I2C_LCD_driver.lcd()
        self.lcd.lcd_load_custom_chars(self.custom_chars)

        self.player = Player.Player()
        if 'last_station' in self.utils.config:
            self.player.set_station(self.utils.config['last_station'])

        # tempo
        self.ow = OpenWeatherMap.OpenWeather(utils.config)
        self.weather = None

    def read_button_states(self):
        self.button_states['b1'] = gpio.input(self.b1)
        self.button_states['b2'] = gpio.input(self.b2)
        self.button_states['b3'] = gpio.input(self.b3)
        self.button_states['b4'] = gpio.input(self.b4)

    # screen state 0
    def display_default_screen(self):
        if self.weather is not None:
            self.curr_temp = self.weather['temp']
            self.prev_temp = self.curr_temp
        else:
            self.curr_temp = self.prev_temp

        self.lcd.lcd_display_string_pos("%s" % time.strftime("%H:%M %d/%m"), 1, 1)
        self.lcd.lcd_write(0x080)
        self.lcd.lcd_write_char(3)
        self.lcd.lcd_write(0xC0)
        self.lcd.lcd_write_char(2)
        self.lcd.lcd_display_string_pos("%sC    " % self.curr_temp, 2, 1)

        self._display_player_icon()

    # screen state 1
    def display_alternative_screen(self):
        self.lcd.lcd_display_string("CPU:%s%% T:%sC " % (self.utils.get_cpu_load().strip(), self.utils.get_cpu_temp()), 1)
        self.lcd.lcd_display_string("Mem:%sMb  " % self.utils.get_ram_usage().strip(), 2)

    # screen state 2
    def display_screen2(self):
        self.running_line['previous_station'] = self.running_line['current_station']
        self._display_player_icon()
        self.lcd.lcd_display_string_pos("%s" % time.strftime("%H:%M %d/%m"), 1, 1)
        self.lcd.lcd_write(0x080)
        self.lcd.lcd_write_char(3)

        str = self._get_running_line()
        spaces = 16 - len(str)

        self.lcd.lcd_display_string(str + spaces * " ", 2)

    def lcd_print(self, line1, line2):
        pass

    def next_screen(self):
        if self.current_screen == 2:
            self.current_screen = 0
        else:
            self.current_screen = self.current_screen + 1

    def clear_screen(self):
        self.lcd.lcd_clear()

    def _display_player_icon(self):
        # display player icon
        self.lcd.lcd_write(0x80 + 15)
        if self.player.is_playing:
            # write speaker char at the end of first line
            self.lcd.lcd_write_char(5)
        else:
            self.lcd.lcd_write_char(ord(' '))

    def _get_running_line(self):
        self.running_line['current_station'] = self.player.get_current_station()
        if self.running_line['current_station'] is not self.running_line['previous_station']:
            self.running_line['is_active'] = False
            self.running_line['steps_index'] = 0
            return self.running_line['current_station']
        else:
            self.running_line['is_active'] = True
            if self.running_line['steps_index'] - 1 == len(self.running_line['current_station']):
                self.running_line['steps_index'] = 0
            else:
                self.running_line['steps_index'] += 1

            index = self.running_line['steps_index']
            new_line = self.running_line['current_station'][index:15 + index]
            new_line_len = len(new_line)
            if new_line_len < 16:
                new_line_addon = self.running_line['current_station'][0:]
                new_line += " " + new_line_addon
        while len(new_line) < 16:
            new_line += " " + new_line_addon
            return new_line

    def running_text(self, text, line):
        pass

    def read_tempo(self):
        self.logger.debug('Running tempo reading')
        threading.Timer(self.utils.config['read_interval'], self.read_tempo).start()
        self.weather = self.ow.get_tempo()
