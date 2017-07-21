import Player
import time

from pyA20.gpio import gpio
from pyA20.gpio import port
from devices import I2C_LCD_driver
from utils import Utils


class MediaCenter():
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

    # ds18b20 i2c location
    temp_sensor_file = '/sys/bus/w1/devices/28-05168238f6ff/w1_slave'

    # statements
    player = None
    lcd = None
    utils = None

    # hardware states
    button_states = {'b1': False, 'b2': False, 'b3': False, 'b4': False}
    prev_button_states = {'b1': False, 'b2': False, 'b3': False, 'b4': False}
    current_screen = 0  # 0 or 1 or 2

    last_temp_value = ''

    def __init__(self):
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
        self.utils = Utils.Utils(self.temp_sensor_file)

    def read_button_states(self):
        self.button_states['b1'] = gpio.input(self.b1)
        self.button_states['b2'] = gpio.input(self.b2)
        self.button_states['b3'] = gpio.input(self.b3)
        self.button_states['b4'] = gpio.input(self.b4)

    # screen state 0
    def display_default_screen(self):
        self.lcd.lcd_display_string_pos("%s" % time.strftime("%H:%M %d/%m"), 1, 1)
        self.lcd.lcd_write(0x080)
        self.lcd.lcd_write_char(3)
        self.lcd.lcd_write(0xC0)
        self.lcd.lcd_write_char(2)
        self.lcd.lcd_display_string_pos("%sC    " % mc.utils.read_temp(), 2, 1)

        # display player icon
        self.lcd.lcd_write(0x80 + 15)
        if mc.player.isPlaying:
            # write dynamic char at the end of first line
            self.lcd.lcd_write_char(5)
        else:
            self.lcd.lcd_write_char(ord(' '))

    # screen state 1
    def display_alternative_screen(self):
        self.lcd.lcd_display_string("CPU:%s%%    " % mc.utils.get_cpu_load().strip(), 1)
        self.lcd.lcd_display_string("Mem:%sMb" % mc.utils.get_ram_usage().strip(), 2)

    # screen state 2
    def display_screen2(self):
        self.lcd.lcd_display_string_pos("%s" % time.strftime("%H:%M %d/%m"), 1, 1)
        self.lcd.lcd_write(0x080)
        self.lcd.lcd_write_char(3)

        str = self.player.get_current_station()[:16]
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


if __name__ == '__main__':
    mc = MediaCenter()
    mc.display_default_screen()
    try:
        while True:
            mc.read_button_states()

            if mc.button_states['b1']:  # press play / pause
                if mc.prev_button_states['b1'] is not True:
                    if mc.player.isPlaying:
                        mc.player.pause()
                    else:
                        mc.player.play()
                    mc.prev_button_states['b1'] = True
            else:
                mc.prev_button_states['b1'] = False

            if mc.button_states['b2']:  # press prev station
                mc.player.prev_station()

            if mc.button_states['b3']:  # press next station
                mc.player.next_station()

            if mc.button_states['b4']:  # press change screen mode
                mc.clear_screen()
                mc.next_screen()

            if mc.current_screen == 0:
                mc.display_default_screen()
            elif mc.current_screen == 1:
                mc.display_alternative_screen()
            elif mc.current_screen == 2:
                mc.display_screen2()

            time.sleep(0.5)

    except KeyboardInterrupt:
        print(u"\r\n Bye")
    finally:
        mc.lcd.lcd_write(I2C_LCD_driver.LCD_CLEARDISPLAY)
        mc.lcd.lcd_write(I2C_LCD_driver.LCD_RETURNHOME)
