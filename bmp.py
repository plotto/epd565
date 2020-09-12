from PIL import Image
import numpy as np
from io import BytesIO
import argparse
import zipfile
import serial, time
from hashlib import md5


parser = argparse.ArgumentParser(description='Prepare an image for Waveshare 5.65inch ACeP 7-Color E-Paper E-Ink Display Module.')
parser.add_argument('-i', help='input file',required=True)
parser.add_argument('--keepPalette', help='skip fitting to eink palette (still hotswaps in the eink palette)',action="store_true")
parser.add_argument('-o', help='output file')
parser.add_argument('-r', type=float, help='red intensity scalar')
parser.add_argument('-g', type=float, help='green intensity scalar')
parser.add_argument('-b', type=float, help='blue intensity scalar')
parser.add_argument('--top', type=int, help='distance from top for crop')
parser.add_argument('--bottom', type=int, help='distance from top for crop')
parser.add_argument('--left', type=int, help='distance from left for crop')
parser.add_argument('--right', type=int, help='distance from left for crop')
parser.add_argument('--lightness', type=float, help='lighten/darken scalar')
parser.add_argument('--saturation', type=float, help='color saturation scalar')
parser.add_argument('-p', help='serial port', nargs='?',const="/dev/cu.SLAB_USBtoUART")
parser.add_argument('-br', help='serial baudrate', type=int, default=115200)
parser.add_argument('-c', help='how many times to clear-cycle the eInk screen', type=int, default=1 )
parser.add_argument('--showEinkPalette', help='show eink paletted bmp', action="store_true")
args = vars(parser.parse_args())

assert((args['left'] != None and args['right'] == None) or (args['left'] == None and args['right'] != None) or (args['left'] == None and args['right'] == None))
assert((args['top'] != None and args['bottom'] == None) or (args['top'] == None and args['bottom'] != None) or (args['top'] == None and args['bottom'] == None))
# this is the palette with the RGB values needed to drive the eink display
finalPaletteByteArray = bytearray([0x00, 0x00, 0xFF, 0x00, 0x00, 0xFF, 0x00,0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x80, 0xFF,0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00, 0xFF, 0xFF, 0xFF,0x00] * 32)

# this is the palette with the actual display colors, used for dithering accurately
paletteImage = Image.new('P', (1, 1))
#paletteImage.putpalette([int(x) for x in [0x78, 0x40, 0x43, 0x32, 0x5C, 0x3D, 0x35, 0x3F, 0x56, 0xAB, 0x9E, 0x54, 0xA4, 0x75, 0x4D, 0x30, 0x30, 0x30, 0xAF, 0xAF, 0xAF, 0xAF, 0xAF, 0xAF]] * 32)

#paletteImage.putpalette([int(x) for x in [0x92, 0x5a, 0x5d, 0x50, 0x73, 0x54, 0x52, 0x5b, 0x74, 0xad, 0xa4, 0x68, 0xa5, 0x7e, 0x61, 0x20, 0x20, 0x20, 0xb1, 0xb1, 0xb2, 0xb1, 0xb1, 0xb2]] * 32)

paletteImage.putpalette([int(x) for x in [0x92, 0x5a, 0x5d, 0x50, 0x73, 0x54, 0x52, 0x5b, 0x74, 0xa0, 0xa0, 0x60, 0xa5, 0x7e, 0x61, 0x20, 0x20, 0x20, 0xb1, 0xb1, 0xb2, 0xb1, 0xb1, 0xb2]] * 32)

# target image size
(targetwidth, targetheight) = (600.0, 448.0)

# open the image and make sure it's in RGB mode
im = Image.open(args['i'])
im = im.convert("RGB")

#crop arguments


# rotate to horizontal
(width, height) = im.size
if width < height:
  im = im.transpose(Image.ROTATE_90)
  (width, height) = im.size
  if args['top'] != None or args['left'] != None:
    temp = args['left']
    args['left'] = args['top']
    args['top'] = temp
 

# resize and crop based on relative aspect ratio to make
#   sure there is no empty space
# todo: add top/left args for positioning the crop
# if it's too tall, fit on width and crop height
if width/height < targetwidth/targetheight:
  percent = targetwidth / float(width)
  im = im.resize((int(width * percent),int(height * percent)))
  left = 0
  if args['top'] != None:
    top = args['top']
  elif args['bottom'] != None:
    top = int(height * percent) - args['bottom'] - 448
  else:
    top = int((height * percent - targetheight) / 2)
  right = 600
  if args['top'] != None:
    bottom = args['top'] + 448
  elif args['bottom'] != None:
    bottom = int(height * percent) - args['bottom']
  else:
    bottom = int((height * percent - targetheight) / 2) + 448
  im = im.crop((left,top,right,bottom))
# if it's too wide, fit on height and crop width
else:
  percent = targetheight / float(height)
  im = im.resize((int(width * percent),int(height * percent)))
  if args['left'] != None:
    left = args['left']
  elif args['right'] != None:
    left = int(width * percent) - args['right'] - 600
  else:
    left = int((width * percent - targetwidth) / 2)
  top = 0
  if args['left'] != None:
    right = args['left'] + 600
  elif args['right'] != None:
    right = int(width * percent) - args['right']
  else:
    right = int((width * percent - targetwidth) / 2) + 600
  bottom = 448
  im = im.crop((left,top,right,bottom))

# process lightness/darkness options
if args['lightness']:
  for chan in ('r','g','b'):
    args[chan] = args['lightness'] if args[chan] == None else args[chan] * args['lightness']
  
# allow for color intensity options
if args['r'] != None or args['g'] != None or args['b'] != None:
  (r,g,b) = [np.array(chan,dtype=np.uint16) for chan in im.split()]
  channels = { 'r': r, 'g': g, 'b': b }
  for chan in channels:
    if args[chan] != None:
      channels[chan] = channels[chan] * args[chan]
      channels[chan] = channels[chan].clip(0,255)
  im = Image.merge("RGB",[Image.fromarray(channels[chan].astype(np.uint8)) for chan in ('r','g','b')])

if args['saturation'] != None:
  im = im.convert('HSV')
  (h,s,v) = [np.array(chan,dtype=np.uint16) for chan in im.split()]
  s = s * args['saturation']
  channels = { 'h': h, 's': s, 'v': v }
  im = Image.merge("HSV",[Image.fromarray(channels[chan].astype(np.uint8)) for chan in ('h','s','v')])
  im = im.convert("RGB")

# convert input image to real color dithered
if not args["keepPalette"]:
  im.load()
  paletteImage.load()
  newim = im.im.convert("P",True,paletteImage.im)
  im = im._new(newim)

if not args["o"] and not args["p"] and not args["showEinkPalette"]:
  im.show()

# get the dithered images bytes and hot swap out the real color
#   palette for the eink color palette
ba = BytesIO()
im.save(ba, format='BMP')
ba = bytearray(ba.getvalue())
ba[54:1078] = finalPaletteByteArray

# reload bytes as an image, and convert again to RGB to mimic the eink demo bmp
# which had a palette but also RGB values for each pixel
# todo: is this necessary?
im = Image.open(BytesIO(ba))
im = im.convert("RGB")
if not args["o"] and not args["p"] and args["showEinkPalette"]:
  im.show()

# save to file?
if args["o"]:
  im.save(args["o"],format="BMP")

# send to serial?
if args["p"]:
  # zip the file in memory
  ba = BytesIO()
  im.save(ba,format='BMP')
  infile = BytesIO()
  zf = zipfile.ZipFile(infile,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9)
  zf.writestr("transfer.bmp",ba.getvalue())
  zf.close()
  infile.seek(0)

  # open the port for ascii handshake
  s = serial.Serial(port=args["p"],baudrate=args["br"])
  transmission = b''
  print("Listening on serial port...")
  while not transmission == b'LISTENING\n':
    transmission = s.readline()
    if transmission == b'WAITING\n':
      s.write(b'HANDSHAKE\n')
      transmission = s.readline()
      print("Heard: "+transmission.decode("ascii"))
  
  # how many times to clear-cycle eInk screen
  for i in range(0,args["c"]):
    print("Sending .Clear()")
    s.write(b'\x01'*1024)

  # zend the file 1024 bytes at a time, verifying md5 checksum each time
  i = 0
  while True:
    kb = infile.read(1024)
    i = i + 1
    # receiving port will wait forever to consume 1024 bytes, so pad
    # the last kb of the file out to 1024 with null bytes if necessary
    #
    # this also means that once the file is exhausted we will be sending
    # 1024 null bytes, which will signal completion and trigger shutdown
    while len(kb) < 1024:
      kb += b'\x00'

    verified = False
    j = 1
    while not verified:
      s.write(kb)

      # verify md5 checksums agree
      checksum = md5(kb)
      rec = s.read(checksum.digest_size)
      if rec == checksum.digest():
        s.write(b'+')
        print(str(i)+". Good")
        verified = True
      else:
        s.write(b'-')
        print(str(i)+". Try Again ("+str(j)+")")

    # if 1024 null bytes then we are past EOF
    if kb == b'\x00'*1024:
      break
  
  infile.close()
  s.close()


