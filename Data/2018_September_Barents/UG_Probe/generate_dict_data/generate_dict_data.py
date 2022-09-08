import time
import os

from icecream import ic

import datetime

import pickle
from pathlib import Path

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
# list of lat lons from the IMU_information file
list_time_lat_lon = {
    "2018-09-19-04_22_21": (82.126, 20.736),
    "2018-09-19-06_28_11": (82.246, 20.245),
    "2018-09-19-08_59_11": (82.355, 19.803),
    "2018-09-19-12_20_31": (82.436, 19.674),
    "2018-09-19-13_11_24": (82.421, 19.579),
    "2018-09-19-14_32_30": (82.359, 19.544),
    "2018-09-19-15_40_26": (82.294, 19.389),
    "2018-09-19-16_54_39": (82.228, 19.275),
    "2018-09-19-18_00_03": (82.163, 19.183),
    "2018-09-19-19_08_30": (82.099, 19.046),
}


# ------------------------------------------------------------------------------------------
# do the work

# list of pickle files to extra data from
data_in_path = Path("/home/jrmet/Desktop/Data/drive-download-20211008T132811Z-001")
list_pkl_files = sorted(list(data_in_path.glob("2018-09-19-*.pkl")))
ic(list_pkl_files)

# dict for putting all the data acquired
dict_all_data = {}

for crrt_pickle_file in list_pkl_files:
    ic(crrt_pickle_file)
    with open(crrt_pickle_file, "br") as fh:
        crrt_pkl_data = pickle.load(fh)

    crrt_timestamp = crrt_pickle_file.name[0:19]
    crrt_datetime = datetime.datetime.strptime(crrt_timestamp, "%Y-%m-%d-%H_%M_%S")
    ic(crrt_datetime)

    dict_all_data[crrt_datetime] = {}

    dict_all_data[crrt_datetime]["hs"] = crrt_pkl_data["Hs"]
    crrt_swh = crrt_pkl_data["SWH"]
    # in the ice, problem with SWH, due to ice blocks coming in and out of under the boat
    if abs(crrt_swh - crrt_pkl_data["Hs"]) / crrt_swh > 0.20:
        # invalid swh computation
        dict_all_data[crrt_datetime]["swh"] = 1e20
    else:
        dict_all_data[crrt_datetime]["swh"] = crrt_swh

    # in the ice, problem with tm, due to parasitic boat motion that is hard to correct and ice coming in and out
    # NOTE: different nomenclature between the CRST manuscript and this data release manuscript
    dict_all_data[crrt_datetime]["tm"] = crrt_pkl_data["Tm01"]
    if abs(crrt_pkl_data["Tm01"] - crrt_pkl_data["Tm02"]) / crrt_pkl_data["Tm01"] > 0.25:
        dict_all_data[crrt_datetime]["tp"] = 1e20
    else:
        dict_all_data[crrt_datetime]["tp"] = crrt_pkl_data["Tm02"]

    if crrt_timestamp in list_time_lat_lon:
        pass
    else:
        raise RuntimeError("cannot find timestamp {} in the lat lon information file".format(crrt_timestamp))
    dict_all_data[crrt_datetime]["lat"] = list_time_lat_lon[crrt_timestamp][0]
    dict_all_data[crrt_datetime]["lon"] = list_time_lat_lon[crrt_timestamp][1]

    ic(crrt_timestamp)
    ic(dict_all_data[crrt_datetime]["lat"])
    ic(dict_all_data[crrt_datetime]["lon"])

    ic(crrt_pkl_data["Hs"])
    ic(crrt_pkl_data["SWH"])
    ic(crrt_pkl_data["T_p"])
    ic(crrt_pkl_data["Tm01"])
    ic(crrt_pkl_data["Tm02"])

    #ic(dict_all_data[crrt_datetime]["tp"])
    #ic(dict_all_data[crrt_datetime]["tm"])

    #ic(dict_all_data[crrt_datetime]["swh"])
    #ic(dict_all_data[crrt_datetime]["hs"])

    print()

pkl_out = Path("./dict_pkl_data.pkl")
with open(pkl_out, "bw") as fh:
    pickle.dump(dict_all_data, fh)
