import serial
from hashlib import md5
from io import BytesIO
import zipfile
import sys
import os
from subprocess import call
#picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
#libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
picdir = "/home/pi/screenpipe/pic"
libdir = "/home/pi/screenpipe/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd5in65f
import time
from PIL import Image,ImageDraw #,ImageFont
import traceback
epd = epd5in65f.EPD()
logging.info("init and Clear")
epd.init()

logging.basicConfig(level=logging.DEBUG)
print("broadcasting on port")
port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
#broadcast i'm alive and wait for a response
transmission = b''
while not transmission == b'HANDSHAKE\n':
  port.write(b'WAITING\n')
  transmission = port.readline()
port.close()
port = serial.Serial("/dev/ttyAMA0", baudrate=115200)
port.write(b'LISTENING\n')
zfba = BytesIO()
i = 0
while True:
  print("waiting on data")
  transmission = port.read(1024)
  print("data received "+str(len(transmission)))
  if transmission == b'\x01'*1024:
    epd.Clear()
    continue
  checksum = md5(transmission)
  print("sending checksum ("+checksum.hexdigest()+")")
  port.write(checksum.digest())
  print("waiting verified")
  verify = port.read(1)
  check = (verify == b'+')
  if not check:
    print("try again" + str(i+1))
    continue
  elif transmission == b'\x00'*1024:
    port.close()
    zfba.seek(0)
    break
  elif len(transmission) > 0:
    zfba.write(transmission)
    i += 1
    print(i)

zf = zipfile.ZipFile(zfba,"r")
outfile = open(os.path.join(picdir,"transfer.bmp"),"wb")
outfile.write(zf.read("transfer.bmp"))
outfile.close()
zfba.close()

try:
  
  logging.info("3.read bmp file")
  Himage = Image.open(os.path.join(picdir, "transfer.bmp"))
  epd.display(epd.getbuffer(Himage))
  logging.info("Goto Sleep...")
  epd.sleep()


except IOError as e:
  logging.info(e)
    
except KeyboardInterrupt:    
  logging.info("ctrl + c:")
  epd5in65f.epdconfig.module_exit()
  exit()

call("sudo shutdown -h now", shell=True)


