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