import pandas as pd
from geopy.distance import distance
import numpy as np
from shapely.wkt import loads as load_wkt
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib import use
# use('Qt5Agg')  # if you want interactive plots
# plt.ion()

# %% Constants:
# N is the number of grids in each direction (N x N grids in total).
# It is most efficient when N is a power of 2, but not very crucial.
N_LOG = 8  # [dimensionless]
N = 2 ** N_LOG  # [dimensionless]
RESOLUTION_METERS = 80  # meters
# note: sector size is N * RESOLUTION_METERS by N * RESOLUTION_METERS.
LON_0, LAT_0 = 35.06362311584926, 32.918285285257184  # the southest-westest point in the map [geo-coordinates]
# Values related to the efficiency map:
RADIUS_METERS = 2000  # the radius of the efficiency map in meters [meters].
RADIUS_MAX_VALUE = 700  # The radius at which the efficiency is best (maximal) [meters].
CONSTANT_EFFICIENCY_SHIFT = 0  # the minimal value of efficiency, far from the point of high efficiency [dimensionless]
VALUE_WIDTH = 400  # The width of the area of high efficiency [meters].
# Dummy data:
DF_VALUES = pd.DataFrame({'id': range(31),
                           'value': np.ones(31),
                           'wkt': ['POLYGON ((35.085869 32.939251, 35.092134 32.939323, 35.092821 32.94278, 35.08647 32.942492, 35.085869 32.939251))',
                                    'POLYGON ((35.09634 32.935649, 35.097027 32.931255, 35.099859 32.931399, 35.100031 32.935001, 35.09634 32.935649))',
                                    'POLYGON ((35.085783 32.928373, 35.084581 32.924339, 35.092993 32.925563, 35.091619 32.928733, 35.085783 32.928373))',
                                    'POLYGON ((35.081148 32.930895, 35.08441 32.931471, 35.083036 32.935577, 35.080805 32.935793, 35.081148 32.930895))',
                                    'POLYGON ((35.118313 32.95913, 35.159855 32.944869, 35.170498 32.960282, 35.160542 32.971804, 35.118313 32.95913))',
                                    'POLYGON ((35.082607 32.976556, 35.096855 32.974972, 35.096512 32.982604, 35.086212 32.984188, 35.082607 32.976556))',
                                    'POLYGON ((35.125179 32.9839, 35.126038 32.980444, 35.128098 32.983468, 35.125179 32.9839))',
                                    'POLYGON ((35.125008 32.939683, 35.129471 32.940259, 35.132732 32.938819, 35.131359 32.942996, 35.133934 32.948326, 35.136509 32.949047, 35.140457 32.944725, 35.139942 32.939539, 35.138226 32.935649, 35.136852 32.932479, 35.1408 32.931759, 35.147495 32.935073, 35.14595 32.941268, 35.147667 32.946166, 35.151787 32.945013, 35.15419 32.942132, 35.158482 32.942852, 35.158138 32.948038, 35.155392 32.9538, 35.150585 32.953656, 35.14698 32.949911, 35.142174 32.953224, 35.138226 32.956969, 35.131531 32.955961, 35.129128 32.950775, 35.126553 32.946742, 35.123806 32.943861, 35.125008 32.939683))',
                                    'POLYGON ((35.079174 32.957257, 35.081577 32.959274, 35.083466 32.957545, 35.083637 32.955241, 35.085869 32.954809, 35.088272 32.954953, 35.088959 32.956681, 35.09119 32.959706, 35.092049 32.96273, 35.091362 32.965179, 35.088959 32.967627, 35.088615 32.964459, 35.087929 32.960714, 35.085697 32.96273, 35.085011 32.967051, 35.078831 32.969356, 35.073853 32.967051, 35.074196 32.96201, 35.072136 32.958554, 35.074024 32.957689, 35.076427 32.959994, 35.079174 32.957257))',
                                    'POLYGON ((35.192642 32.987932, 35.210495 32.982172, 35.224228 32.998874, 35.211868 33.012694, 35.192642 32.987932))',
                                    'POLYGON ((35.152817 33.060471, 35.130844 33.040328, 35.14801 33.034571, 35.163803 33.053565, 35.152817 33.060471))',
                                    'POLYGON ((35.286026 33.030542, 35.261307 32.940115, 35.386963 32.974684, 35.399323 33.036874, 35.286026 33.030542))',
                                    'POLYGON ((35.192642 33.053565, 35.200195 33.053565, 35.200195 33.057019, 35.192642 33.057019, 35.192642 33.053565))',
                                    'POLYGON ((35.213928 33.042054, 35.211182 33.02939, 35.222855 33.02939, 35.226288 33.039752, 35.213928 33.042054))',
                                    'POLYGON ((35.195045 33.040615, 35.185089 33.034859, 35.190582 33.028239, 35.198822 33.032844, 35.195045 33.040615))',
                                    'POLYGON ((35.208092 33.0504, 35.215302 33.044357, 35.219765 33.050976, 35.213585 33.056443, 35.208092 33.0504))',
                                    'POLYGON ((35.197449 33.050256, 35.189381 33.042054, 35.196419 33.045364, 35.197449 33.050256))',
                                    'POLYGON ((35.196419 33.025648, 35.20895 33.025792, 35.206203 33.03011, 35.196419 33.025648))',
                                    'POLYGON ((35.184574 33.047522, 35.176506 33.038745, 35.181828 33.039752, 35.184574 33.047522))',
                                    'POLYGON ((35.217876 33.047378, 35.221138 33.042486, 35.231094 33.047091, 35.217876 33.047378))',
                                    'POLYGON ((35.205173 33.043205, 35.20277 33.037881, 35.207233 33.040615, 35.205173 33.043205))',
                                    'POLYGON ((35.20071 33.056731, 35.198822 33.0504, 35.209465 33.055148, 35.20071 33.056731))',
                                    'POLYGON ((35.195904 33.033708, 35.194016 33.02536, 35.212212 33.027519, 35.211353 33.033852, 35.195904 33.033708))',
                                    'POLYGON ((35.210667 33.050688, 35.216503 33.036586, 35.231094 33.033708, 35.219936 33.050976, 35.210667 33.050688))',
                                    'POLYGON ((35.195904 33.053134, 35.185089 33.050976, 35.184231 33.034715, 35.191612 33.03673, 35.195904 33.053134))',
                                    'POLYGON ((35.208263 33.05558, 35.213242 33.038457, 35.218048 33.037162, 35.221138 33.041335, 35.208263 33.05558))',
                                    'POLYGON ((35.180798 33.012406, 35.171528 33.023921, 35.14595 33.017444, 35.140285 33.009671, 35.180798 33.012406))',
                                    'POLYGON ((35.266113 33.056299, 35.260448 33.035435, 35.30817 33.056443, 35.266113 33.056299))',
                                    'POLYGON ((35.214615 32.961434, 35.203629 32.938386, 35.219421 32.938386, 35.231094 32.955097, 35.214615 32.961434))',
                                    'POLYGON ((35.342331 33.069103, 35.323792 33.057594, 35.337524 33.049537, 35.35675 33.057594, 35.342331 33.069103))',
                                    'POLYGON ((35.120544 33.067952, 35.082779 33.051839, 35.082779 33.034571, 35.110245 33.036874, 35.120544 33.067952))']})

# %% Functions:
def spatial_join(grids_df, values_df):
    """
    Perform a spatial join to check if coordinates in grids_df fall within the polygons in values_df.
    Utilizes the fact that the polygons are rectangles and filters grids_df based on the bounding box of each polygon.

    Args:
        grids_df (pd.DataFrame): DataFrame with columns ['longitude_center', 'latitude_center', 'i', 'j'].
        values_df (pd.DataFrame): DataFrame with columns ['id', 'value', 'wkt'].

    Returns:
        pd.DataFrame: A DataFrame representing the left join of grids_df and values_df.
    """
    # Parse the WKT polygons into shapely objects
    values_df['geometry'] = values_df['wkt'].apply(load_wkt)

    def process_polygon(row):
        polygon = row['geometry']
        lon_min, lat_min, lon_max, lat_max = polygon.bounds  # Get bounding box

        # Filter grids_df within the bounding box
        filtered_grids = grids_df[
            (grids_df['lon'] > lon_min) &
            (grids_df['lon'] < lon_max) &
            (grids_df['lat'] > lat_min) &
            (grids_df['lat'] < lat_max)
        ]

        # Check if points in the filtered DataFrame are contained in the polygon
        filtered_grids = filtered_grids[filtered_grids.apply(
            lambda grid_row: polygon.contains(Point(grid_row['lon'], grid_row['lat'])), axis=1
        )]
        # Add matching id and value
        filtered_grids['id'] = row['id']
        filtered_grids['value'] = row['value']
        if len(filtered_grids) > 0:
            filtered_grids['value'] /= len(filtered_grids)
            # drop geometry column:
            filtered_grids.drop(columns=['lon', 'lat'], inplace=True)
        return filtered_grids

    kaki = values_df.apply(process_polygon, axis=1).tolist()

    # Apply the process to each row in values_df and concatenate results
    result_df = pd.concat(kaki, ignore_index=True)

    return result_df


def generate_flatten_value_map(result_df, N, different_layers_for_different_ids=False):
    """
    Generate a 2D numpy array where the (i, j) element is the sum of 'value' in result_df
    for rows with 'i' and 'j' equal to the respective indices.

    Args:
        result_df (pd.DataFrame): DataFrame with columns ['i', 'j', 'value', 'id'].

    Returns:
        np.ndarray: 2D array with summed values.
        @param N:
    """
    # Initialize a 2D array with zeros
    if different_layers_for_different_ids:
        result_df["k"] = pd.factorize(result_df["id"])[0]  # assign a number to each ID
        heat_map = np.zeros((N, N, len(result_df["k"].unique())))
    else:
        heat_map = np.zeros((N, N))

    # Iterate over the rows of the DataFrame and sum values into the array
    for _, row in result_df.iterrows():
        if different_layers_for_different_ids:
            i, j, k, value = int(row['i']), int(row['j']), int(row['k']), row['value']
            heat_map[i, j, k] += value
        else:
            i, j, value = int(row['i']), int(row['j']), row['value']
            heat_map[i, j] += value

    return heat_map


def generate_efficiency_map(radius_meters,
                            resolution_meters,
                            radius_max_value,
                            value_width,
                            constant_value):  # What we called B

    x_dummy = np.arange(-radius_meters, radius_meters, resolution_meters)
    y_dummy = np.arange(-radius_meters, radius_meters, resolution_meters)

    X, Y = np.meshgrid(x_dummy, y_dummy)
    R = np.sqrt(X ** 2 + Y ** 2)
    efficiency_map = np.exp(- (R - radius_max_value) ** 2 / (2 * value_width ** 2)) + constant_value
    # Pad B to be the size of A:# Pad B to match the size of A_padded:
    return efficiency_map


def generate_maps(N, RESOLUTION_METERS, LAT_0, LON_0, df_values, different_layers_for_different_ids=False):
    lon_step = distance(meters=RESOLUTION_METERS).destination((LAT_0, LON_0), 90)  # 90 degrees for east
    delta_lon = lon_step.longitude - LON_0
    lat_step = distance(meters=RESOLUTION_METERS).destination((LAT_0, LON_0), 0)  # 0 degrees for north
    delta_lat = lat_step.latitude - LAT_0

    # Create a pandas dataframe with 2 nested indices, each one containing 10 values (1..10) (100 rows in total):
    df_grids = pd.DataFrame(index=pd.MultiIndex.from_product([range(N), range(N)], names=['i', 'j']))
    df_grids.reset_index(inplace=True)
    # df.columns = ['i', 'j']
    df_grids['lon'] = LON_0 + df_grids['i'] * delta_lon
    df_grids['lat'] = LAT_0 + df_grids['j'] * delta_lat

    LON_1, LAT_1 = df_grids['lon'].max(), df_grids['lat'].max()

    df_joined = spatial_join(df_grids, df_values)
    value_map = generate_flatten_value_map(df_joined, N=N, different_layers_for_different_ids=different_layers_for_different_ids)  # What we called A
    efficiency_map = generate_efficiency_map(RADIUS_METERS, RESOLUTION_METERS, RADIUS_MAX_VALUE, VALUE_WIDTH,
                                             CONSTANT_EFFICIENCY_SHIFT)
    # The padding is important for the convolution, to avoid circular world effects.
    # For sanity checks:
    # A_padded *= 0
    # i_0, j_0  = 0, 0
    # i_1, j_1 = 0, 255
    # A_padded[i_0, j_0] = 1
    # A_padded[i_1, j_1] = 1

    return value_map, efficiency_map, delta_lon, delta_lat, LON_1, LAT_1


def convolution_2d_fft(value_map, efficiency_map, lon_0, lat_0, lon_1, lat_1, delta_lon, delta_lat):
    value_map_padded = np.pad(value_map, ((0, value_map.shape[0]), (0, value_map.shape[1])), mode='constant')
    efficiency_map_padded = np.pad(efficiency_map, (
        (0, value_map_padded.shape[0] - efficiency_map.shape[0]),
        (0, value_map_padded.shape[1] - efficiency_map.shape[1])),
                                   mode='constant')

    value_map_fft = np.fft.fft2(value_map_padded)
    efficiency_map_fft = np.fft.fft2(efficiency_map_padded)

    multiplication_in_k_space = value_map_fft * efficiency_map_fft
    convolution_in_real_space = np.real(np.fft.ifft2(multiplication_in_k_space))

    convolution_in_real_space = convolution_in_real_space[0:value_map.shape[0] + efficiency_map.shape[0], 0:value_map.shape[1] + efficiency_map.shape[1]]  # Remove the padding.

    convolution_for_plotting = np.flip(convolution_in_real_space.T, axis=0)  # the transpose makes the matrix's vertical axis to be the latitude,and the flip makes the latitude to be from north to south.
    # convolution_for_plotting = convolution_for_plotting[0:value_map.shape[0] , 0:value_map.shape[1]]  # Remove the padding.
    extent_for_plotting = (lon_0 - efficiency_map.shape[0] // 2 * delta_lon,
                           lon_1 + efficiency_map.shape[0] // 2 * delta_lon,
                           lat_0 - efficiency_map.shape[1] // 2 * delta_lat,
                           lat_1 + efficiency_map.shape[1] // 2 * delta_lat)  # Those are the actual coordinates of the grid's corners, in real world's geo-coordinates.
    return convolution_for_plotting, extent_for_plotting

# %% Generate the maps:
def generate_df_spatial_join(N, RESOLUTION_METERS, LAT_0, LON_0, df_values):
    lon_step = distance(meters=RESOLUTION_METERS).destination((LAT_0, LON_0), 90)  # 90 degrees for east
    delta_lon = lon_step.longitude - LON_0
    lat_step = distance(meters=RESOLUTION_METERS).destination((LAT_0, LON_0), 0)  # 0 degrees for north
    delta_lat = lat_step.latitude - LAT_0

    # Create a pandas dataframe with 2 nested indices, each one containing 10 values (1..10) (100 rows in total):
    df_grids = pd.DataFrame(index=pd.MultiIndex.from_product([range(N), range(N)], names=['i', 'j']))
    df_grids.reset_index(inplace=True)
    # df.columns = ['i', 'j']
    df_grids['lon'] = LON_0 + df_grids['i'] * delta_lon
    df_grids['lat'] = LAT_0 + df_grids['j'] * delta_lat
    df_joined = spatial_join(df_grids, df_values)
    return df_joined

df_joined = generate_df_spatial_join(N, RESOLUTION_METERS, LAT_0, LON_0, DF_VALUES)
efficiency_map = generate_efficiency_map(RADIUS_METERS, RESOLUTION_METERS, RADIUS_MAX_VALUE, VALUE_WIDTH,
                                             CONSTANT_EFFICIENCY_SHIFT)
ids = df_joined['id'].unique().tolist()  # list of all the ids in the data.
relative_contributions = np.zeros(len(ids))  # here the contribution of each polygon will be stored
i, j = 100, 200  # Assume you found this coordinate to be the best coordinate

h, w = efficiency_map.shape  # Shape of B (small array)

# Compute valid slice ranges
A_i_min = max(i - h // 2, 0)
A_i_max = min(i + h // 2 + h % 2, N)

A_j_min = max(j - w // 2, 0)
A_j_max = min(j + w // 2 + w % 2, N)

# Compute corresponding slice for B
B_i_min = max(h // 2 - i, 0)
B_i_max = h - max(i + h // 2 + h % 2 - N, 0)

B_j_min = max(w // 2 - j, 0)
B_j_max = w - max(j + w // 2 + w % 2 - N, 0)

efficiency_map_cut = efficiency_map[B_i_min:B_i_max, B_j_min:B_j_max]  # B with it only, but cut to the valid region

for id_index, id in enumerate(ids):
    df_joined_filtered = df_joined[df_joined['id'] == id]  # the current polygon with it's intersected grids
    value_map_single_polygon = generate_flatten_value_map(df_joined, N=N)  # A with this polygon only
    value_map_single_polygon_cut = value_map_single_polygon[A_i_min:A_i_max, A_j_min:A_j_max]  # A with it only, but cut to the valid region
    contribution_id = np.sum(efficiency_map_cut * value_map_single_polygon_cut)  # their inner product
    relative_contributions[id_index] = contribution_id  # save the results


# %% generate heatmap:
convolution_for_plotting, extent_for_plotting = convolution_2d_fft(value_map, efficiency_map, LON_0, LAT_0, LON_1, LAT_1, delta_lon, delta_lat)
# convolve A with B:  # Classical convolution: (EXTREMELY SLOW!)
# from scipy.signal import convolve2d
# convolution_for_plotting = convolve2d(A, B, mode='same')

# %% Plot value map:
plt.imshow(np.flip(value_map.T, axis=0), interpolation='nearest')
plt.savefig(f'value_map.png')
plt.show()

# %% Plot efficiency map:
plt.imshow(efficiency_map, interpolation='nearest', vmin=0)
plt.show()

# %% Plot convolution:
plt.imshow(np.abs(convolution_for_plotting),
           interpolation='nearest',
           extent=extent_for_plotting)

plt.gca().set_aspect('auto', adjustable='box')
plt.gca().set_box_aspect(1)
plt.show()


# %% compare different resolutions:
# TL;DR it is meaningless to go below 50 meters of resolution (for the polygons of the size I chose).
import time
def compare_resolutions(N_LOG):
    N = 2 ** N_LOG
    RESOLUTION_METERS = 10 * 2 ** (11 - N_LOG)

    start_time = time.time()
    value_map, efficiency_map, delta_lon, delta_lat, LON_1, LAT_1 = generate_maps(N, RESOLUTION_METERS, LAT_0, LON_0,
                                                                                  DF_VALUES)
    convolution_for_plotting, extent_for_plotting = convolution_2d_fft(value_map, efficiency_map, LON_0, LAT_0, LON_1,
                                                                       LAT_1, delta_lon, delta_lat)
    end_time = time.time()

    computation_time = end_time - start_time

    plt.imshow(np.abs(convolution_for_plotting),
               interpolation='nearest',
               extent=extent_for_plotting)
    plt.gca().set_aspect('auto', adjustable='box')
    plt.gca().set_box_aspect(1)
    plt.title(
        f'resolution: {RESOLUTION_METERS} meters, number of grids: {N ** 2:.2e}\ncomputation time: {computation_time:.3f} seconds')
    # save the figure:
    plt.savefig(f'convolution_{N_LOG}.png')
    plt.show()


for i in range(4, 12):
    compare_resolutions(i)

# %%



# Example usage:
A = np.zeros((10, 10))
B = np.array([[1, 2, 1],
              [2, 4, 2],
              [1, 2, 1]])

add_within_bounds(A, B, i=0, j=0)  # Adding B centered at (1,1)
