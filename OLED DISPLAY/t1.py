from machine import SPI
from machine import Pin
from ssd1306 import SSD1306_SPI

import framebuf
from framebuf import FrameBuffer

from machine import I2C #For i2c communication
from machine import sleep #
import bme280_float


# importing time module
import time


spi = SPI(1, baudrate=8000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
oled = SSD1306_SPI(128, 64, spi, dc=Pin(16), res=Pin(17), cs=Pin(18))
oled.fill(0)

with open('trisa.pbm', 'rb') as f:
    f.readline() # Magic number
    f.readline() # Creator comment
    f.readline() # Dimensions
    data = bytearray(f.read())
fbuf = framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)


oled.invert(1)
oled.blit(fbuf, 0, 0)
oled.show()


time.sleep(3.5)
oled.invert(0)

##################################

i2c = I2C(scl=Pin(22), sda=Pin(21), freq = 100000)
while True:
	bme = bme280_float.BME280(i2c=i2c)
	oled.fill(0)
	oled.text('T: '+str(bme.values[0]), 0, 0)
	oled.text('H: '+str(bme.values[1]), 0, 10)
	oled.text('P: '+str(bme.values[2]), 0, 20)
	oled.show()
	sleep(2)

