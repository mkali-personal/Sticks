import serial
import csv

# Open the serial port (replace with your ESP32 COM port)
ser = serial.Serial('COM8', 115200, timeout=1)  # Replace 'COM3' with the correct port

# Open a CSV file to write the data
with open('sensor_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Index', 'Timestamp', 'MQ9', 'MQ135'])  # Write header row

    for i in range(25000):
        line = ser.readline().decode('utf-8').strip()  # Read a line from the ESP32
        data = line.split(',')  # Split by commas
        if data[0].isdigit():
            #Pring data values in csv format:
            if i % 1000 == 0:
                print(f'{data[0]},{data[1]},{data[2]},{data[3]}')
            writer.writerow(data)  # Write the data to the CSV file

ser.close()  # Close the serial connection
# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import convolve
from scipy.stats import norm


df = pd.read_csv('sensor_data.csv')
# Define Gaussian kernel
std_gaussian = 5
kernel_size = std_gaussian * 6  # Ensure the kernel captures enough of the Gaussian tail
x = np.linspace(-kernel_size // 2, kernel_size // 2, kernel_size)
gaussian_kernel = norm.pdf(x, scale=std_gaussian)  # Gaussian of height 1
gaussian_kernel /= gaussian_kernel.sum()  # Normalize so it doesn't change total magnitude

# Convolve the data with the Gaussian
df['mq135_convolved'] = convolve(df['mq135'], gaussian_kernel, mode='same')
df['time_hms'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%H:%M:%S')


df.head()
# %%
df.iloc[24000:-kernel_size].plot(x='time_hms', y=['mq9', 'mq135', 'mq135_convolved'], figsize=(10, 5), title='MQ9 and MQ135 data')
plt.show()
