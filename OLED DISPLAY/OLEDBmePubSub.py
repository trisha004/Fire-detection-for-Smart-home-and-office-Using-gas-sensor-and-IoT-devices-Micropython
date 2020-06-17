from machine import SPI
from machine import Pin
from ssd1306 import SSD1306_SPI
import framebuf
import bme280_float
from framebuf import FrameBuffer
from machine import I2C  # For i2c communication
from machine import sleep  #
# importing time modul
import time
import network
import time
from umqtt.robust import MQTTClient
import os
import gc
import sys
def go():
    spi = SPI(1, baudrate=8000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    oled = SSD1306_SPI(128, 64, spi, dc=Pin(16), res=Pin(17), cs=Pin(18))
    oled.fill(0)

    with open('trisa.pbm', 'rb') as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        f.readline()  # Dimensions
        data = bytearray(f.read())
    fbuf = framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)

    oled.invert(1)
    oled.blit(fbuf, 0, 0)
    oled.show()

    time.sleep(3.5)
def cb(topic, msg):
    print('Subscribe:  Received Data:  Topic = {}, Msg = {}\n'.format(topic, msg))
    free_heap = int(str(msg, 'ascii'))  # converted from'utf-8 2nd parameter


# WiFi connection information
WIFI_SSID = 'Bela Guest'
WIFI_PASSWORD = 'Beluest'

# turn off the WiFi Access Point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# connect the device to the WiFi network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

# wait until the device is connected to the WiFi network
MAX_ATTEMPTS = 20
attempt_count = 0
while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    time.sleep(1)

if attempt_count == MAX_ATTEMPTS:
    print('could not connect to the WiFi network')
    sys.exit()

# create a random MQTT clientID
random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id = bytes('client_' + str(random_num), 'ascii')  # ' converted from utf-8 2nd parameter

# connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
#
# To use a secure connection (encrypted) with TLS:
#   set MQTTClient initializer parameter to "ssl=True"
#   Caveat: a secure connection uses about 9k bytes of the heap
#         (about 1/4 of the micropython heap on the ESP8266 platform)
ADAFRUIT_IO_URL = b'io.adafruit.com'
ADAFRUIT_USERNAME = b'Belancer1st'
ADAFRUIT_IO_KEY = b'9a1482d0b59c4d86bd935007855b612d'
ADAFRUIT_IO_FEEDNAME = b'hmd'
ADAFRUIT_IO_FEEDNAME1 = b'subs'
ADAFRUIT_IO_FEEDNAME2 = b'tmp'
ADAFRUIT_IO_FEEDNAME3 = b'prs'

client = MQTTClient(client_id=mqtt_client_id,
                    server=ADAFRUIT_IO_URL,
                    user=ADAFRUIT_USERNAME,
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)

try:
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()

# publish free heap statistics to Adafruit IO using MQTT
# subscribe to the same feed
#
# format of feed name:
#   "ADAFRUIT_USERNAME/feeds/ADAFRUIT_IO_FEEDNAME"
mqtt_feedname = bytes('{:s}/f/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME),
                      'ascii')  # converted from 'ustf-8' 2nd parameter
mqtt_feedname1 = bytes('{:s}/f/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME1),
                       'ascii')  # converted from' ustf-8' 2nd parameter
mqtt_feedname2 = bytes('{:s}/f/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME2),
                      'ascii')  # converted from 'ustf-8' 2nd parameter
mqtt_feedname3 = bytes('{:s}/f/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME3),
                      'ascii')  # converted from 'ustf-8' 2nd parameter

client.set_callback(cb)
client.subscribe(mqtt_feedname1)
PUBLISH_PERIOD_IN_SEC = 10
SUBSCRIBE_CHECK_PERIOD_IN_SEC = 0.5
accum_time = 0
def go():
    spi = SPI(1, baudrate=8000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    oled = SSD1306_SPI(128, 64, spi, dc=Pin(16), res=Pin(17), cs=Pin(18))
    oled.fill(0)

    with open('trisa.pbm', 'rb') as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        f.readline()  # Dimensions
        data = bytearray(f.read())
    fbuf = framebuf.FrameBuffer(data, 128, 64, framebuf.MONO_HLSB)

    oled.invert(1)
    oled.blit(fbuf, 0, 0)
    oled.show()

    time.sleep(3.5)
    i2c = I2C(scl=Pin(22), sda=Pin(21), freq = 100000)
    while True:
        oled.invert(0)
        oled.fill(0)
        oled.text('T: ' + str(bme.values[0]), 0, 0)
        oled.text('H: ' + str(bme.values[1]), 0, 10)
        oled.text('P: ' + str(bme.values[2]), 0, 20)
        oled.show()
        sleep(2)
        try:
            accum_time = 0
            # Publish
            if accum_time >= PUBLISH_PERIOD_IN_SEC:
                # free_heap_in_bytes = gc.mem_free()
                value_to_be_published = oled.show()
                print('Publish:  Published Value = {}'.format(value_to_be_published))
                client.publish(mqtt_feedname,
                               bytes(str(value_to_be_published), 'ascii'),
                               qos=0)  # converted from 'utf-8' 2nd parameter
                accum_time = 0

            # Subscribe.  Non-blocking check for a new message.
            client.check_msg()

            time.sleep(SUBSCRIBE_CHECK_PERIOD_IN_SEC)
            accum_time += SUBSCRIBE_CHECK_PERIOD_IN_SEC
        except KeyboardInterrupt:
            print('Ctrl-C pressed...exiting')
            client.disconnect()
            sys.exit()
go()