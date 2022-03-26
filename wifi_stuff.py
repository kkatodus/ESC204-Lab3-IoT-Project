# Write your code here :-)

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
# Define callback functions which will be called when certain events happen.
# pylint: disable=unused-argument
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    print("Connected to Adafruit IO! ")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")


def setup_wifi():

    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    # Set up SPI pins
    esp32_cs = DigitalInOut(board.CS1)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)


     # Connect RP2040 to the WiFi module's ESP32 chip via SPI, then connect to WiFi
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready,
    esp32_reset)
    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

    # Configure the RP2040 Pico LED Pin as an output
    led_pin = DigitalInOut(board.LED)
    led_pin.switch_to_output()

    # Connect to WiFi
    print("Connecting to WiFi...")
    wifi.connect()
    print("Connected!")

    # Initialize MQTT interface with the esp interface
    MQTT.set_socket(socket, esp)

    # Initialize a new MQTT Client object
    mqtt_client = MQTT.MQTT(
        broker="io.adafruit.com",
        port=secrets["port"],
        username=secrets["aio_username"],
        password=secrets["aio_key"],
    )

    # Initialize an Adafruit IO MQTT Client
    io = IO_MQTT(mqtt_client)

    # Connect the callback methods defined above to Adafruit IO
    io.on_connect = connected
    io.on_disconnect = disconnected
    io.on_subscribe = subscribe

    return io, wifi

def connect(io, wifi):
    # Poll for incoming messages
    try:
        io.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        io.reconnect()



