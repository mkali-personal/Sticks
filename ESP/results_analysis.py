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
from request_data_over_ip import request_and_merge_files


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
        df = df.iloc[:-kernel_size]
    return df


# %% download and merge files:
n_files = 2  # There are at most 20 files of 32kb each on the ESP32
file_list = [f"file_{i}.bin" for i in range(n_files)]
output_file_path = request_and_merge_files(file_list, "merged_files - new_format")

# %% read df:
df = read_from_local_bin(output_file_path)

# %% plot df:
# %%
df_narrowed = df[df['date_time'] >= (pd.Timestamp.now() - pd.Timedelta(minutes=230))]

for col, color in zip(['mq9_value', 'mq135_value', 'mq2_value', 'mq7_value', 'mq3_value'], ['blue', 'red', 'green', 'purple', 'orange']):
    plt.plot(df_narrowed['date_time'], df_narrowed[col], marker='.', alpha=0.3, markersize=4, color=color, label=col)

plt.ylim(bottom=0)
plt.title('Sensor Data Over Time')
plt.legend()
plt.show()
# %%
# std and mean:
df_narrowed.plot.hist(y='mq135_value', bins=20, alpha=0.5, color='blue', edgecolor='black')
mean = df_narrowed['mq135_value'].mean()
std = df_narrowed['mq135_value'].std()
plt.axvline(mean, color='red', linestyle='dashed', linewidth=1)
plt.axvline(mean + std, color='green', linestyle='dashed', linewidth=1)
plt.axvline(mean - std, color='green', linestyle='dashed', linewidth=1)
plt.title(f'standard deviation: {std:.2f}, mean: {mean:.2f}')
plt.show()

# # present the fourier transform of the measurements:
# def plot_fourier_transform(df):
#     # Perform Fourier Transform
#     N = len(df)
#     T = 1.0  # Sampling interval (1 second)
#     yf = np.fft.fft(df['mq135_value'])
#     xf = np.fft.fftfreq(N, T)[:N // 2]
#
#     # Plot the Fourier Transform
#     plt.figure(figsize=(10, 5))
#     plt.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
#     plt.title('Fourier Transform of MQ135 Data')
#     plt.xlabel('Frequency (Hz)')
#     plt.ylabel('Amplitude')
#     plt.grid()
#     plt.show()
#
# plot_fourier_transform(df_narrowed)
#
