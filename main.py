import time
from classes import MediaCenter

if __name__ == '__main__':
    mc = MediaCenter.MediaCenter()
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
        mc.clear_screen()
