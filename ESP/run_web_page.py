import network
import webrepl
import time
import machine
import socket
import uasyncio as asyncio

# Wi-Fi credentials
SSID = "Kalifrotz_2.4G"
PASSWORD = "doremifasol"

# Pin setup
LED_PIN = 2
MQ9_PIN = 34
MQ135_PIN = 35

led = machine.Pin(LED_PIN, machine.Pin.OUT)
mq9_adc = machine.ADC(machine.Pin(MQ9_PIN))
mq135_adc = machine.ADC(machine.Pin(MQ135_PIN))

# Set ADC attenuation
mq9_adc.atten(machine.ADC.ATTN_11DB)
mq135_adc.atten(machine.ADC.ATTN_11DB)

# Global flag to control the web server
server_running = True


# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)

        # Wait for connection
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


# Web server to serve sensor data
def web_page():
    mq9_value = mq9_adc.read()
    mq135_value = mq135_adc.read()

    led.value(1)  # Blink LED to indicate measurement
    time.sleep(0.1)
    led.value(0)

    # HTML content with a button to stop the server
    html = f"""<!DOCTYPE html>
    <html>
    <head><title>ESP32 Sensor Data</title></head>
    <body>
    <h1>MQ9: {mq9_value}</h1>
    <h1>MQ135: {mq135_value}</h1>
    <button onclick="fetch('/stop_server');">Stop Server</button>
    </body>
    </html>"""
    return html


# Web server function to handle requests
async def start_web_server():
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 80))
    server_socket.listen(5)

    print("Server started... Access via browser: http://" + network.WLAN(network.STA_IF).ifconfig()[0])

    while True:
        conn, addr = server_socket.accept()
        print("Got connection from", addr)

        request = conn.recv(1024)
        request = str(request)

        if '/stop_server' in request:
            # Stop the server when the button is pressed
            print("Stopping server...")
            server_running = False
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
            conn.sendall("<html><body><h1>Server Stopped. You can now access WebREPL.</h1></body></html>")
            break

        conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
        conn.sendall(web_page())
        conn.close()


# The main function to initialize everything
async def main():
    # Start Wi-Fi and services
    if connect_wifi():
        # Start WebREPL
        webrepl.start(password='kalesp')
        print('WebREPL started')

        # Start the web server using asyncio
        asyncio.create_task(start_web_server())

        # Let the system run indefinitely while the web server and WebREPL continue to work
        while server_running:
            await asyncio.sleep(1)

        print("Web server has been stopped. WebREPL can now be accessed.")


# Run the main function
asyncio.run(main())
