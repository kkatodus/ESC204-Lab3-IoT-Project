
import board
import pwmio
import time
import digitalio
import bitbangio
import adafruit_am2320
from microcontroller import cpu
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
from wifi_stuff import connect, setup_wifi

def on_surveil_mode_change(client, topic, message):
    #function being called upon change in surveillance feed
    global surveil_mode
    if message == "ON":
        surveil_mode = True
    elif message == "OFF":
        surveil_mode = False
    else:
        print("Unexpected message on surveillance feed.")

def sound_buzzer(buzzer):
    #function to sound the buzzer
    buzzer.duty_cycle = 30000# Up
    time.sleep(0.001)

def kill_buzzer(buzzer):
    #function to stop the buzzer
    buzzer.duty_cycle = 0
    time.sleep(0.001)


# Setup digital input for PIR sensor:
pir = digitalio.DigitalInOut(board.A1)
i2c = bitbangio.I2C(board.D3, board.D4)
dhtDevice = adafruit_am2320.AM2320(i2c)
pir.direction = digitalio.Direction.INPUT
#setup buzzer as output
buzzer = pwmio.PWMOut(board.D2, duty_cycle = 0, frequency = 1000, variable_frequency = True)
surveil_mode = True
#setup some wifi stuff in order to connect to adafruit
io, wifi = setup_wifi()
# Set up a callback for the surveillance feed
io.add_feed_callback("surveillance", on_surveil_mode_change)
# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()
#listen to change in surveillance mode
io.subscribe("surveillance")

while True:
    #keep connecting to the adafruit site
    connect(io,wifi)
    #get value from pir sensor
    pir_value = pir.value
    #when there is intruder the intruder value is set to 0 and
    #if there is not it is set to 1
    intruder_value = 1 if not pir_value else 0
    #activating the buzzer based on pir input
    if pir_value and surveil_mode:
        sound_buzzer(buzzer)
    else:
        kill_buzzer(buzzer)
    try:
        #as error frequently occurs with the temp and humidity it is separated from publishing the intruder
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.relative_humidity
        print("AM2320      Temp: {:.1f} C      Humidity: {}% ".format(temperature_c,humidity))
        io.publish("temperature", temperature_c)
        io.publish("humidity", humidity)
        print("published temperature and humidity")
    except:
        print("could not publish temperature or humidity")
    try:
        #publishing to dashboard about presence of intruder
        io.publish("intruder", intruder_value)
        print("published intruder situation")
    except:
        print("could not publish intruder situation")
    #need to make it sleep so that it does not overload
    time.sleep(3)




