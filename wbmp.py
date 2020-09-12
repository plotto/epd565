import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
import numpy as np
from io import BytesIO
import zipfile
import serial
from hashlib import md5
from math import ceil
from sys import exit
import tkinter as tk
import tkinter.filedialog as fd

activeColors = ["R","G","B","Y","O","K","W"]
eInkDrivingPaletteBytes= { "R": [0x00, 0x00, 0xFF, 0x00], "G": [0x00, 0xFF, 0x00, 0x00], "B": [0xFF, 0x00, 0x00, 0x00], "Y": [0x00, 0xFF, 0xFF, 0x00], "O": [0x00, 0x80, 0xFF, 0x00], "K": [0x00, 0x00, 0x00, 0x00], "W": [0xFF, 0xFF, 0xFF, 0xFF] }
eInkTruePaletteBytes= { "R": [0x5D, 0x5A, 0x92, 0x00], "G": [0x54, 0x73, 0x50, 0x00], "B": [0x74, 0x5B, 0x52, 0x00], "Y": [0x60, 0xA0, 0xA0, 0x00], "O": [0x61, 0x7E, 0xA5, 0x00], "K": [0x40, 0x40, 0x40, 0x00], "W": [0xB2, 0xB1, 0xB1, 0x00] }
targetPalette= { "R": [0x92, 0x5a, 0x5d], "G": [0x50, 0x73, 0x54], "B": [0x52, 0x5b, 0x74], "Y": [0xa0, 0xa0, 0x60], "O": [0xa5, 0x7e, 0x61], "K": [0x20, 0x20, 0x20], "W": [0xb1, 0xb1, 0xb2] }

# this is the palette with the actual display colors, used for dithering accurately
paletteImage = Image.new('P', (1, 1))
#paletteImage.putpalette([int(x) for x in [0x78, 0x40, 0x43, 0x32, 0x5C, 0x3D, 0x35, 0x3F, 0x56, 0xAB, 0x9E, 0x54, 0xA4, 0x75, 0x4D, 0x30, 0x30, 0x30, 0xAF, 0xAF, 0xAF, 0xAF, 0xAF, 0xAF]] * 32)
#paletteImage.putpalette([int(x) for x in [0x92, 0x5a, 0x5d, 0x50, 0x73, 0x54, 0x52, 0x5b, 0x74, 0xad, 0xa4, 0x68, 0xa5, 0x7e, 0x61, 0x20, 0x20, 0x20, 0xb1, 0xb1, 0xb2, 0xb1, 0xb1, 0xb2]] * 32)

# target image size
(targetwidth, targetheight) = (600.0, 448.0)
im = None
root = tk.Tk()
root.file = fd.askopenfilename(initialdir="/Users/thomjc/Downloads", title="Select file")
im = Image.open(root.file)
im = im.convert("RGB")

(width, height) = im.size
# resize
if height > width:
  for i in range(3): im = im.transpose(Image.ROTATE_90)
(width, height) = im.size
if width/height < targetwidth/targetheight:
  percent = targetwidth / float(width)
  im = im.resize((int(width * percent),int(height * percent)))
# if it's too wide, fit on height and crop width
else:
  percent = targetheight / float(height)
  im = im.resize((int(width * percent),int(height * percent)))
(width, height) = im.size

original = im.copy()
thumbnail = original.resize((int(width /2.0), int(height /2.0)))
ogThumbnail = im.resize((int(width /2.0), int(height /2.0)))

def dither(img):
  dithered = img.copy()
  # convert input image to real color dithered
  paletteImage.putpalette(([int(byte) for colorBytes in [targetPalette[color] for color in activeColors] for byte in colorBytes] * ceil(768.0/(len(activeColors)*3)))[:768])

  dithered.load()
  paletteImage.load()
  newim = dithered.im.convert("P",True,paletteImage.im)
  return dithered._new(newim)

def ditherPreview(img):
  expected = dither(img)
  ba = BytesIO()
  expected.save(ba, format='BMP')
  ba = bytearray(ba.getvalue())
  ba[54:1078] = bytearray(([byte for colorBytes in [eInkTruePaletteBytes[color] for color in activeColors] for byte in colorBytes] * ceil(1024.0/(len(activeColors)*4)))[:1024])
  #ba[54:1078] = expectedColorByteArray
  
  # reload bytes as an image, and convert again to RGB to mimic the eink demo bmp
  # which had a palette but also RGB values for each pixel
  # todo: is this necessary?
  expected = Image.open(BytesIO(ba))
  return expected # eink.convert("RGB")
  

def toEink(img):
  # get the dithered images bytes and hot swap out the real color
  #   palette for the eink color palette
  ba = BytesIO()
  eink = img.copy()
  eink.save(ba, format='BMP')
  ba = bytearray(ba.getvalue())
  ba[54:1078] = bytearray(([byte for colorBytes in [eInkDrivingPaletteBytes[color] for color in activeColors] for byte in colorBytes] * ceil(1024.0/(len(activeColors)*4)))[:1024])
  
  # reload bytes as an image, and convert again to RGB to mimic the eink demo bmp
  # which had a palette but also RGB values for each pixel
  # todo: is this necessary?
  eink = Image.open(BytesIO(ba))
  return eink.convert("RGB")

# send to serial?
def pushToSerial(caller=None):
  img = toEink(dither(editColors(original)))
  img = img.crop((left.get(), top.get(),left.get() + 600,top.get() + 448))
  # zip the file in memory
  ba = BytesIO()
  img.save(ba,format='BMP')
  infile = BytesIO()
  zf = zipfile.ZipFile(infile,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9)
  zf.writestr("transfer.bmp",ba.getvalue())
  zf.close()
  infile.seek(0)

  # open the port for ascii handshake
  s = serial.Serial(port=port.get().split(" ")[0],baudrate=int(port.get().split(" ")[1]))
  transmission = b''
  print("Listening on serial port...")
  while not transmission == b'LISTENING\n':
    transmission = s.readline()
    if transmission == b'WAITING\n':
      s.write(b'HANDSHAKE\n')
      transmission = s.readline()
      print("Heard: "+transmission.decode("ascii"))
  
  # how many times to clear-cycle eInk screen
  for i in range(0,int(clear.get())):
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
  exit(0)

def updateThumbnails(caller=None):
  manipulated = editColors(thumbnail)
  draw = ImageDraw.Draw(manipulated)
  if width > 600:
    if left.get() > 0:
      draw.rectangle((0,0,left.get() /2.0,448),fill=tuple([int(x) for x in targetPalette[activeColors[0]]]))
    if left.get() + 600 < width:
      draw.rectangle(((left.get() + 600) /2.0 , 0, width / 2.0, 448),fill=tuple([int(x) for x in targetPalette[activeColors[0]]]))
  if height > 448:
    if top.get() > 0:
      draw.rectangle((0,0,600,top.get() /2.0),fill=tuple([int(x) for x in targetPalette[activeColors[0]]]))
    if top.get() + 448 < height:
      draw.rectangle((0, (top.get() + 448) /2.0 , 600, height / 2.0),fill=tuple([int(x) for x in targetPalette[activeColors[0]]]))

  for i in range(rotations):
    manipulated = manipulated.transpose(Image.ROTATE_90)

  manipulatedTk = ImageTk.PhotoImage(manipulated)
  manipulatedColor.configure(image= manipulatedTk)
  manipulatedColor.img = manipulatedTk

  dithered = ditherPreview(manipulated)
  ditheredTk = ImageTk.PhotoImage(dithered)
  ditheredColor.configure(image= ditheredTk)
  ditheredColor.img = ditheredTk

  einked = toEink(dithered)
  einkedTk = ImageTk.PhotoImage(einked)
  einkedColor.configure(image= einkedTk)
  einkedColor.img = einkedTk
  
  
def editColors(img):
  edited = img.copy()

  # allow for color intensity options
  (r,g,b) = [np.array(chan,dtype=np.uint16) for chan in edited.split()]
  channels = { 'r': r, 'g': g, 'b': b }
  for chan in channels:
    channels[chan] = channels[chan] * colorChannels[chan].get()/100.0
    channels[chan] = channels[chan].clip(0,255)
  edited = Image.merge("RGB",[Image.fromarray(channels[chan].astype(np.uint8)) for chan in ('r','g','b')])

  saturator = ImageEnhance.Color(edited)
  edited = saturator.enhance(saturation.get()/100.0)

  lightnessor = ImageEnhance.Brightness(edited)
  edited = lightnessor.enhance(lightness.get()/100.0)
  
  contrastor = ImageEnhance.ContrastEink(edited)
  edited = contrastor.enhance(contrast.get()/100.0)
  
  return edited

def saveDithered(caller=None,suppressShow=False):
  img = dither(editColors(original))
  img = img.crop((left.get(), top.get(),left.get() + 600,top.get() + 448))
 # img.save("out.dither.bmp")
  if not suppressShow: img.show()
  return img
  
def saveEinked(caller=None,suppressShow=False):
  img = toEink(dither(editColors(original)))
  img = img.crop((left.get(), top.get(),left.get() + 600,top.get() + 448))
#  img.save("out.einked.bmp")
  if not suppressShow: img.show()
  return img

rotations = 0
def rot90(caller=None):
  global rotations, ogThumbnail
  rotations = (rotations + 1) % 4
  updateThumbnails()
  ogThumbnail = ogThumbnail.transpose(Image.ROTATE_90)
  originalTk = ImageTk.PhotoImage(ogThumbnail)
  originalColor.configure(image=originalTk)
  originalColor.img = originalTk


def toggleColor():
  global activeColors
  activeColors = []
  for color in activeColorVars:
    if activeColorVars[color].get():
      activeColors.append(color)
  updateThumbnails()


# GUI GUI GUI
column = 0
def nextColumn(colspan=1,reset=False,suppressIncrement=False):
  global column
  if reset: column = 0
  current = column
  if not suppressIncrement: column += colspan
  return current

#root = tk.Tk()
main = tk.Frame(root)
main.grid()

toolbar = tk.Frame(main)
toolbar.grid(row=0, column = 0)

saturation = tk.DoubleVar()
saturation.set(100)
tk.Scale(toolbar,variable = saturation, from_=200, to=0, command=updateThumbnails).grid(row=0, column=nextColumn(reset=True,suppressIncrement=True), columnspan=2)
tk.Label(toolbar, text="Saturation%").grid(row=1, column=nextColumn(colspan=2), columnspan=2)

lightness = tk.DoubleVar()
lightness.set(100)
tk.Scale(toolbar,variable = lightness, from_=200, to=0, command=updateThumbnails).grid(row=0, column=nextColumn(suppressIncrement=True), columnspan=2)
tk.Label(toolbar, text="Lightness%").grid(row=1, column=nextColumn(colspan=2), columnspan=2)

contrast = tk.DoubleVar()
contrast.set(100)
tk.Scale(toolbar,variable = contrast, from_=200, to=0, command=updateThumbnails).grid(row=0, column=nextColumn(suppressIncrement=True), columnspan=2)
tk.Label(toolbar, text="Contrast").grid(row=1, column=nextColumn(colspan=2), columnspan=2)


colorChannels={}
for color in ('r','g','b'):
  colorChannels[color] = tk.DoubleVar()
  colorChannels[color].set(100)
  tk.Scale(toolbar,variable = colorChannels[color], from_=200, to=0, command= updateThumbnails).grid(row = 0, column = nextColumn(suppressIncrement=True))
  tk.Label(toolbar, text=color.upper()+"%").grid(row = 1, column = nextColumn())

top = tk.DoubleVar()
top.set(int((height - 448.0)/2.0))
tk.Scale(toolbar,variable = top, from_=0, to=max(0,height-448), command= updateThumbnails).grid(row = 0, column = nextColumn(suppressIncrement=True))
tk.Label(toolbar, text="Top").grid(row = 1, column = nextColumn())

left = tk.DoubleVar()
left.set(int((width - 600)/2.0))
tk.Scale(toolbar,variable = left, from_=0, to=max(0,width-600), command= updateThumbnails).grid(row = 0, column = nextColumn(suppressIncrement=True))
tk.Label(toolbar, text="Left").grid(row = 1, column = nextColumn())

tk.Button(toolbar,text="Rotate",command=rot90,highlightbackground='#3E4149').grid(row=0,column=nextColumn())

activeColorVars = {}
for color in ('R','G','B','Y','O','W','K'):
  activeColorVars[color] = tk.IntVar()
  activeColorVars[color].set(1)
  tk.Checkbutton(toolbar, variable = activeColorVars[color], text=color, bg="gray", command=toggleColor).grid(row = 0, column = nextColumn())

# frame for displaying current edits
images = tk.Frame(main)
images.grid(row=1,column=0)

originalTk = ImageTk.PhotoImage(ogThumbnail)
originalColor = tk.Label(images,image=originalTk)
originalColor.img = originalTk
originalColor.grid(row=0,column=0)

manipulatedColor = tk.Label(images)
manipulatedColor.grid(row=0,column=1)

ditheredColor = tk.Label(images)
ditheredColor.grid(row=1,column=0)

einkedColor = tk.Label(images)
einkedColor.grid(row=1,column=1)

# Bottom toolbar for saving and exiting
finish = tk.Frame(main)
finish.grid(row=2,column=0)

tk.Button(finish,text="Export Dithered",highlightbackground='#3E4149',command=saveDithered).grid(row=0,column=0)
tk.Button(finish,text="Export eInked",highlightbackground='#3E4149',command=saveEinked).grid(row=0,column=1)

port = tk.StringVar()
port.set("/dev/cu.SLAB_USBtoUART 115200")
tk.Entry(finish,highlightbackground='#3E4149',textvariable=port,width=len(port.get())).grid(row=0,column=2)

clear = tk.StringVar()
clear.set("1")
tk.Entry(finish,highlightbackground='#3E4149',textvariable=clear,width=2).grid(row=0,column=3)

tk.Button(finish,text="Push",highlightbackground='#3E4149',command=pushToSerial).grid(row=0,column=4)
tk.Button(finish,text="Exit",highlightbackground='#3E4149',command=lambda *args: exit(0)).grid(row=0,column=5);

# fire it up!
updateThumbnails()
root.mainloop()

