from results_analysis_utils import read_from_local_bin_multiple
from request_data_over_ip import request_and_merge_files
from matplotlib import pyplot as plt
import pandas as pd
IPS_AND_PORTS = {
    1: [12345, '10.100.102.24'],
    2: [12346, '10.100.102.23']
}

# %% download and merge files:
n_files = 3  # There are at most 20 files of 32kb each on the ESP32
file_list = [f"file_{i}.bin" for i in range(n_files)]

output_file_path_1 = request_and_merge_files(file_list, "merged_files_1", esp32_port=IPS_AND_PORTS[1][0], esp32_ip=IPS_AND_PORTS[1][1])
output_file_path_2 = request_and_merge_files(file_list, "merged_files_2", esp32_port=IPS_AND_PORTS[2][0], esp32_ip=IPS_AND_PORTS[2][1])

# %% read df:
df = read_from_local_bin_multiple([output_file_path_1, output_file_path_2])
last_measurement_time = df['date_time'].max()
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

# Group by 'source_index' and plot each group with a different color
for source_index, group in df_narrowed.groupby('source_index'):
    ax.plot(group['date_time'], group['value_1'], marker='.', alpha=0.7, label=f"Source {source_index}")

ax.set_title('Value 1 Over Time by Source Index')
ax.set_xlabel('Date Time')
ax.set_ylabel('Value 1')
ax.legend()
plt.show()
