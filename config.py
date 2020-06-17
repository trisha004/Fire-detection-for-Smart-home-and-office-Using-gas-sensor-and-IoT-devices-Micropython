# --------- Const Variables -------- #
MACHINE_FREQ = 240000000 # Possible frequency 80 160 240Mhz ???

# ---- WIFI      ---
WIFI_SSID = b'wighj Guest'#'HomeBase_V2'#b'HomeBase_V2' #'Belancer Guest'
WIFI_PASSWORD =b'Belanceguest'#b'Mdrif5k123456789!' # #b'Mdrif5k123456789!'

WIFI_MAX_ATTEMPTS = const(20)

# ----
STARTUP_LOGO_FILE = b'deshlogo.bin'
WIIFI_CONNECTED_ICON = b'wifi_connected.pbm'
WIIFI_NOT_CONNECTED_ICON = b'wifi_not_connected.pbm'
TEMPERATURE_ICON = b'tem16.bin'
PRESSURE_ICON = b'pres16.bin'
HUMIDITY_ICON = b'humidity16.bin'
GAS_ICON = b'BottleFire.bin'

#---- PIN Defination ---#
# -- --
SPI_BAUD_RATE = const(8000000)
SPI_SCK_PIN = const(14) #oled display SCL pin
SPI_MOSI_PIN = const(13) #oled display SDA pin
SPI_MISO_PIN = const(12)

#--- OLED ---
# SSD1306_SPI(128, 64, spi, dc=Pin(16), res=Pin(17), cs=Pin(18))
OLED_MAX_X_RES = const(128)
OLED_MAX_Y_RES = const(64)
OLED_DC_PIN = const(16)  # Direction / read / write ??
OLED_RES_PIN = const(17) # Reset 
OLED_CS_PIN = const(18)  # Chip Select

# --- I2C---BME --
# i2c = I2C(scl=Pin(22), sda=Pin(21), freq = 100000)
I2C_SCL_PIN = const(22) #BME SCL pin
I2C_SDA_PIN = const(21) #BME SDA pin
I2C_FREQ = const(100000)


# --- ADC
ADC_IN_PIN = const(34) #for Gass sensor
ADC_INPUT_ATTENUATION = const(3) # ??
ADC_BIT_RES = const(3) #12bit
#-----------------------

#-----
RELAY_GPIO_PIN = const(4)

#Buzzer Pin
BUZZER_GPIO_PIN = const(0)
BUZZER_TRIGGER_VOLT = 2.50

#Flame sensor Pin
FLAME_SENSOR_GPIO_PIN = const(2)
FLAME_DETECTION_STATUS = False


# --- Cayenne IoT Server Parameters 
#User: farjana186@gmail.com
#password : 345677

MQTT_IO_URL = b'mqtt.mydevices.com'
MQTT_USERNAME ='335e9720-76eb-11e9-be3b-372b0d2759ae' 
MQTT_IO_KEY =b'9d1dedcef7b48c6ea30922ff8fc0882c5599b56d'
MQTT_CLIENT_ID = '663b1be0-76ec-11e9-94e9-493d67fd755e'



MQTT_IO_FEEDNAME = '0'
MQTT_IO_FEEDNAME1 = '1'#const(1)
MQTT_IO_FEEDNAME2 = '2'#const(2)
MQTT_IO_FEEDNAME3 = '3'#const(3)
MQTT_IO_FEEDNAME4 = '4'


#PUBLISH_PERIOD_IN_SEC = const(2)
PUBLISH_PERIOD_IN_SEC = const(1900)#const(2000)
SUBSCRIBE_CHECK_PERIOD_IN_SEC = const(500) #0.5

# --- 
BOOT_UP_LOGO_SPLASH_DELAY = const(4)

# ----------------------------------------
ENABLE_SEND_TELEGRAM_MSG = True
TELEGAM_CHAT_ID = '893154612'
TELEGRAM_API_KEY = '805789718:AAHNNcMMqyxENYfHtIxwhG0LVOVrvjvYLwk'
TELEGRAM_MSG_SEND_INTERVAL = 100000 #// in MiliSecond