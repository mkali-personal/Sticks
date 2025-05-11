from results_analysis_utils import read_from_local_bin_multiple, save_fig_safe
from request_data_over_ip import request_and_merge_files
from matplotlib import pyplot as plt
import pandas as pd
IPS_AND_PORTS = {
    1: [12345, '192.168.1.142'],
    2: [12346, '192.168.1.46']
}

# %% download and merge files:
n_files = 8  # There are at most 20 files of 32kb each on the ESP32
file_list = [f"file_{i}.bin" for i in range(n_files)]
# 'data\\20250506\\merged_files_1.bin'  #
output_file_path_1 = request_and_merge_files(file_list, "merged_files_1", esp32_port=IPS_AND_PORTS[1][0], esp32_ip=IPS_AND_PORTS[1][1])
output_file_path_2 = request_and_merge_files(file_list, "merged_files_2", esp32_port=IPS_AND_PORTS[2][0], esp32_ip=IPS_AND_PORTS[2][1])

# %% read df:
df = read_from_local_bin_multiple([output_file_path_1, output_file_path_2])
last_measurement_time = df['date_time'].max()
# %%
# List of columns to melt
value_columns = [
    "value_1", "value_2", "value_3"
]

# Melt the DataFrame
df_melted = df.melt(
    id_vars=["timestamp_s", "date_time", "source_index"],  # keep these columns
    value_vars=value_columns,
    var_name="key",
    value_name="value"
)
# remove rows where value is NaN:
df_melted = df_melted.dropna(subset=["value"])

print(df_melted)


# %%
start_time_dict = {'relative': last_measurement_time - pd.Timedelta(minutes=120),
                   'absolute': last_measurement_time.replace(hour=16, minute=8, second=0, microsecond=0),
                   'far_past': last_measurement_time.replace(year=2020, month=1, day=1),}
end_time_dict = {'relative': last_measurement_time - pd.Timedelta(hours=11),
                 'absolute': last_measurement_time.replace(hour=8, minute=40, second=0, microsecond=0),
                 'now': last_measurement_time}
start_time = start_time_dict['far_past']
end_time = end_time_dict['now']

df_narrowed = df_melted[(df_melted['date_time'] >= start_time) & (df_melted['date_time'] <= end_time)]
# df_narrowed = df[df['date_time'] >= (pd.Timestamp.now() - pd.Timedelta(minutes=20))]
# Group by (source_in, key)
grouped = df_narrowed.groupby(["source_index", "key"])

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

for (source, key), group in grouped:
    if group["value"].notna().any():
        ax.plot(group["date_time"], group["value"], label=f"{key} (source {source})")

ax.set_xlabel("Timestamp (s)")
ax.set_ylabel("Value")
ax.set_title("Sensor Values by Source and Key")
ax.legend()
plt.tight_layout()
save_fig_safe(r"manual saves\correlated results in uncorrelated sensors")
plt.show()
