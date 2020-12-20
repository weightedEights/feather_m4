import board
import busio
import digitalio
import time
import analogio
import neopixel
import adafruit_sdcard
import storage
import adafruit_pcf8523
import os


# red board led
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


# create two tmp36 objects on A0 and A1 inputs
TMP36_A_PIN = board.A0
tmp36_a = analogio.AnalogIn(TMP36_A_PIN)
TMP36_B_PIN = board.A1
tmp36_b = analogio.AnalogIn(TMP36_B_PIN)


# neopixel is D8 for Feather M4 Express
pixel_pin = board.NEOPIXEL
num_pixels = 1
ORDER = neopixel.RGB
pixel = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.02, pixel_order=ORDER)


# blink on-board LED as a running indicator, in place of neopixel
def strobe_led(delay):
    led.value = 1
    time.sleep(delay)
    led.value = 0
    time.sleep(delay)


# fetch and convert TMP36 analog val to degC val
def tmp36_temperature_C(analogin):
    analog_mV = (analogin.value / 65535) * (analogin.reference_voltage * 1000)
    return (analog_mV - 500) / 10


# setup RTC for time stamps
# note that time has to be set on the REPL using:
# rtc.datetime = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
myI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(myI2C)
# TIME_FORMAT = ""{:04d}{:02d}{:02d} {:02d}{:02d}{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)"

# set up SD card for data logging
SD_CS = board.D10
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


print("Feather M4 Express: running")
# wait 30sec before logging for REPL entry
# print("Sensor Log commence: 30sec")
# time.sleep(10)
# print("Sensor Log commence: 20sec")
# time.sleep(10)
print("Sensor Log commence: 10sec")
time.sleep(10)
print("Sensor Log commence: logging")

while True:

    # log temp to sd card
    with open("/sd/temps.txt", 'a') as fout:
        # turn on pixel to indicate log write
        pixel[0] = (100, 50, 150)

        # get, format, print time stamp
        t = rtc.datetime
        # format excel-friendly datetime
        print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
        fout.write("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))

        # write comma for csv
        # fout.write(',')

        # get, format, write temp_a data
        temp_C_a = tmp36_temperature_C(tmp36_a)
        # print("Logging temp: {:.3f}".format(temp_C))
        # fout.write("{:.3f}".format(temp_C_a))

        # write comma for csv
        # fout.write(',')

        # get, format, write temp_b data
        temp_C_b = tmp36_temperature_C(tmp36_b)
        # fout.write("{:.3f}".format(temp_C_b))

        # write a newline
        # fout.write('\n')

        print("{}{:.3f}{}{:.3f}{}".format(',', temp_C_a, ',', temp_C_b, '\n'))
        fout.write("{}{:.3f}{}{:.3f}{}".format(',', temp_C_a, ',', temp_C_b, '\n'))

        # turn off pixel when finished
        pixel[0] = 0

        # delay 1sec
        time.sleep(6)

    # turn off neopixel
    # pixel[0] = 0
    # time.sleep(0.25)
    # pixel[0] = (100, 50, 150)
    # time.sleep(0.25)