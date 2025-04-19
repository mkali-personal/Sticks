import network
import webrepl
import machine
import uasyncio as asyncio
import uos
import struct
import socket
import ntptime  # Built-in NTP client for MicroPython
import time
from wifi_credentials import HOUSE_WIFI_SSID, HOUSE_WIFI_PASSWORD
import asyncio
from array import array
from local_config import PINS, SERVER_PORT, DEVICE_ID

# Pin setup
LED_PIN = 2
START_TIME = 0
MEASUREMENT_TIME_INTERVAL = 1  # seconds
N_MEASUREMENTS_MEMORY = 50
N_MEASUREMENTS_DELAY = 20
CURRENT_MEASUREMENT_INDEX = 0
N_MEASUREMENTS_TO_AVERAGE = 50
N_SENSORS = len(PINS)
MEASUREMENTS = [array('H', [0] * N_MEASUREMENTS_MEMORY) for _ in range(N_SENSORS)]
N_STDS_ANOMALY = 2
MY_IP = 'not yet configured'
led = machine.Pin(LED_PIN, machine.Pin.OUT)
adcs = [machine.ADC(machine.Pin(pin)) for pin in PINS]

for adc in adcs:
    adc.atten(machine.ADC.ATTN_0DB)  # Set ADC attenuation to 11dB for better range
# Set ADC attenuation
# Binary file setup
MAX_FILE_SIZE = 32 * 1024  # 32KB

ENTRY_FORMAT = "<I" + "I" * len(PINS)  # 1 unsigned int (timestamp) + 5 unsigned ints (sensor values)
ENTRY_SIZE = struct.calcsize(ENTRY_FORMAT)
server_running = True

UDP_IP = "255.255.255.255"  # Broadcast address
UDP_PORT = 4210
DEBUG_LEVEL = 2  # 0 = Off, 1 = all udp logs, 2 = all udp logs and print to console

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
    for i in range(20):
        try:
            print("Syncing time with NTP...")
            time.sleep(1)
            ntptime.settime()  # Synchronizes the ESP32's time with an NTP server
            udp_log(f"Time synchronized: {time.localtime()}", DEBUG_LEVEL)
            print("Time synchronized!")
        except Exception as e:
            print("Failed to sync time:", e)
        if time.localtime()[0] > 2023:
            break


def udp_log(message, level):
    """Send logs over UDP using a pre-initialized socket."""
    if level > 0:
        try:
            log_socket.sendto(f"{DEVICE_ID} at {MY_IP}, {format_timestamp(time.time())}: {message}\n".encode(), (UDP_IP, UDP_PORT))
        except Exception as e:
            print("Logging error:", e)
    if level > 1:
        print(f"Time: {format_timestamp(time.time())}  Message: {message}")


# ====== 1. Binary Save Function ======
def write_header_if_needed(file_path):
    try:
        try:
            file_stat = uos.stat(file_path)
            file_empty = file_stat[6] == 0
        except OSError:
            file_empty = True  # File does not exist, treat as empty

        if file_empty:
            udp_log("Writing file header", DEBUG_LEVEL)
            header_format = "<II"  # DEVICE_ID (uint32), ENTRY_FORMAT length (uint32)
            header_data = struct.pack(header_format, DEVICE_ID, len(ENTRY_FORMAT))
            print(f"header_data = {DEVICE_ID, len(ENTRY_FORMAT)}")
            print("unpacked header_data:", struct.unpack(header_format, header_data))
            with open(file_path, "ab") as f:
                f.write(header_data)
    except Exception as e:
        print("Error writing header:", e)


def file_exists(file_path):
    try:
        uos.stat(file_path)
        return True
    except OSError:
        return False


def should_rotate_due_to_format(file_path):
    print('Starting should_rotate_due_to_format')
    # print(f"file_exists: {file_exists(file_path)}")
    # print(f"uos.stat(file_path)[6]: {uos.stat(file_path)[6]}")
    if not file_exists(file_path) or uos.stat(file_path)[6] == 0:
        print("File does not yet exist or is just empty")
        return False
    try:
        print("Checking file header")
        with open(file_path, "rb") as f:
            header_format = "<II"
            header_size = struct.calcsize(header_format)
            header_data = f.read(header_size)
            if len(header_data) != header_size:
                return True  # Missing or incomplete header
            file_sensor_id, file_format_len = struct.unpack(header_format, header_data)
            return file_sensor_id != DEVICE_ID or file_format_len != len(ENTRY_FORMAT)
    except Exception as e:
        udp_log(f"Header check failed, will rotate file: {e}", DEBUG_LEVEL)
        return True


def save_measurement(timestamp, measurements_array):
    try:
        udp_log("starting save_measurement function", DEBUG_LEVEL)

        try:
            udp_log("Getting file size", DEBUG_LEVEL)
            file_size = uos.stat(LIST_OF_FILES_NAMES[0])[6]
            time.sleep(0.1)
            udp_log(f"File size: {file_size} / {MAX_FILE_SIZE}", DEBUG_LEVEL)
        except OSError:
            udp_log(f"File {LIST_OF_FILES_NAMES[0]} doesn't exist", DEBUG_LEVEL)
            file_size = 0

        if file_size >= MAX_FILE_SIZE or should_rotate_due_to_format(LIST_OF_FILES_NAMES[0]):

            try:
                udp_log("Rotating data files...", DEBUG_LEVEL)
                uos.remove(LIST_OF_FILES_NAMES[-1])
            except OSError:
                pass

            for i in range(N_FILES - 1, 0, -1):
                try:
                    udp_log(f"Renaming {LIST_OF_FILES_NAMES[i - 1]} to {LIST_OF_FILES_NAMES[i]}...", DEBUG_LEVEL)
                    uos.rename(LIST_OF_FILES_NAMES[i - 1], LIST_OF_FILES_NAMES[i])
                except OSError as e:
                    print("Error rotating files:", e)

        write_header_if_needed(LIST_OF_FILES_NAMES[0])

        with open(LIST_OF_FILES_NAMES[0], "ab") as f:
            udp_log(f"Saving binary data: {timestamp}, {measurements_array}", DEBUG_LEVEL)
            f.write(struct.pack(ENTRY_FORMAT, timestamp, *measurements_array))
    except Exception as e:
        print("Error saving binary data:", e)


def read_measurements(last_n=None):
    measurements = []

    def skip_header_and_get_entry_size(f):
        header_format = "<II"
        header_size = struct.calcsize(header_format)
        header_data = f.read(header_size)
        if len(header_data) != header_size:
            raise Exception("Invalid or missing header")
        _, entry_format_length = struct.unpack(header_format, header_data)
        return header_size, entry_format_length

    if last_n is None:
        for file_path in LIST_OF_FILES_NAMES:
            udp_log(f"Reading binary data from {file_path}", DEBUG_LEVEL)
            try:
                with open(file_path, "rb") as f:
                    header_size, _ = skip_header_and_get_entry_size(f)
                    while True:
                        data = f.read(ENTRY_SIZE)
                        if not data:
                            break
                        measurements.append(struct.unpack(ENTRY_FORMAT, data))
            except OSError:
                pass
            except Exception as e:
                print(f"Error reading binary data from {file_path}: {e}")

    else:
        udp_log(f"Reading the last {last_n} measurements from {LIST_OF_FILES_NAMES[0]}", DEBUG_LEVEL)
        try:
            with open(LIST_OF_FILES_NAMES[0], "rb") as f:
                header_size, _ = skip_header_and_get_entry_size(f)
                f.seek(0, 2)
                file_size = f.tell()
                total_entries = (file_size - header_size) // ENTRY_SIZE

                entries_to_read = min(last_n, total_entries)
                f.seek(header_size + (total_entries - entries_to_read) * ENTRY_SIZE)

                for _ in range(entries_to_read):
                    data = f.read(ENTRY_SIZE)
                    if not data:
                        break
                    measurements.append(struct.unpack(ENTRY_FORMAT, data))
        except OSError:
            pass
        except Exception as e:
            print(f"Error reading binary data from {LIST_OF_FILES_NAMES[0]}: {e}")

    return measurements


def check_for_anomaly(measurements_current):
    global CURRENT_MEASUREMENT_INDEX, MEASUREMENTS

    # Update cyclic buffer
    index = CURRENT_MEASUREMENT_INDEX % N_MEASUREMENTS_MEMORY
    for i in range(N_SENSORS):
        MEASUREMENTS[i][index] = measurements_current[i]

    CURRENT_MEASUREMENT_INDEX += 1

    # Compute the past range indices
    mean_start = (CURRENT_MEASUREMENT_INDEX - N_MEASUREMENTS_MEMORY) % N_MEASUREMENTS_MEMORY
    mean_end = (CURRENT_MEASUREMENT_INDEX - N_MEASUREMENTS_DELAY) % N_MEASUREMENTS_MEMORY

    def get_window(sensor_array):
        if mean_start < mean_end:
            return sensor_array[mean_start:mean_end]
        else:
            return sensor_array[mean_start:] + sensor_array[:mean_end]

    # Check each sensor
    for i in range(N_SENSORS):
        window = get_window(MEASUREMENTS[i])
        n = len(window)
        if n == 0:
            continue  # avoid division by zero

        mean = sum(window) / n
        std = (sum((x - mean) ** 2 for x in window) / n) ** 0.5

        if measurements_current[i] > mean + N_STDS_ANOMALY * std:
            return True

    return False


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
        global MY_IP
        MY_IP = wlan.ifconfig()[0]
        udp_log('Connected to WiFi', level=DEBUG_LEVEL)
        udp_log(f'Network config: {wlan.ifconfig()}', level=DEBUG_LEVEL)
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

    server = await asyncio.start_server(handle_client, HOST, SERVER_PORT)
    print(f"File server running on {HOST}:{SERVER_PORT}")

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
            list_of_measurements_arrays = [array('H', [0] * N_MEASUREMENTS_TO_AVERAGE) for _ in range(N_SENSORS)]
            led.value(1)
            for i in range(N_MEASUREMENTS_TO_AVERAGE):
                for j in range(N_SENSORS):
                    reading_value = adcs[j].read()
                    list_of_measurements_arrays[j][i] = reading_value
                await asyncio.sleep(MEASUREMENT_TIME_INTERVAL / N_MEASUREMENTS_TO_AVERAGE)
            led.value(0)

            # Average the measurements
            list_of_averaged_measurements = [sum(measurements) // N_MEASUREMENTS_TO_AVERAGE for measurements in
                                             list_of_measurements_arrays]
            print(list_of_averaged_measurements)
            # Check for anomalies
            # not yet implemented
            # Save in binary format
            save_measurement(timestamp, list_of_averaged_measurements)
            udp_log(f"Measurement: {timestamp} ({format_timestamp(timestamp)}), {list_of_averaged_measurements}",
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
