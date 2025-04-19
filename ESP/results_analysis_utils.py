import serial
import csv
import time
import struct
import pandas as pd
import numpy as np
from scipy.signal import convolve
from scipy.stats import norm


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


# ====== Pandas Parser ======
def read_from_local_bin(file_path):
    data = []
    try:
        with open(file_path, 'rb') as f:
            header_format = "<II"
            header_size = struct.calcsize(header_format)
            header_data = f.read(header_size)
            DEVICE_ID, entry_format_length = struct.unpack(header_format, header_data)

            # Reconstruct entry_format based on number of uint32s
            num_fields = entry_format_length - 2  # -2 for the timestamp and the constant <
            entry_format = '<' + 'I' + 'I' * num_fields
            entry_size = struct.calcsize(entry_format)

            while True:
                chunk = f.read(entry_size)
                if not chunk:
                    break
                try:
                    values = struct.unpack(entry_format, chunk)
                    record = {'timestamp_s': values[0]}
                    for i, val in enumerate(values[1:], 1):
                        record[f'value_{i}'] = val
                    data.append(record)
                except struct.error as e:
                    print(f"Error unpacking data: {e}")
                    continue

    except Exception as e:
        print(f"Error reading binary file: {e}")

    df = pd.DataFrame(data)

    if not df.empty:
        df['timestamp_s'] += 3 * 3600  # temporary timezone offset
        df['date_time'] = pd.to_datetime(df['timestamp_s'], unit='s', origin='2000-01-01')

        std_gaussian = 10
        kernel_size = std_gaussian * 6
        x = np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size)
        gaussian_kernel = norm.pdf(x, scale=std_gaussian)
        gaussian_kernel /= gaussian_kernel.sum()

        for col in df.columns:
            if col.startswith('value_'):
                df[f"{col}_convolved"] = convolve(df[col], gaussian_kernel, mode='same')

    return df


def read_from_local_bin_multiple(file_paths):
    if isinstance(file_paths, str):
        # If a single file path is provided, process it as usual
        return read_from_local_bin(file_paths)

    if isinstance(file_paths, list):
        all_dfs = []
        for idx, file_path in enumerate(file_paths):
            df = read_from_local_bin(file_path)
            if not df.empty:
                df['source_index'] = idx  # Add a column for the index of the DataFrame
                all_dfs.append(df)

        # Perform UNION ALL (concatenation) on all DataFrames
        if all_dfs:
            concatenated_df = pd.concat(all_dfs, ignore_index=True)
            ordered_df = concatenated_df.sort_values(by='date_time', ascending=True)
            return ordered_df
