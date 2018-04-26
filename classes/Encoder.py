import OPi.GPIO as GPIO
import threading
from time import sleep

class Encoder:
                        # GPIO Ports
    Enc_A = 16                              # Encoder input A: input GPIO 4
    Enc_B = 18                              # Encoder input B: input GPIO 14
    Volume =0
    NewCounter=0
    Rotary_counter = 0                      # Start counting from 0
    Current_A = 1                                   # Assume that rotary switch is not
    Current_B = 1                                   # moving while we init software

    Volume = 0
    NewCounter = 0
    LockRotary = threading.Lock()           # create lock for rotary switch

# initialize interrupt handlers
    def __init__(self):
	print ("init-------------")
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.Enc_A, GPIO.IN)
        GPIO.setup(self.Enc_B, GPIO.IN) #define the Encoder switch inputs

        GPIO.setwarnings(True)
                                            # setup callback thread for the A and B encoder
                                            # use interrupts for all inputs
	
	GPIO.add_event_detect(self.Enc_A, GPIO.RISING, callback=self.rotary_interrupt)                                # NO bouncetime
        GPIO.add_event_detect(self.Enc_B, GPIO.RISING, callback=self.rotary_interrupt)                                # NO bouncetime


# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
    def rotary_interrupt(self,A_or_B):
	#global Rotary_counter, Current_A, Current_B, LockRotary
                                                    # read both of the switches
        Switch_A = GPIO.input(self.Enc_A)
        Switch_B = GPIO.input(self.Enc_B)
                                                    # now check if state of A or B has changed
                                                    # if not that means that bouncing caused it
	if self.Current_A == Switch_A and self.Current_B == Switch_B:         # Same interrupt as before (Bouncing)?
	    return                                                                          # ignore interrupt!

        self.Current_A = Switch_A                                                                # remember new state
        self.Current_B = Switch_B                                                                # for next bouncing check


	if (Switch_A and Switch_B):                                         # Both one active? Yes -> end of sequence
	    self.LockRotary.acquire()                                            # get lock
            if A_or_B == self.Enc_B:                                                     # Turning direction depends on
	        self.Rotary_counter += 1                                         # which input gave last interrupt
    	    else:                                                                           # so depending on direction either
        	self.Rotary_counter -= 1                                         # increase or decrease counter
            self.LockRotary.release()                                            # and release lock
	return                                                                                      # THAT'S IT

# Main loop. Demonstrate reading, direction and speed of turning left/rignt
    def get_volume(self):
	self.LockRotary.acquire()                                    # get lock for rotary switch
        self.NewCounter = self.Rotary_counter                     # get counter value
	self.Rotary_counter = 0                                              # RESET IT TO 0
    	self.LockRotary.release()                                    # and release lock

        if (self.NewCounter !=0):                                    # Counter has CHANGED
	    self.Volume = self.Volume + self.NewCounter*abs(self.NewCounter)        # Decrease or increase volume
    	    if self.Volume < 0:                                              # limit volume to 0...100
        	self.Volume = 0
            if self.Volume > 100:                                    # limit volume to 0...100
	        self.Volume = 100
    	    #print self.NewCounter, self.Volume                    # some test print
	    return self.Volume
	return 255

 