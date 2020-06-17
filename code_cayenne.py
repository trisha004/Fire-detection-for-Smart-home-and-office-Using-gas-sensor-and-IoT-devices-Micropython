##############################################################
""" 
# Author : Trisha
# Date: 17 April 2019
# Operation: Loads Static logo , displays BME280 parameters , Uploads Data to Adafruit IO MQTT Server

# Dependency File : 
#           config
    
    

# Main Dependency Libraries :
#           bme280_float #https://github.com/robert-hh/BME280
#           SSD1306_SPI
#           telegram_api_lite

# MQTT Implementation code from Mike Teachman

# Whats new :
#            18-04-2019
#            Wifi connect code optimized with multiple retry attempts
#            Const Inplemented on Numerical Values
#
#            20-04-2019
#            Non Blocking code on Publish
#            Non Blocking code on Subscribe
#
#            22-04-2019
#            import library bloat reduced..but few remains
#            Now HW Pin #'s in Const

#            26-04-2019
#            Configuration file has benn implimented to the system as config.py


# ToDo: 
"""

#############################################################

#-------------- Start of Import -----------------
from machine import SPI,Pin,I2C,sleep,freq,ADC
from ssd1306 import SSD1306_SPI

import framebuf
from framebuf import FrameBuffer # ??? cant optimize here ???

import bme280_float #https://github.com/robert-hh/BME280
#from bme280_float import bme280
import time
#from time import sleep, ticks_diff, ticks_ms ??? # ???? cant optimize here


from umqtt.robust import MQTTClient
import os
from os import urandom
import gc
import sys
from sys import exit

# For WiFi
#from network import WLAN, STA_IF 
#import network ??? How to make this more optimized ??
from network import WLAN, STA_IF ,AP_IF

import telegram_api_lite #

#from time import sleep #for waiting some times

# ------------ End of Import -------------------

import config

IS_WIFI_CONNECTED = False
IS_MQTT_SERVER_CONNECTED = True #To publish or subscribe data to IoT server

#-----------------------

def cb(topic, msg):
    print('Subscribe:  Received Data:  Topic = {}, Msg = {}\n'.format(topic, msg))
    value = msg[-1:]
    pin4 = Pin(config.RELAY_GPIO_PIN, Pin.OUT)
    if value == b'0':
        pin4.off()
        print('Relay is OFF now')
    elif value == b'1':
        pin4.on()
        print('Relay is ON now')
    else:
        print('Not working')


#---Setup SPI Bus for OLED Display	
spi = SPI(1, baudrate=config.SPI_BAUD_RATE, polarity=0, phase=0, sck=Pin(config.SPI_SCK_PIN), mosi=Pin(config.SPI_MOSI_PIN), miso=Pin(config.SPI_MISO_PIN))
oled = SSD1306_SPI(config.OLED_MAX_X_RES, config.OLED_MAX_Y_RES, spi, dc=Pin(config.OLED_DC_PIN), res=Pin(config.OLED_RES_PIN), cs=Pin(config.OLED_CS_PIN))


# --- Setup ADC --
pin=Pin(config.ADC_IN_PIN, Pin.IN)
adc = ADC(pin)
adc.atten(config.ADC_INPUT_ATTENUATION)    # set 11dB input attentuation (voltage range roughly 0.0v - 3.6v)
adc.width(config.ADC_BIT_RES)   # set 9 bit return values (returned range 0-511)
#-----------------

#--------------------------------------
# Display Startup Splash Screen Logo --
with open(config.STARTUP_LOGO_FILE, 'rb') as f:
    data = bytearray(f.read())
fbuf = FrameBuffer(data, 80, 32, framebuf.MONO_HLSB) # Need Software Engg here..

oled.fill(0)
oled.invert(0)
oled.blit(fbuf, 20, 5)
oled.show()
sleep(2)
#======================

oled.invert(0)
#oled.fill(0)
oled.text('Connecting wifi', 0, 40)
oled.text('...', 50, 50)
oled.show()

##################################
i2c = I2C(scl=Pin(config.I2C_SCL_PIN), sda=Pin(config.I2C_SDA_PIN), freq = config.I2C_FREQ)


# ------- New Wifi connect Code ----------

ap_if = WLAN(AP_IF)
ap_if.active(False)


wifi = WLAN(STA_IF)
wifi.active(True)
wifi.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

# wait until the device is connected to the WiFi network
attempt_count = 0
while not wifi.isconnected() and attempt_count < config.WIFI_MAX_ATTEMPTS:
    attempt_count += 1
    time.sleep(1)
    
IS_WIFI_CONNECTED = True # Need Software-Engg here ... Should be software managed ... should be IS_WIFI_CONNECTED = False

if attempt_count == config.WIFI_MAX_ATTEMPTS:

    IS_WIFI_CONNECTED =  False
    IS_MQTT_SERVER_CONNECTED = False
    print('could not connect to the WiFi network')
    oled.fill(0)
    oled.invert(0)
    oled.blit(fbuf, 20, 5)  # ?????
    oled.show()
    #======================
    oled.invert(0)
    #oled.fill(0)
    oled.text('Connection', 20, 40)
    oled.text('Failed !', 35, 50)
    oled.show()
    #sys.exit()
    sleep(5)
#------------------------------------------

if IS_WIFI_CONNECTED == True:
    
    #----From send message
    
    telegram = telegram_api_lite.TelegramBot(config.TELEGRAM_API_KEY) # Setup the TeleGram Object here
    
    last_telegram_send_time = 0
    
    #-----------------------------------------
    
    #Connecting MQTT Server
    
    oled.fill(0)
    oled.invert(0)
	# --- 
    oled.blit(fbuf, 20, 5)     
    oled.show()
              
    #======================
    oled.invert(0)       
    #oled.fill(0)       
    oled.text('Connecting IoT', 0, 40)       
    oled.text('Server...', 38, 50)      
    oled.show()     
    sleep(2)

    
    # create a random MQTT clientID
    #random_num = int.from_bytes(os.urandom(3), 'little')
    #random_num = int.from_bytes(urandom(3), 'little')
    
    #mqtt_client_id = bytes('client_' + str(random_num), 'ascii')  # ' converted from utf-8 2nd parameter
    client = MQTTClient(client_id=config.MQTT_CLIENT_ID,server=config.MQTT_IO_URL,user=config.MQTT_USERNAME,password=config.MQTT_IO_KEY,ssl=False)
    
    try:
    	if client.connect() == True:
            IS_MQTT_SERVER_CONNECTED = True
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        IS_MQTT_SERVER_CONNECTED = False
        #sys.exit()
    	
    
    if IS_MQTT_SERVER_CONNECTED == True :
        # format of feed name:
        #   "ADAFRUIT_USERNAME/feeds/ADAFRUIT_IO_FEEDNAME"
        mqtt_feedname = bytes('v1/'+config.MQTT_USERNAME+'/things/'+config.MQTT_CLIENT_ID+'/cmd/'+config.MQTT_IO_FEEDNAME,'ascii')  # converted from 'ustf-8' 2nd parameter
        mqtt_feedname1 = bytes('v1/'+config.MQTT_USERNAME+'/things/'+config.MQTT_CLIENT_ID+'/data/'+config.MQTT_IO_FEEDNAME1,'ascii')  # converted from' ustf-8' 2nd parameter
        mqtt_feedname2 = bytes('v1/'+config.MQTT_USERNAME+'/things/'+config.MQTT_CLIENT_ID+'/data/'+config.MQTT_IO_FEEDNAME2,'ascii')  # converted from 'ustf-8' 2nd parameter
        mqtt_feedname3 = bytes('v1/'+config.MQTT_USERNAME+'/things/'+config.MQTT_CLIENT_ID+'/data/'+config.MQTT_IO_FEEDNAME3,'ascii')  # converted from 'ustf-8' 2nd parameter
        mqtt_feedname4 = bytes('v1/'+config.MQTT_USERNAME+'/things/'+config.MQTT_CLIENT_ID+'/data/'+config.MQTT_IO_FEEDNAME4,'ascii')  # converted from 'ustf-8' 2nd parameter
        client.set_callback(cb)
        client.subscribe(mqtt_feedname)
        
        accum_time = 0
        last_publish_time = 0
        last_subscribe_read_time = 0
        queue_element_counter = 0 # Initializer 0 ..

        #------------------------------------------

oled.invert(0)


#Buzzer
Buzzer = Pin(config.BUZZER_GPIO_PIN,Pin.OUT)

#Flame

Flame = Pin(config.FLAME_SENSOR_GPIO_PIN, Pin.IN)  

#logo section ------------------------------------------------

oled.fill(0)
with open(config.TEMPERATURE_ICON, 'rb') as f:
    data = bytearray(f.read())
tem16_buff = FrameBuffer(data, 16, 16, framebuf.MONO_HLSB) # Need Software Engg..

#---------------------------
with open(config.PRESSURE_ICON, 'rb') as f:
    data = bytearray(f.read())
pres16_buff = FrameBuffer(data, 16, 16, framebuf.MONO_HLSB) # Soft engg here todo

#----------------------------
with open(config.HUMIDITY_ICON, 'rb') as f:
    data = bytearray(f.read())
humi16_buff = FrameBuffer(data, 16, 16, framebuf.MONO_HLSB) # # Soft engg here todo

#----------------------------
with open(config.GAS_ICON, 'rb') as f:
    data = bytearray(f.read())
flame_buff = FrameBuffer(data, 16, 16, framebuf.MONO_HLSB)  # Soft engg here todo

#------------------------------
if IS_WIFI_CONNECTED == True :
    wifi_logo = config.WIIFI_CONNECTED_ICON
else :
    wifi_logo = config.WIIFI_NOT_CONNECTED_ICON
    
with open(wifi_logo, 'rb') as f:
    f.readline() # Magic number
    f.readline() # Creator comment
    f.readline() # Dimensions
    data = bytearray(f.read())
wifi_icon = FrameBuffer(data, 16, 16, framebuf.MONO_HLSB)  # Soft engg here todo

#end of logo section ------------------------------------------------

while True:

    bme = bme280_float.BME280(i2c=i2c)

    temp = bme.values[0]
    temp = temp[:-1] # Filter C  - last char
    print('T',bme.values[0],temp)
    #temp = round(float(temp))

    pressure = bme.values[1]
    pressure = pressure[:-3]
    print('P',bme.values[1],pressure)
    

    humidity = bme.values[2]
    humidity =  humidity[:-1]
    print('H',bme.values[2],humidity)


    #Gas section
    gas_raw = adc.read()
    gas_volt = gas_raw  * (3.70 / 4096) #12bit 
    #gas_volt = gas_raw  * (1.74 / 256) #8bit
    #gas_volt = gas_raw  * (3.66 / 1024) #10bit
   
    if gas_volt > config.BUZZER_TRIGGER_VOLT:
        Buzzer.on()
        WARNING_MESSAGE = 'Warning ! Gas leak detected'
        print(WARNING_MESSAGE)
        
        if (IS_WIFI_CONNECTED == True) and (config.ENABLE_SEND_TELEGRAM_MSG == True):
            
            if time.ticks_diff(time.ticks_ms(), last_telegram_send_time) >= config.TELEGRAM_MSG_SEND_INTERVAL:
               WARNING_MESSAGE= WARNING_MESSAGE+' V: '+str(gas_volt) #  Need format here .. Soft engg
               print ("Telegram msg send:")
               last_telegram_send_time=time.ticks_ms()   
               telegram.send(config.TELEGAM_CHAT_ID, WARNING_MESSAGE)
              
                        
    else :
        Buzzer.off()
        
    #End of Gas section
    
    
    
    #Flame detection section
    Falme_sensor_value = Flame.value()
    print('Flame sensor value is : ',Falme_sensor_value)
   
    if Falme_sensor_value == 0:
        Buzzer.on()
        WARNING_MESSAGE = 'Danger ! Fire detected'
        print(WARNING_MESSAGE)
        
        if (IS_WIFI_CONNECTED == True) and (config.ENABLE_SEND_TELEGRAM_MSG == True):
            telegram.send(config.TELEGAM_CHAT_ID, WARNING_MESSAGE)
              
                        
    else :
        Buzzer.off()
        
    #Flame detection section
        
    
    time.sleep_us(100)
    print('G',gas_volt,'v')
   
    print("------------------\n")   
	
    #oled.invert(0)
    oled.fill(0)
    oled.blit(tem16_buff, 0, 0)
    oled.text("T:" + str(temp) + "'C", 20, 5)
    oled.blit(wifi_icon, 112, 0)
    
    oled.blit(pres16_buff, 0, 18)
    oled.text('P:' + str(pressure), 20, 22)
    
    oled.blit(humi16_buff, 0, 34)
    oled.text('H:' + str(humidity), 20, 40)
    
    oled.blit(flame_buff, 0, 52)
    oled.text('G:' + str(gas_volt), 20 ,55)
    oled.show()
    
    if IS_MQTT_SERVER_CONNECTED == True:
        
        try:
            
            # Publish
            publish_delta = time.ticks_diff(time.ticks_ms(), last_publish_time)
            if  publish_delta >= config.PUBLISH_PERIOD_IN_SEC:
    		# ---- make a queue to compensate the Adafruit IO 2 second 1 data limitation
                queue_element_counter = queue_element_counter + 1
                if queue_element_counter > 4: queue_element_counter=0
    			
    			# This could be improved being more pythonic - 1st level readibilty optimization
                if (queue_element_counter == 1): item_to_be_published = temp; selected_mqtt_feedname = mqtt_feedname1
                elif (queue_element_counter == 2): item_to_be_published = pressure; selected_mqtt_feedname = mqtt_feedname2
                elif (queue_element_counter == 3): item_to_be_published = humidity; selected_mqtt_feedname = mqtt_feedname3
                elif (queue_element_counter == 4): item_to_be_published = gas_volt; selected_mqtt_feedname = mqtt_feedname4
                #------------------
    			
                print('Publish: = {} , {}'.format(item_to_be_published , publish_delta))
                client.publish(selected_mqtt_feedname,bytes(str(item_to_be_published), 'ascii'),qos=0) 
                last_publish_time=time.ticks_ms()
    
           
            if time.ticks_diff(time.ticks_ms(), last_subscribe_read_time) >= config.SUBSCRIBE_CHECK_PERIOD_IN_SEC:
               client.check_msg()
               last_subscribe_read_time = time.ticks_ms()
    
        except KeyboardInterrupt:
            print('Ctrl-C pressed...exiting')
            client.disconnect()
            sys.exit()
