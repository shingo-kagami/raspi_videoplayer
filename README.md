# Raspberry Pi Endless Video Player

## Installation for 2018-06-27-raspbian-stretch-lite in Raspberry Pi Zero W

- Uncomment `hdmi_force_hotplug=1` in `/boot/config.txt`
- Add ` consoleblank=600` (or any of your favorite duration in second) at the end of `/boot/cmdline.txt`
- Choose `console autologin` by running `raspi-config` (Boot Option - Desktop / CLI)
- Install `omxplayer` and `python3-rpi.gpio` by `apt-get`
- Put `videoplayer.py` (the file distributed here) at `~pi/script/`
- Put video files in `~pi/Videos/`, which are played in the dictionary order of the file names.
  - Optionally, you can put `playlist.py` (the file distributed here) in `~pi/Videos/` and specify the file names to be played in this file.
- Add the following line in crontab of user `pi` by running `crontab -e`:
```
@reboot	/home/pi/script/videoplayer.py > /dev/null 2>&1 &
```

## Operation

- Connect HDMI output to a display and power input (or USB input) to 5V power source; The videos are automatically started.

- Connect BCM 23 (Pin 16 in Pi Zero) to Gnd (e.g. Pin 14) to stop playing; Let the pin open to start again from the next video.
- Connect BCM 24 (Pin 18 in Pi Zero) to Gnd to shut down the OS.
