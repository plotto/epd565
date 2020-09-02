The Story
=========

Broadly, I am very annoyed at being unable to read a screen in direct sunlight.  More specifically I love non-emissive screens.  Aside: I set an alarm for 4am long ago to make sure i got an [OLPC XO](http://one.laptop.org/about/hardware) buy-two/get-one.  Still have that machine, my 3-4 year old loves it -- though i had to get an external [toddler mouse](https://www.amazon.com/ChesterMouse-AbleNet-Chester-Computers-CCT/dp/B004001QTU) since that trackpad is garbage.  To that end I've long been a follower and fan of eink technology, though for a long long time it seemed like dedicated readers were the only viable product for it.  More recently I was particularly interested in the dual screen (yottaphone 3)[https://www.theverge.com/circuitbreaker/2017/8/24/16196766/yotaphone-3-specs-release-price] though I never could tell if i could use it states-side.  Ultimately I bought into (LightPhone 2)[https://www.thelightphone.com/products] (my first smartphone!) and I'm very happy with it (strong caveat: i came to it from no prior use of smart phones.  i had a complete piece of shit alcatel go flip, so the sluggish response and at times difficult texting experience with light phone 2 was still a vast improvement over what i was used to.  if you are a power-texter you probably will not enjoy the experience.)   

so when (this)[https://news.ycombinator.com/item?id=23898523] story popped up on HN about an affordable consumer-facing /seven color/ display, i had to jump.  i ordered it despite having almost zero experience hobbying with hardware.  i've built my own computers, i'm a application developer by title, but i've never really dabbled in pin-outs and shit since my aborted undergraduate foray into ComputerE almost twenty years ago.

the display arrived, and i took a look at it.  ribbon cable, screen, not much else.  okay, time to think.  what am i doing, and how will i do it.

ever since digital photo frames hit the market i thought they were a cool idea, but completely ruined by being 1. emissive and 2. corded.  okay, here's my chance to build the product i always wanted.  i'm going to build an unplugged digital photoframe.  

i dug into waveshare's wiki (which is great!) and got the notion that a low-powered dedicated microcontroller (am i even using that term correctly?) would be ideal.  but further digging demonstrated that waveshare has resources built and demo scripts written for only a subset of devices.  one of which is raspberry pi.  okay, that's another device i've always thought was slick sounding but have never had a use for.  pi it is!

looking at the pi options and considering my use case, the raspberry pi zero (no W) was clearly my pick.  least amount of capabilities == least amount of power draw == lowest profile (i want to hide this behind a frame flush to the wall).  but this is also going to mean soldering.  i have soldering stuff, i've done it once before to fix a radio, i made a mess, melted some plastic, but was ultimately succesful.  plus it's 5 bucks, if i fuck it up i can try again.

i don't have a spare screen, nor do i have a monitor with hdmi in/out at all.  i don't want to buy one for this, so what do i do?  turns out you can solder a usb adapter direct to the pi to get terminal over serial -- also that cord can supply the pi with power.  fucking sick, i've got my i/o and my power all in one port, this is ideal for my end-product.  i ponder for a while how best to transfer various python libraries and the waveshare code over this serial connection before i decide that for development's sake, i'm going to need wifi at least just for the dev part.  some other blog links me to this powered usb-on-the-go hub which seems ideal for what i'm doing.  time to make my order: pi zero, console cable, an usb-to-mini power cable, some extra wire just in case, powered hub, compatible wifi dongle (well, that i got later, i thought the one i had would work but it didn't).  

first step is soldering on the serial adapter (not the power line yet) and seeing if it boots.  
next step is figuring out how to fucking talk on serial.  i don't have any experience with this.  polyglotdeveloper blog walks me through it.

it lives!

