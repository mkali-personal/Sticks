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
import asyncio
from array import array

# Pin setup
LED_PIN = 2
MQ9_PIN = 33
MQ135_PIN = 32
MQ2_PIN = 35
MQ7_PIN = 34
MQ3_PIN = 39
START_TIME = 0
MEASUREMENT_TIME_INTERVAL = 1  # seconds

led = machine.Pin(LED_PIN, machine.Pin.OUT)
mq9_adc = machine.ADC(machine.Pin(MQ9_PIN))
mq135_adc = machine.ADC(machine.Pin(MQ135_PIN))
mq2_adc = machine.ADC(machine.Pin(MQ2_PIN))
mq7_adc = machine.ADC(machine.Pin(MQ7_PIN))
mq3_adc = machine.ADC(machine.Pin(MQ3_PIN))

# Set ADC attenuation
mq9_adc.atten(machine.ADC.ATTN_0DB)
mq135_adc.atten(machine.ADC.ATTN_0DB)
mq2_adc.atten(machine.ADC.ATTN_0DB)
mq7_adc.atten(machine.ADC.ATTN_0DB)
mq3_adc.atten(machine.ADC.ATTN_0DB)

# Binary file setup
MAX_FILE_SIZE = 32 * 1024  # 32KB

ENTRY_FORMAT = "<IIIIII"  # timestamp_ms, mq9_value, mq135_value, mq2_value, mq7_value, mq3_value
ENTRY_SIZE = struct.calcsize(ENTRY_FORMAT)
server_running = True

UDP_IP = "255.255.255.255"  # Broadcast address
UDP_PORT = 4210
DEBUG_LEVEL = 0  # 0 = Off, 1 = all udp logs, 2 = all udp logs and print to console

N_FILES = 20  # Number of files to keep
LIST_OF_FILES_NAMES = [f"data/file_{i}.bin" for i in range(20)]  # Extend for n files

# 🔹 Create the UDP socket once
log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
log_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast


def format_timestamp(timestamp):
    TIMEZONE_OFFSET = 3 * 3600  # Offset in seconds (3 hours)
    utc_time = time.localtime(timestamp + TIMEZONE_OFFSET)
    return "{:02}/{:02}/{:02} {:02}:{:02}:{:02}".format(
        utc_time[0], utc_time[1], utc_time[2],
        utc_time[3], utc_time[4], utc_time[5]
    )


def sync_time():
    try:
        print("Syncing time with NTP...")
        ntptime.settime()  # Synchronizes the ESP32's time with an NTP server
        udp_log(f"Time synchronized: {time.localtime()}", DEBUG_LEVEL)
        print("Time synchronized!")
    except Exception as e:
        print("Failed to sync time:", e)


def udp_log(message, level):
    """Send logs over UDP using a pre-initialized socket."""
    if level > 0:
        try:
            log_socket.sendto(f"ESP32: {message}\n".encode(), (UDP_IP, UDP_PORT))
        except Exception as e:
            print("Logging error:", e)
    if level > 1:
        print(f"Time: {format_timestamp(time.time())}  Message: {message}")


# ====== 1. Binary Save Function ======
def save_measurement(timestamp, measurements_array):
    try:
        udp_log("starting save_measurement function", DEBUG_LEVEL)

        # Get current file size for the last file
        try:
            udp_log("Getting file size", DEBUG_LEVEL)
            file_size = uos.stat(LIST_OF_FILES_NAMES[0])[6]  # Get current file size
            time.sleep(0.1)
            udp_log(f"File size: {file_size} / {MAX_FILE_SIZE}", DEBUG_LEVEL)

        except OSError:
            udp_log(f"File {LIST_OF_FILES_NAMES[0]} doesn't exist", DEBUG_LEVEL)
            file_size = 0  # File doesn't exist yet

        if file_size >= MAX_FILE_SIZE:
            # Rotate files
            try:
                udp_log("Rotating data files...", DEBUG_LEVEL)
                uos.remove(LIST_OF_FILES_NAMES[-1])  # Remove the oldest file
            except OSError:
                pass  # No file to remove

            # Shift all files in the list to the left
            for i in range(N_FILES - 1, 0, -1):
                try:
                    udp_log(f"Renaming {LIST_OF_FILES_NAMES[i - 1]} to {LIST_OF_FILES_NAMES[i]}...", DEBUG_LEVEL)
                    uos.rename(LIST_OF_FILES_NAMES[i - 1], LIST_OF_FILES_NAMES[i])  # Move last to the next position
                except OSError as e:
                    print("Error rotating files:", e)

        # Append new measurement to the latest file
        with open(LIST_OF_FILES_NAMES[0], "ab") as f:
            udp_log(f"Saving binary data: {timestamp}, {measurements_array}", DEBUG_LEVEL)
            f.write(struct.pack(ENTRY_FORMAT, timestamp, *measurements_array))
    except Exception as e:
        print("Error saving binary data:", e)


def read_measurements(last_n=None):
    measurements = []

    if last_n is None:
        # Read all data from all files
        for file_path in LIST_OF_FILES_NAMES:
            udp_log(f"Reading binary data from {file_path}", DEBUG_LEVEL)
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
        udp_log(f"Reading the last {last_n} measurements from {LIST_OF_FILES_NAMES[0]}", DEBUG_LEVEL)
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


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connection from {addr}")

    try:
        # Receive file request
        requested_file = (await reader.read(128)).decode().strip()
        print(f"Requested file: {requested_file}")

        if requested_file in uos.listdir("data/"):  # Validate file existence
            writer.write(b"OK")  # Confirm file is found
            await writer.drain()
            await asyncio.sleep(0.1)  # Short delay for synchronization

            # Send file content
            with open("data/" + requested_file, "rb") as f:
                while chunk := f.read(1024):
                    writer.write(chunk)
                    await writer.drain()

            print(f"File {requested_file} sent successfully.")
        else:
            writer.write(b"ERROR: File not found")
            await writer.drain()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        writer.close()
        await writer.wait_closed()
        print("Connection closed")


async def file_server():
    HOST = "0.0.0.0"
    PORT = 12345

    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"File server running on {HOST}:{PORT}")

    while True:
        await asyncio.sleep(1)  # Keep the server running


# Measurement loop
async def measurement_loop():
    print("Starting measurement loop...")
    udp_log("Starting measurement loop...", DEBUG_LEVEL)

    while server_running:
        try:
            # Take measurements
            timestamp = time.time()
            udp_log(f"Taking measurement at: {timestamp}", DEBUG_LEVEL)
            n_measruements_to_average = 50
            mq9_values = array('H', [0] * n_measruements_to_average)
            mq135_values = array('H', [0] * n_measruements_to_average)
            mq2_values = array('H', [0] * n_measruements_to_average)
            mq7_values = array('H', [0] * n_measruements_to_average)
            mq3_values = array('H', [0] * n_measruements_to_average)

            led.value(1)
            for i in range(n_measruements_to_average):
                # print(f"{str(time.ticks_ms()).ljust(30)}, {i}")
                mq9_values[i] = mq9_adc.read()
                mq135_values[i] = mq135_adc.read()
                mq2_values[i] = mq2_adc.read()
                mq7_values[i] = mq7_adc.read()
                mq3_values[i] = mq3_adc.read()
                await asyncio.sleep(MEASUREMENT_TIME_INTERVAL / n_measruements_to_average)
            led.value(0)

            # Average the measurements
            mq9 = sum(mq9_values) // n_measruements_to_average
            mq135 = sum(mq135_values) // n_measruements_to_average
            mq2 = sum(mq2_values) // n_measruements_to_average
            mq7 = sum(mq7_values) // n_measruements_to_average
            mq3 = sum(mq3_values) // n_measruements_to_average

            if mq9 > 4000:
                mq9_adc.atten(machine.ADC.ATTN_11DB)
                udp_log("MQ9 ADC set to 11dB", level=max(1, DEBUG_LEVEL))  # always log this one
            if mq135 > 4000:
                mq135_adc.atten(machine.ADC.ATTN_11DB)
                udp_log("MQ9 ADC set to 11dB", level=max(1, DEBUG_LEVEL))  # always log this one
            if mq2 > 4000:
                mq2_adc.atten(machine.ADC.ATTN_11DB)
                udp_log("MQ2 ADC set to 11dB", level=max(1, DEBUG_LEVEL))
            if mq7 > 4000:
                mq7_adc.atten(machine.ADC.ATTN_11DB)
                udp_log("MQ7 ADC set to 11dB", level=max(1, DEBUG_LEVEL))
            if mq3 > 4000:
                mq3_adc.atten(machine.ADC.ATTN_11DB)
                udp_log("MQ3 ADC set to 11dB", level=max(1, DEBUG_LEVEL))

            # Save in binary format
            save_measurement(timestamp, [mq9, mq135, mq2, mq7, mq3])
            udp_log(f"Measurement: {timestamp} ({format_timestamp(timestamp)}), {[mq9, mq135, mq2, mq7, mq3]}",
                    level=max(1, DEBUG_LEVEL))  # always log this one
            # Blink LED
            # udp_log("LED blinked", DEBUG_LEVEL)
        except Exception as e:
            udp_log(f"Measurement error: {e}", DEBUG_LEVEL)
            await asyncio.sleep(1)


# Main function
async def main():
    if connect_wifi():
        webrepl.start(password='kalesp')
        print("WebREPL started")
        udp_log("WebREPL started", DEBUG_LEVEL)

        time.sleep(1)
        sync_time()
        global START_TIME
        START_TIME = time.time()

        udp_log(f"Starting at start_time = {START_TIME}", DEBUG_LEVEL)

        server_task = asyncio.create_task(file_server())  # File server replaces web server
        measurement_task = asyncio.create_task(measurement_loop())

        while server_running:
            await asyncio.sleep(1)


asyncio.run(main())

