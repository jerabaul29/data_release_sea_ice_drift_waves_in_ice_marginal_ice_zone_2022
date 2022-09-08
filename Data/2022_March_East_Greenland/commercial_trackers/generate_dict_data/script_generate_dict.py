import time
import os

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

from icecream import ic

import datetime
import pytz

import pickle as pkl

import json

utc_timezone = pytz.timezone("UTC")

ic.configureOutput(prefix="", outputFunction=print)

# From ShadowDeployments.csv, taking a bit of margin, in UTC times
dict_start_times = {
    "T1": datetime.datetime(2022, 3, 21, 18, 30, 0, tzinfo=utc_timezone),
    "T2": datetime.datetime(2022, 3, 21, 17, 0, 0, tzinfo=utc_timezone),
    "T3": datetime.datetime(2022, 3, 22, 11, 0, 0, tzinfo=utc_timezone),
    "T4": datetime.datetime(2022, 3, 22, 16, 30, 0, tzinfo=utc_timezone),
    "T5": datetime.datetime(2022, 3, 22, 18, 0, 0, tzinfo=utc_timezone),
}

dict_all_data = {}

print("load all data in the json file...")

with open('./trusted.geojson', 'r') as f:
  data = json.load(f)

# ic(data.keys)
# ic(data["features"][0].keys())
# ic(data["features"][0]["properties"].keys())
# ic(data["features"][0]["geometry"].keys())

dict_all_data = {}
for crrt_instrument_id in dict_start_times:
    dict_all_data[crrt_instrument_id] = {}

for crrt_entry in data["features"]:
    # ic(crrt_entry)

    crrt_instrument_id = crrt_entry["properties"]["UnitName"]
    assert crrt_instrument_id in dict_start_times
    # ic(crrt_instrument_id)

    crrt_utc_timestamp = datetime.datetime.strptime(crrt_entry["properties"]["UTC"], "%Y-%m-%d %H:%M:%S")
    crrt_utc_timestamp = utc_timezone.localize(crrt_utc_timestamp)
    # ic(crrt_utc_timestamp)

    crrt_lat = float(crrt_entry["geometry"]["coordinates"][1])
    crrt_lon = float(crrt_entry["geometry"]["coordinates"][0])
    # ic(crrt_lat)
    # ic(crrt_lon)

    dict_all_data[crrt_instrument_id][crrt_utc_timestamp] = {}
    dict_all_data[crrt_instrument_id][crrt_utc_timestamp]["lat"] = crrt_lat
    dict_all_data[crrt_instrument_id][crrt_utc_timestamp]["lon"] = crrt_lon

print("dump")

# dump with pickle
with open("data_from_Martin_2022.pkl", "bw") as fh:
    pkl.dump(dict_all_data, fh)
