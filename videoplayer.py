#!/usr/bin/python3

import sys
import subprocess
import RPi.GPIO as GPIO
import time
import os
import glob

try:
    sys.path.append('/home/pi/Videos/')
    from playlist import vids
except ImportError:
    vids = sorted(glob.glob('/home/pi/Videos/*.*'))


pin_shutdown = 24
pin_stop = 23


def doAndRetry(fn, n_retries, interval_sec):
    for i in range(n_retries):
        try:
            fn()
        except Exception as e:
            print("exception: {e}; retry {i}/{max}"
                  .format(e = e, i= i + 1, max = n_retries))
            time.sleep(i * interval_sec)
        else:
            break

class VideoPlayer:
    def __init__(self):
        self.proc = None
        self.state_stop = False

    def stopVideo(self):
        os.system("TERM=linux sudo setterm -blank poke < /dev/tty1")
        if self.proc is not None and self.proc.poll() is None:
            self.proc.stdin.write('q')
            self.proc.stdin.flush()
            print("q sent")
        self.state_stop = True
    
    def callBackShutdown(self, channel):
        time.sleep(1)
        if GPIO.input(pin_shutdown) == 0:
            self.stopVideo()
            print("shutting down")
            os.system("sudo echo shutting down... > /dev/tty1")
            time.sleep(1)
            os.system("sudo shutdown -h now")
    
    def callBackStop(self, channel):
        time.sleep(1)
        if GPIO.input(pin_stop) == 0:
            self.stopVideo()
            print("stop")
        else:
            self.state_stop = False
            print("play")
    
    def mainLoop(self):
        n_vids = len(vids)
        k = 0
        while True:
            if self.state_stop == True:
                time.sleep(1)
                continue

            def blankTerminal():
                subprocess.check_call(
                    "TERM=linux sudo setterm -blank force < /dev/tty1", 
                    shell=True
                )
            doAndRetry(blankTerminal, n_retries = 5, interval_sec = 10)
    
            cmd = "omxplayer -o local %s" % vids[k]
            print(cmd)
            self.proc = subprocess.Popen(cmd, shell=True, 
                                         stdin=subprocess.PIPE, 
                                         universal_newlines=True)
            self.proc.wait()
            k = (k + 1) % n_vids

if __name__ == "__main__":
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
    vp = VideoPlayer();

    print("initializing GPIO...")
    def initGPIO():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_stop, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(pin_shutdown, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(pin_stop, GPIO.BOTH, 
                              callback=vp.callBackStop, bouncetime=300) 
        GPIO.add_event_detect(pin_shutdown, GPIO.FALLING, 
                              callback=vp.callBackShutdown, bouncetime=300)
    doAndRetry(initGPIO, n_retries = 5, interval_sec = 5)

    try:
        print("main")
        vp.mainLoop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("KeyboardInterrupt")
