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
                #Pring data values in csv format:
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
    entry_format = "<III"  # 3 unsigned integers (timestamp, mq9, mq135)
    entry_size = struct.calcsize(entry_format)

    data = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(entry_size)
            if not chunk:
                break
            try:
                # Unpack binary data
                timestamp, mq9, mq135 = struct.unpack(entry_format, chunk)
                data.append({
                    'timestamp_s': timestamp,
                    'mq9_value': mq9,
                    'mq135_value': mq135
                })
            except struct.error as e:
                print(f"Error unpacking data: {e}")
                continue

    # Create DataFrame
    df = pd.DataFrame(data)

    # Add human-readable datetime if needed
    if not df.empty:
        df['timestamp_s'] += 3*3600  # delete this when the data is fixed
        df['date_time'] = pd.to_datetime(df['timestamp_s'], unit='s', origin='2000-01-01')
        df = df[['timestamp_s', 'date_time', 'mq9_value', 'mq135_value']]
        df = df[df['timestamp_s'] > 100000]
    return df

# %%
# df = pd.read_csv('sensor_data.csv')
# df_0 = read_from_local_bin('data/data_file_0.bin')
df_1 = read_from_local_bin('merged_output.bin')

df = pd.concat([df_1], ignore_index=True)

# Define Gaussian kernel
std_gaussian = 20
kernel_size = std_gaussian * 6  # Ensure the kernel captures enough of the Gaussian tail
x = np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size)
gaussian_kernel = norm.pdf(x, scale=std_gaussian)  # Gaussian of height 1
gaussian_kernel /= gaussian_kernel.sum()  # Normalize so it doesn't change total magnitude


# Convolve the data with the Gaussian
df['mq135_convolved'] = convolve(df['mq135_value'], gaussian_kernel, mode='same')
df = df.iloc[:-kernel_size]
#


df.tail()
# %%
# df[(df['date_time'] >= '2025-03-29 06:40:00') & (df['date_time'] <= '2025-03-29 07:50:00')].plot(x='date_time', y=['mq9_value', 'mq135_value'], figsize=(10, 5), title='MQ9 and MQ135 data')
df.plot(x='date_time', y=['mq9_value', 'mq135_value'], figsize=(10, 5), title='MQ9 and MQ135 data')
plt.show()
# %%

from datetime import datetime, timedelta

# Given number of seconds since 2020-01-01 00:00:00
seconds_since_2020 = 796632341

# Define the start time
start_time = datetime(2020, 1, 1, 0, 0, 0)

# Calculate the new date-time
converted_time = start_time + timedelta(seconds=seconds_since_2020)
print("Converted date-time:", converted_time)

