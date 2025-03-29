import network
import webrepl
import time
import machine
import uasyncio as asyncio
from uasyncio import StreamReader, StreamWriter
import uos
import struct
import socket
import ntptime  # Built-in NTP client for MicroPython
import time
from wifi_credentials import HOUSE_WIFI_SSID, HOUSE_WIFI_PASSWORD


def sync_time():
    try:
        print("Syncing time with NTP...")
        ntptime.settime()  # Synchronizes the ESP32's time with an NTP server
        print("Time synchronized!")
    except Exception as e:
        print("Failed to sync time:", e)

# Pin setup
LED_PIN = 2
MQ9_PIN = 34
MQ135_PIN = 35
START_TIME = 0
MEASUREMENT_TIME_INTERVAL = 3  # seconds

led = machine.Pin(LED_PIN, machine.Pin.OUT)
mq9_adc = machine.ADC(machine.Pin(MQ9_PIN))
mq135_adc = machine.ADC(machine.Pin(MQ135_PIN))

# Set ADC attenuation
mq9_adc.atten(machine.ADC.ATTN_11DB)
mq135_adc.atten(machine.ADC.ATTN_11DB)

# Binary file setup
DATA_LAST_FILE = "/data_last.bin"
DATA_SECOND_LAST_FILE = "/data_second_to_last.bin"
MAX_FILE_SIZE = 512 * 1024  # 512KB

ENTRY_FORMAT = "<III"  # timestamp_ms, mq9_value, mq135_value (no index)
ENTRY_SIZE = struct.calcsize(ENTRY_FORMAT)
server_running = True

UDP_IP = "255.255.255.255"  # Broadcast address
UDP_PORT = 4210
DEBUG_LEVEL = 1  # 0 = Off, 1 = Normal, 2 = Verbose

# 🔹 Create the UDP socket once
log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
log_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast


def udp_log(message, level=1):
    """Send logs over UDP using a pre-initialized socket."""
    if level > DEBUG_LEVEL:
        return  # Ignore messages above the debug level

    try:
        log_socket.sendto(f"ESP32: {message}\n".encode(), (UDP_IP, UDP_PORT))
    except Exception as e:
        print("Logging error:", e)

# ====== 1. Binary Save Function ======
def save_measurement(timestamp, mq9, mq135):
    try:
        udp_log("starting save_measurement function")
        try:
            udp_log("Getting file size")
            file_size = uos.stat(DATA_LAST_FILE)[6]  # Get current file size
            time.sleep(0.1)
            udp_log(f"File size: {file_size} / {MAX_FILE_SIZE}")

        except OSError:
            udp_log(f"File {DATA_LAST_FILE} doesn't exist")
            file_size = 0  # File doesn't exist yet

        if file_size >= MAX_FILE_SIZE:
            # Rotate files
            try:
                udp_log("Rotating data files...")
                uos.remove(DATA_SECOND_LAST_FILE)  # Remove old second-to-last file
            except OSError:
                pass  # No file to remove
            try:
                udp_log("Renaming files...")
                uos.rename(DATA_LAST_FILE, DATA_SECOND_LAST_FILE)  # Move last to second-to-last
            except OSError as e:
                print("Error rotating files:", e)

        # Append new measurement to /data_last.bin
        with open(DATA_LAST_FILE, "ab") as f:
            udp_log(f"Saving binary data: {timestamp}, {mq9}, {mq135}")
            f.write(struct.pack(ENTRY_FORMAT, timestamp, mq9, mq135))
    except Exception as e:
        print("Error saving binary data:", e)


# ====== 2. Binary Read Function (all rows) ======
def read_measurements(last_n=None):
    measurements = []

    if last_n is None:
        # Read all data from both files
        for file_path in [DATA_SECOND_LAST_FILE, DATA_LAST_FILE]:
            udp_log(f"Reading binary data from {file_path}")
            try:
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(ENTRY_SIZE)
                        if not data:
                            break
                        measurements.append(struct.unpack(ENTRY_FORMAT, data))
            except OSError:
                pass  # File doesn't exist
            except Exception as e:
                print(f"Error reading binary data from {file_path}: {e}")

    else:
        # Read only the last `last_n` measurements from DATA_LAST_FILE
        udp_log(f"Reading the last {last_n} measurements from {DATA_LAST_FILE}")
        try:
            with open(DATA_LAST_FILE, "rb") as f:
                f.seek(0, 2)  # Move to the end of the file
                file_size = f.tell()
                total_entries = file_size // ENTRY_SIZE

                entries_to_read = min(last_n, total_entries)
                f.seek(max(0, file_size - (entries_to_read * ENTRY_SIZE)))

                for _ in range(entries_to_read):
                    data = f.read(ENTRY_SIZE)
                    if not data:
                        break
                    measurements.append(struct.unpack(ENTRY_FORMAT, data))
        except OSError:
            pass  # File doesn't exist
        except Exception as e:
            print(f"Error reading binary data from {DATA_LAST_FILE}: {e}")

    return measurements



# ====== 3. Binary-to-CSV Download Handler ======
async def handle_download(writer):
    try:
        # Start HTTP response
        await writer.awrite("HTTP/1.1 200 OK\r\n")
        await writer.awrite("Content-Type: text/csv\r\n")
        await writer.awrite('Content-Disposition: attachment; filename="sensor_data.csv"\r\n\r\n')

        # Write CSV header
        await writer.awrite("timestamp,human_time,mq9_value,mq135_value\r\n")

        # Stream binary data and convert to CSV
        for timestamp, mq9, mq135 in read_measurements():
            csv_line = f"{timestamp},{format_timestamp(timestamp)},{mq9},{mq135}\r\n"
            await writer.awrite(csv_line)
    except Exception as e:
        print("Download error:", e)
    finally:
        await writer.wait_closed()


# ====== 3. Timestamp Formatting ======
def format_timestamp(timestamp):
    TIMEZONE_OFFSET = 3 * 3600  # Offset in seconds (2 hours)
    utc_time = time.localtime(timestamp + TIMEZONE_OFFSET)
    return "{:02}/{:02}/{:02} {:02}:{:02}:{:02}".format(
        utc_time[0], utc_time[1], utc_time[2],
        utc_time[3], utc_time[4], utc_time[5]
    )

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(HOUSE_WIFI_SSID, HOUSE_WIFI_PASSWORD)
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


# ====== 4. Updated Web Page ======
def web_page():
    measurements = read_measurements(last_n=100)
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Sensor Data</title>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .button { 
                display: inline-block;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
    <h1>ESP32 Sensor Data</h1>
    <a href="/download" class="button">Download Full Data (CSV)</a>
    <h2>All Measurements</h2>
    <table>
    <tr>
        <th>Timestamp</th>
        <th>Datatime</th>
        <th>MQ9</th>
        <th>MQ135</th>
    </tr>"""

    for timestamp, mq9, mq135 in measurements:
        html += f"""<tr>
            <td>{timestamp}</td>
            <td>{format_timestamp(timestamp)}</td>
            <td>{mq9}</td>
            <td>{mq135}</td>
        </tr>"""

    html += """</table>
    <p><a href="/stop_server">Stop Server</a></p>
    </body>
    </html>"""
    return html


# Client handler
async def handle_client(reader, writer):
    global server_running
    try:
        request = await reader.read(1024)
        request = str(request)
        udp_log(f"Request: {request}")

        if '/stop_server' in request:
            print("Stopping server...")
            udp_log("Stopping server...")
            server_running = False
            await writer.awrite("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
            await writer.awrite("<html><body><h1>Server Stopped.</h1></body></html>")
            await writer.wait_closed()
            return
        elif '/download' in request:
            await handle_download(writer)
            return
        else:
            await writer.awrite("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
            await writer.awrite(web_page())
            await writer.wait_closed()
    except Exception as e:
        print("Client error:", e)


# Web server
async def start_web_server():
    global server_running
    print("Starting web server...")
    udp_log("Starting web server...")
    try:
        server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
        print(f"Server started: http://{network.WLAN(network.STA_IF).ifconfig()[0]}")
        udp_log(f"Server started: http://{network.WLAN(network.STA_IF).ifconfig()[0]}")
        async with server:
            while server_running:
                udp_log(f"Server running - {format_timestamp(time.time())}")
                await asyncio.sleep(1)
    except Exception as e:
        print("Server error:", e)


# Measurement loop
async def measurement_loop():
    print("Starting measurement loop...")
    udp_log("Starting measurement loop...")

    while server_running:
        try:
            # Take measurements
            timestamp = time.time()
            udp_log(f"Taking measurement at: {timestamp}")
            mq9 = mq9_adc.read()
            mq135 = mq135_adc.read()

            # Save in binary format
            save_measurement(timestamp, mq9, mq135)
            udp_log(f"Measurement: {timestamp}, {mq9}, {mq135}")
            # Blink LED
            led.value(1)
            await asyncio.sleep(0.01)
            led.value(0)
            await asyncio.sleep(MEASUREMENT_TIME_INTERVAL - 0.01)
            udp_log("LED blinked")
        except Exception as e:
            print("Measurement error:", e)
            udp_log(f"Measurement error: {e}")
            await asyncio.sleep(1)


# Main function
async def main():
    if connect_wifi():
        sync_time()
        global START_TIME
        START_TIME = time.time()
        udp_log(f"Starting at start_time = {START_TIME}")
        webrepl.start(password='kalesp')
        print("WebREPL started")
        udp_log("WebREPL started")

        server_task = asyncio.create_task(start_web_server())
        measurement_task = asyncio.create_task(measurement_loop())

        while server_running:
            await asyncio.sleep(1)


asyncio.run(main())