# Grovepi Wordprocessor

## Background

I wanted a stand-alone wordprocessor, similar to [this one](https://www.amazon.com/Alphasmart-NEO-AA-0410-10971-AQ-Neo-Handheld/dp/B007BHWRII), meaning a device that can only be used
to type text, and absolutely nothing else (no notifications, no browser, no distractions). But I definitively wasn't willing to pay over $100 for a glorified keyboard.

I also had an old [Raspberry Pi Model B](https://en.wikipedia.org/wiki/Raspberry_Pi) and an old [GrovePI](https://www.dexterindustries.com/grovepi/) kit, both taking dust for over a decade.

Below is a description of the steps taken to make this project happen.

## Hardware

* A [Raspberry Pi](https://www.raspberrypi.com/). Tested on the 2012 model B, so should work on any regular Raspberry Pi (meaning Pico and Zero models excluded). 
* A [Grove Pi](https://www.dexterindustries.com/grovepi/) kit. Especially the board and the LCD. It looks like it's discontinued but maybe it can be found on eBay.
* A keyboard. 

## Installation

* Attach the GrovePi board on the Raspberry Pi and the LCD screen in port I2C-2 on the board
* Install **buster** on the Raspberry. Not bullseye or later.
  * Bullseye or later will **[not work](https://forum.dexterindustries.com/t/grove-pi-doesnt-work-do-not-use-raspbian-bullseye/8664)** with the GrovePi kit. Wasted a day here.
  * Buster can be downloadesd from [here](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-legacy).
  * The lite version (no desktop) is recommended since the whole point of the wordprocessor is to only display on an LCD screen.
* Run `sudo raspi-config` to:
  * Set the pi user to Console AutoLogin using (under System Options, Boot / Auto login)
  * Optional: setup Wifi. Note the Raspberry Pi Model B doesn't have Wifi natively. Need a USB adapter.
  * Recommended: enable and test ssh.
* Install [GrovePi](https://github.com/DexterInd/GrovePi). The below incantation (that bypasses the UI components) is recommended:
  `curl -kL dexterindustries.com/update_grovepi | bash -s -- --bypass-gui-installation --system-wide`
* Optional: since the goal is to have the Raspberry Pi headless but also produce some files, you want these to be either accessible or be copied to another machine.
  For example, install samba server to have the files accessible from Windows machines or samba client to have the files copied to Windows machines. I went with `sudo apt-get install smbclient`.
* Optional: setup a Bluetooth keyboard. 
  * Get a BT adapter (if Raspberry Pi older than model 2)
  * `sudo bluetoothctl`, then scan on, pair, etc.
  * You may need to trust the keyboard after to make sure it auto-connects. `sudo bluetoothctl trust <mac-address>`
* Download this repo locally, e.g. `git clone git@github.com:vdbg/grovepi-wordprocessor.git`
* Configure the script; in particular configure where it should save the files. If saving to share, configure it in `/etc/fstab` to automount
* Test the script; change paths accordingly if needed:
  `/usr/bin/python3 $HOME/grovepi-wordprocessor/word.py`
* Edit the `~/.profile` file and add the following lines at the end (with path fixed if appropriate):
```
if [[ "$(tty)" == "/dev/tty1" ]]
then
  /usr/bin/python3 $HOME/grovepi-wordprocessor/word.py
fi
```
* If logged on the console (physical monitor), press 'Ctrl-D'. This should automatically start the word processor. Now that the default tty1 console is "taken" by the word processor, you have to use CTRL+ALT+Function_Key (F1-F7) to use the other consoles.
* If logged through ssh instead, then `ps auwx  | grep bash` and kill the bash process on tty1. The wordprocessor should automatically start.
* Now, whenever the keyboard physically attached to the pi is used (possibly through bluetooth), the LCD screen should show what's typed





   