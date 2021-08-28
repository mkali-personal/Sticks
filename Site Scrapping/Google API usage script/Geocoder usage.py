import pandas as pd
import geocoder as gc

# Set your input file here
input_filename = "data/Addresses input.csv"
# Specify the column name in your input data that contains addresses here
address_column_name = "Address"

data = pd.read_csv(input_filename, encoding='utf8')
addresses = (data[address_column_name] + ',' + ' ירושלים, ישראל').tolist()

l = []

# for a in addresses:
#     p = gc.google(a)
#     l.append(p.geojson)
#     print(p.response)

example_

