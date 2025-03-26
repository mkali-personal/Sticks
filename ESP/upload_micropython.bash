# First, connect the ESP32 to the computer
python -m esptool --chip esp32 erase_flash

# Download the latest firmware from https://micropython.org/download/esp32/ and replace the file name with the one you downloaded.
python -m esptool --baud 115200 write_flash 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin

# put operate_esp.py on the ESP32:
python -m ampy.cli --port COM8 --delay 1 put operate_esp.py