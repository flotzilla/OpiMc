import time
from classes import MediaCenter
import logging

logger = None


def init_logger():
    global logger
    logger = logging.getLogger('OpiMc logger')
    fh = logging.FileHandler('app.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)


if __name__ == '__main__':
    init_logger()
    logger.debug('starting new session')

    mc = MediaCenter.MediaCenter(logger)
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
                mc.set_config_param('last_station', mc.player.get_current_station())

            if mc.button_states['b3']:  # press next station
                mc.player.next_station()
                mc.set_config_param('last_station', mc.player.get_current_station())

            if mc.button_states['b4']:  # press change screen mode
                mc.clear_screen()
                mc.next_screen()

            if mc.current_screen == 0:
                mc.display_default_screen()
            elif mc.current_screen == 1:
                mc.display_alternative_screen()
            elif mc.current_screen == 2:
                mc.display_screen2()

            time.sleep(0.2)

    except KeyboardInterrupt:
        print(u"\r\n Bye")
    finally:
        mc.set_config_param('last_station', mc.player.get_current_station())
        mc.save_config_to_file()
        mc.clear_screen()
        logger.debug('going down')
