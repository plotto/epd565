# epd565
Preparing and sending images to the Waveshare 5.65inch ACeP 7-Color E-Paper E-Ink Display Module.

Physical Things
===============
* https://www.waveshare.com/product/displays/e-paper/5.65inch-e-paper-module-f.htm
* https://www.adafruit.com/product/2885
* https://www.adafruit.com/product/954
* https://www.adafruit.com/product/102
* https://www.adafruit.com/product/592
* https://www.tripplite.com/4-port-usb-charging-station-otg-hub-5v-6a-30w-usb-charger-output~U280004OTG
* https://www.adafruit.com/product/2810 / https://www.amazon.com/gp/product/B06Y2HKT75/
* soldering iron
* tin/lead rosin core solder
* wire snips
* hot glue gun

Initial Software
================
* https://www.raspberrypi.org/downloads/
* Python3 https://www.python.org/
* https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers


Documentation
=============
* https://www.thepolyglotdeveloper.com/2017/02/connect-raspberry-pi-pi-zero-usb-ttl-serial-cable/
* https://www.waveshare.com/wiki/5.65inch_e-Paper_Module_(F)

Process (Outline)
=================
1. Plug powered USB hub into wall, and plug Pi power into hub on a 2A out line, verify boot (power light turns on)
1. Image the SD card with Raspbian Lite
1. Enable UART in config.txt (enable_uart=1)
1. Clip the female ends off the console cable and solder it on to pi (not the red power wire though)
1. Install silabs driver on your computer
1. Put the dongle in the hub, connect Pi usb otg to hub's otg, and Pi's power on a 2A port
1. Power on the hub, plug the USB end of the console cable in, point your favorite terminal program to your new USBtoUART port (i used gnu screen: "screen /dev/cu.SLAB_USBtoUART 115200")
1. sudo raspi-config to enable spi and connect to wifi
1. verify Python3
1. install pip3
1. install $(necessary python modules)
1. "Install BCM2835 libraries"
1. "Install WiringPi libraries"
1. "Install Python3 libraries"
1. "sudo git clone https://github.com/waveshare/e-Paper"
1. verify that the python epd_5in65.py script runs -- should get stuck on "e-paper is busy" since it can't read it
1. poweroff, disassemble, clip the EPD ribbon cable female ends off and solder on to Pi
1. reassemble, log in, run epd_5in65.py verify output on screen
1. install this serial reader script (add ./screenpipe to /home/pi)
1. add the waveshare python lib folder to /home/pi/screenpipe
1. add sudo python3 $(this reader script) to /etc/rc.local
1. raspi-config disable console on serial
1. ssh for terminal as needed
1. solder red usb cable onto 5v gpio
1. i can't believe this is working, but it is
1. wbmp.py is a python (tkinter) GUI for preparing images and pushing them to the pi over the USB to Serial Console Cable
1. Screen.command can be dragged to your OSx dock as a shortcut for opening it

