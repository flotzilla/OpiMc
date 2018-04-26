import time
from classes import MediaCenter, RequestServer, Encoder
import logging
from utils import Utils
import telepot
from telepot.loop import MessageLoop
import alsaaudio


logger = None

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    print 'Got command: %s' % command

    m = alsaaudio.Mixer('Line Out')
    vol = m.getvolume()[0]

    if command == '/next':
        mc.player.next_station()
        utils.set_config_param('last_station', mc.player.get_current_station())
    elif command == '/prev':
        mc.player.prev_station()
        utils.set_config_param('last_station', mc.player.get_current_station())
    elif command == '/pause':
        mc.player.pause()
    elif command == '/play':
        mc.player.play()
    elif command == '/station':
        bot.sendMessage(chat_id, str(mc.player.get_current_station()))
    elif command =='/volume':
        bot.sendMessage(chat_id, str(m.getvolume()))
    elif command =='/vol+':
        print vol
        vol = vol+10
        if vol>100:
            vol=100
        m.setvolume(vol)
        bot.sendMessage(chat_id, str(m.getvolume()))
    elif command =='/vol-':
        print vol
        vol = vol-10
        if vol<0:
            vol=0
        m.setvolume(vol)
        bot.sendMessage(chat_id, str(m.getvolume()))


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

    utils = Utils.Utils(logger)
    mc = MediaCenter.MediaCenter(utils, logger)
    mc.read_tempo()
    mc.display_default_screen()

    server = RequestServer.RequestServer(utils, mc, logger)
    server.run()

    en = Encoder.Encoder()
    mix = alsaaudio.Mixer('Line Out')

    bot = telepot.Bot('*insert your telegram token here*')

    MessageLoop(bot, handle).run_as_thread()
    print 'I am listening ...'

    try:
        while True:
            vm=en.get_volume()
            if vm != 255:
                print (vm)
                mix.setvolume(vm)

            mc.read_button_states()

            if mc.button_states['b1']:  # press play / pause
                if mc.prev_button_states['b1'] is not True:
                    if mc.player.is_playing:
                        mc.player.pause()
                    else:
                        mc.player.play()
                    mc.prev_button_states['b1'] = True
            else:
                mc.prev_button_states['b1'] = False

            if mc.button_states['b2']:  # press prev station
                mc.player.prev_station()
                utils.set_config_param('last_station', mc.player.get_current_station())

            if mc.button_states['b3']:  # press next station
                mc.player.next_station()
                utils.set_config_param('last_station', mc.player.get_current_station())

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
        utils.set_config_param('last_station', mc.player.get_current_station())
        utils.save_config_to_file()
        mc.clear_screen()
        mc.kill_timing_threads()
        server.stop()
        logger.debug('going down')
