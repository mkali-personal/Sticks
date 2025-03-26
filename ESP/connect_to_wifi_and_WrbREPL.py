import network
import webrepl
import time
import machine

LED_PIN = 2  # Built-in LED (GPIO 2)
led = machine.Pin(LED_PIN, machine.Pin.OUT)


# Connect to your WiFi network
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect('Kalifrotz_2.4G', 'doremifasol')

        # Wait for connection with timeout
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)

    if wlan.isconnected():
        print('Connected to WiFi')
        print('Network config:', wlan.ifconfig())
        return True
    else:
        print('Could not connect to WiFi')
        return False


# Start connection
if connect_wifi():
    # Enable WebREPL
    webrepl.start(password='kalesp')
    print('WebREPL started')


