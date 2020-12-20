import time
import board
import busio
from digitalio import DigitalInOut

# ESP32 AT
from adafruit_espatcontrol import adafruit_espatcontrol, adafruit_espatcontrol_wifimanager

#Use below for Most Boards
import neopixel
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2) # Uncomment for Most Boards
#Uncomment below for ItsyBitsy M4#
#import adafruit_dotstar as dotstar
#status_light = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


# With a Metro or Feather M4
uart = busio.UART(board.TX, board.RX, timeout=0.1)
resetpin = DigitalInOut(board.D5)
rtspin = DigitalInOut(board.D6)

# With a Particle Argon
"""
RX = board.ESP_TX
TX = board.ESP_RX
resetpin = DigitalInOut(board.ESP_WIFI_EN)
rtspin = DigitalInOut(board.ESP_CTS)
uart = busio.UART(TX, RX, timeout=0.1)
esp_boot = DigitalInOut(board.ESP_BOOT_MODE)
from digitalio import Direction
esp_boot.direction = Direction.OUTPUT
esp_boot.value = True
"""


print("ESP AT commands")
esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200,
                                          reset_pin=resetpin, rts_pin=rtspin, debug=False)
wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(esp, secrets, status_light)


counter = 0

while True:
    try:
        print("Posting data...", end='')
        data = counter
        feed = 'test'
        payload = {'value':data}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
            json=payload,
            headers={bytes("X-AIO-KEY", "utf-8"):bytes(secrets['aio_key'], "utf-8")})
        print(response.json())
        response.close()
        counter = counter + 1
        print("OK")
    except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    response = None
    time.sleep(15)
