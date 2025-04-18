# MicroPython on ESP32
to put the micropython on the ESP32, you need to download the firmware from the official website:
https://micropython.org/download/ESP32_GENERIC/

and run the following commands in the terminal:

```bat
pip install esptool
python -m esptool erase_flash
python -m esptool --baud 115200 write_flash 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin
```
where `ESP32_GENERIC-20241129-v1.24.1.bin` is the name of the firmware file you downloaded. in the first stage

# Communicating with the device

## Through usb wire:
pip install the packages adafruit-ampy, mpremote, and pyserial:

to connect to the device (to use the pycharm's terminal/windows cmd as a python console of the ESP),
you can use the following command:

```bat
python -m mpremote connect COM8
```
where `COM8` is the port where the device is connected. You can find the port in the device manager.
Note that if you are already connected to the ESP through Thonny, or Pycharm's MicroPython
plugin, you will not be able to connect to the device using the above command,
and will first have to quite the other connection.

to upload a file to the ESP, run the following command:

```bat
python -m ampy.cli --port COM8 --delay 1 put boot.py
```