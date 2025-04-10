import serial
import csv
import struct
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve
from scipy.stats import norm
import time


# ====== 3. Timestamp Formatting ======
def format_timestamp(timestamp):
    TIMEZONE_OFFSET = 3 * 3600  # Offset in seconds (2 hours)
    utc_time = time.localtime(timestamp + TIMEZONE_OFFSET)
    return "{:02}/{:02}/{:02} {:02}:{:02}:{:02}".format(
        utc_time[0], utc_time[1], utc_time[2],
        utc_time[3], utc_time[4], utc_time[5]
    )


# Read from serial port:
def from_serial_port_to_csv():
    # Open the serial port (replace with your ESP32 COM port)
    ser = serial.Serial('COM8', 115200, timeout=1)  # Replace 'COM3' with the correct port

    # Open a CSV file to write the data
    with open('sensor_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index', 'timestamp', 'mq9', 'mq135'])  # Write header row

        for i in range(43010):
            line = ser.readline().decode('utf-8').strip()  # Read a line from the ESP32
            data = line.split(',')  # Split by commas
            if data[0].isdigit():
                # Pring data values in csv format:
                if i % 1000 == 0:
                    print(f'{data[0]},{data[1]},{data[2]},{data[3]}')
                writer.writerow(data)  # Write the data to the CSV file

    ser.close()  # Close the serial connection


def read_from_local_bin(file_path):
    """
        Convert ESP32 binary sensor data to Pandas DataFrame

        Args:
            file_path (str): Path to data.bin file

        Returns:
            pd.DataFrame: DataFrame with columns [timestamp_ms, mq9_value, mq135_value]
        """
    # Binary format specification (must match ESP32 code)
    entry_format = "<IIIIII"  # 3 unsigned integers (timestamp, mq9, mq135)
    entry_size = struct.calcsize(entry_format)

    data = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(entry_size)
            if not chunk:
                break
            try:
                # Unpack binary data
                timestamp, mq9, mq135, mq2, mq7, mq3 = struct.unpack(entry_format, chunk)
                data.append({
                    'timestamp_s': timestamp, # and  # mq9, mq135, mq2, mq7, mq3
                    'mq9_value': mq9,
                    'mq135_value': mq135,
                    'mq2_value': mq2,
                    'mq7_value': mq7,
                    'mq3_value': mq3

                })
            except struct.error as e:
                print(f"Error unpacking data: {e}")
                continue

    # Create DataFrame
    df = pd.DataFrame(data)

    # Add human-readable datetime if needed
    if not df.empty:
        df['timestamp_s'] += 3 * 3600  # delete this when the data is fixed
        df['date_time'] = pd.to_datetime(df['timestamp_s'], unit='s', origin='2000-01-01')

        # Define Gaussian kernel
        std_gaussian = 10
        kernel_size = std_gaussian * 6  # Ensure the kernel captures enough of the Gaussian tail
        x = np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size)
        gaussian_kernel = norm.pdf(x, scale=std_gaussian)  # Gaussian of height 1
        gaussian_kernel /= gaussian_kernel.sum()  # Normalize so it doesn't change total magnitude

        for col in ['mq9_value', 'mq135_value', 'mq2_value', 'mq7_value', 'mq3_value']:
            # Convolve the data with the Gaussian
            df[f"{col}_convolved"] = convolve(df[col], gaussian_kernel, mode='same')
        # df = df.iloc[:-kernel_size]
    return df