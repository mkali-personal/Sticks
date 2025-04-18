from results_analysis_utils import read_from_local_bin
from request_data_over_ip import request_and_merge_files
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

# %% download and merge files:
n_files = 2  # There are at most 20 files of 32kb each on the ESP32
file_list = [f"file_{i}.bin" for i in range(n_files)]
output_file_path = request_and_merge_files(file_list, "merged_files")

# %% read df:
df = read_from_local_bin(output_file_path)
last_measurement_time = df['date_time'].max()

# %% plot df:
# %%
start_time_dict = {'relative': last_measurement_time - pd.Timedelta(minutes=15),
                   'absolute': last_measurement_time.replace(hour=16, minute=8, second=0, microsecond=0),
                   'far_past': last_measurement_time.replace(year=2020, month=1, day=1),}
end_time_dict = {'relative': last_measurement_time - pd.Timedelta(hours=11),
                 'absolute': last_measurement_time.replace(hour=8, minute=40, second=0, microsecond=0),
                 'now': last_measurement_time}
start_time = start_time_dict['far_past']
end_time = end_time_dict['now']

df_narrowed = df[(df['date_time'] >= start_time) & (df['date_time'] <= end_time)]
# df_narrowed = df[df['date_time'] >= (pd.Timestamp.now() - pd.Timedelta(minutes=20))]
fig, ax = plt.subplots(figsize=(18, 12))
for col, color in zip(['mq9_value', 'mq135_value', 'mq2_value', 'mq7_value', 'mq3_value'], ['blue', 'red', 'green', 'purple', 'orange']):
    plt.plot(df_narrowed['date_time'], df_narrowed[col], marker='.', alpha=0.3, color=color, label=col)  #

plt.ylim(bottom=0)
plt.title('Sensor Data Over Time')
plt.legend()
plt.ylim(0, 500)
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
