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
import gc

# gc.collect()  # Try freeing unused memory

def sync_time():
    try:
        print("Syncing time with NTP...")
        ntptime.settime()  # Synchronizes the ESP32's time with an NTP server
        udp_log(f"Time synchronized: {time.localtime()}")
        print("Time synchronized!")
    except Exception as e:
        print("Failed to sync time:", e)


def get_storage_info():
    fs_stat = uos.statvfs('/')
    storage =  {
        'block_size': fs_stat[0],          # Filesystem block size
        'total_blocks': fs_stat[2],        # Total blocks
        'free_blocks': fs_stat[3],         # Free blocks
        'total_bytes': fs_stat[2] * fs_stat[0],
        'free_bytes': fs_stat[3] * fs_stat[0],
        'used_percent': 100 - (fs_stat[3] / fs_stat[2] * 100)
    }

    return f"Free: {storage['free_bytes'] / 1024:.1f}KB / {storage['total_bytes'] / 1024:.1f}KB"

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
MAX_FILE_SIZE = 32 * 1024  # 32KB

ENTRY_FORMAT = "<III"  # timestamp_ms, mq9_value, mq135_value (no index)
ENTRY_SIZE = struct.calcsize(ENTRY_FORMAT)
server_running = True

UDP_IP = "255.255.255.255"  # Broadcast address
UDP_PORT = 4210
DEBUG_LEVEL = 1  # 0 = Off, 1 = Normal, 2 = Verbose

N_FILES = 20  # Number of files to keep
LIST_OF_FILES_NAMES = [f"data/file_{i}.bin" for i in range(20)]  # Extend for n files

# 🔹 Create the UDP socket once
log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
log_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast


def udp_log(message, level=1):
    """Send logs over UDP using a pre-initialized socket."""
    if level > DEBUG_LEVEL:
        return  # Ignore messages above the debug level

    try:
        print(f"Message: {message}, Time: {format_timestamp(time.time())}")#, Free memory: {gc.mem_free()}, storage_status={get_storage_info()}")  # Check available RAM
        log_socket.sendto(f"ESP32: {message}\n".encode(), (UDP_IP, UDP_PORT))
    except Exception as e:
        print("Logging error:", e)


# Constants


# ====== 1. Binary Save Function ======
def save_measurement(timestamp, mq9, mq135):
    try:
        udp_log("starting save_measurement function")

        # Get current file size for the last file
        try:
            udp_log("Getting file size")
            file_size = uos.stat(LIST_OF_FILES_NAMES[0])[6]  # Get current file size
            time.sleep(0.1)
            udp_log(f"File size: {file_size} / {MAX_FILE_SIZE}")

        except OSError:
            udp_log(f"File {LIST_OF_FILES_NAMES[0]} doesn't exist")
            file_size = 0  # File doesn't exist yet

        if file_size >= MAX_FILE_SIZE:
            # Rotate files
            try:
                udp_log("Rotating data files...")
                uos.remove(LIST_OF_FILES_NAMES[-1])  # Remove the oldest file
            except OSError:
                pass  # No file to remove

            # Shift all files in the list to the left
            for i in range(N_FILES - 1, 0, -1):
                try:
                    udp_log(f"Renaming {LIST_OF_FILES_NAMES[i - 1]} to {LIST_OF_FILES_NAMES[i]}...")
                    uos.rename(LIST_OF_FILES_NAMES[i - 1], LIST_OF_FILES_NAMES[i])  # Move last to the next position
                except OSError as e:
                    print("Error rotating files:", e)

        # Append new measurement to the latest file
        with open(LIST_OF_FILES_NAMES[0], "ab") as f:
            udp_log(f"Saving binary data: {timestamp}, {mq9}, {mq135}")
            f.write(struct.pack(ENTRY_FORMAT, timestamp, mq9, mq135))
    except Exception as e:
        print("Error saving binary data:", e)


# ====== 2. Binary Read Function (all rows) ======
def read_measurements(last_n=None):
    measurements = []

    if last_n is None:
        # Read all data from all files
        for file_path in LIST_OF_FILES_NAMES:
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
        # Read only the last `last_n` measurements from the most recent file
        udp_log(f"Reading the last {last_n} measurements from {LIST_OF_FILES_NAMES[0]}")
        try:
            with open(LIST_OF_FILES_NAMES[0], "rb") as f:
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
            print(f"Error reading binary data from {LIST_OF_FILES_NAMES[0]}: {e}")

    return measurements


# ====== 3. Binary Download Handler ======


# ====== 3. Timestamp Formatting ======
def format_timestamp(timestamp):
    TIMEZONE_OFFSET = 3 * 3600  # Offset in seconds (3 hours)
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
        elif '/download' in request:
            # Extract number of files from request
            try:
                num_files = int(request.split('num_files=')[1].split(' ')[0])
            except (IndexError, ValueError):
                num_files = 1  # Default to 1 if not specified
            await handle_download(writer, num_files)
        else:
            await writer.awrite("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
            await writer.awrite(web_page())
        await writer.wait_closed()
    except Exception as e:
        print("Client error:", e)

    finally:
        await writer.wait_closed()  # Ensure socket closure


# Download handler with multiple file merging
async def handle_download(writer, num_files_to_download):
    try:
        # Get list of available files, sorted by newest first
        available_files = sorted(
            [f for f in uos.listdir("data/") if f.startswith("file_")]
        )
        available_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]), reverse=False)
        udp_log(f"Available files: {available_files}")

        # Select the latest N files
        files_to_download = available_files[:num_files_to_download]
        udp_log(f"Files to download: {files_to_download}")
        if not files_to_download:
            await writer.awrite("HTTP/1.1 404 Not Found\r\n\r\n")
            return

        # Start HTTP response for binary file download
        await writer.awrite("HTTP/1.1 200 OK\r\n")
        await writer.awrite("Content-Type: application/octet-stream\r\n")
        await writer.awrite("Content-Disposition: attachment; filename=\"data.bin\"\r\n\r\n")

        # Stream binary data from the selected files
        for file_name in files_to_download:
            try:
                udp_log(f"Downloading file: {file_name}")
                with open("data/" + file_name, "rb") as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        await writer.awrite(data)
                udp_log(f"File {file_name} downloaded")
            except OSError:
                continue  # Skip missing files
    except Exception as e:
        print("Download error:", e)
    finally:
        await writer.wait_closed()


# Updated web page
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
    <form action='/download' method='get'>
        <label for='num_files'>Number of files to download:</label>
        <input type='number' id='num_files' name='num_files' min='1' max='10' value='1'>
        <input type='submit' value='Download' class='button'>
    </form>
    <h2>All Measurements</h2>
    <table>
    <tr>
        <th>Timestamp</th>
        <th>Datetime</th>
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
    <p><a href='/stop_server'>Stop Server</a></p>
    </body>
    </html>"""
    return html


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
            udp_log(f"Measurement: {timestamp} ({format_timestamp(timestamp)}), {mq9}, {mq135}")
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
        webrepl.start(password='kalesp')
        print("WebREPL started")
        udp_log("WebREPL started")

        time.sleep(1)
        sync_time()
        global START_TIME
        START_TIME = time.time()

        udp_log(f"Starting at start_time = {START_TIME}")

        server_task = asyncio.create_task(start_web_server())
        measurement_task = asyncio.create_task(measurement_loop())

        while server_running:
            await asyncio.sleep(1)


asyncio.run(main())
