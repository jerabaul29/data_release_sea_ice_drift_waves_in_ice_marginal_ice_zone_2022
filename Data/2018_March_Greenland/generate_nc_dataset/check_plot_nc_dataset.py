"""
From the nc4 file:
- plot trajectories

Looking at these plots allows to double check the quality and content of the nc files.
This can also be used as an example for how to read and use the data.

All these scripts should be quite identical from deployment to deployment - convenient
as no need to "install" anything on your machine, but a bit of code duplication...

This specific version only shows the GPS track, as there was no wave measurements associated
with this specific instrument.
"""

from datetime import timedelta
from datetime import datetime

import os
import time

from icecream import ic

import netCDF4 as nc4

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

import math

import numpy as np

# ------------------------------------------------------------------------------------------
# copy by hand, see point above

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** configure matplotlib")
plt.rcParams.update({'font.size': 14})
list_colors = list(mcolors.TABLEAU_COLORS)
list_colors.append("k")
list_colors.append("w")

# ------------------------------------------------------------------------------------------
print("***** load the netcdf data file")

verbose_load = False

dict_extracted_data = {}

time_start = datetime.fromtimestamp(2e10)
time_end = datetime.fromtimestamp(0)

input_file = "./data_drift_2018_March_Greenland.nc"

with nc4.Dataset(input_file, "r", format="NETCDF4") as nc4_fh:
    number_of_trajectories = nc4_fh.dimensions["trajectory"].size
    if verbose_load:
        ic(number_of_trajectories)

    for ind_trajectory in range(number_of_trajectories):
        if verbose_load:
            print("** new instrument **")

        # get the instrument id
        crrt_instrument_id = ""
        array_chars = nc4_fh["trajectory_id"][ind_trajectory, :]
        for crrt_char in array_chars:
            if np.ma.is_masked(crrt_char):
                break
            crrt_instrument_id += crrt_char.decode('ascii')
        ic(crrt_instrument_id)

        # read the data content and organize it into
        # dicts {time: (spectrum, swh, hs, tp, tz0)} and {time: (lat, lon)}
        crrt_dict_time_pos = {}

        array_datetime = nc4_fh["time"][ind_trajectory, :].data
        array_lat = nc4_fh["lat"][ind_trajectory, :].data
        array_lon = nc4_fh["lon"][ind_trajectory, :].data

        for crrt_index, crrt_time in enumerate(array_datetime):
            if verbose_load:
                print("**")

            try:
                crrt_datetime = datetime.fromtimestamp(float(crrt_time))
            except Exception as e:
                # print(f"fromtimestamp on {float(crrt_time)} for entry {crrt_index} failed: {e}")
                pass

            if verbose_load:
                ic(crrt_datetime)

            if -90.0 <= float(array_lat[crrt_index]) and float(array_lat[crrt_index]) <= 90.0 and -180.0 <= array_lon[crrt_index] and array_lon[crrt_index] <= 360.0:
                pass
            else:
                # print(f"entry {crrt_index} with lat {array_lat[crrt_index]} and lon {array_lon[crrt_index]} seems invalid! ignore!")
                continue

            crrt_position = (float(array_lat[crrt_index]), float(array_lon[crrt_index]))
            if verbose_load:
                ic(crrt_position)
            crrt_dict_time_pos[crrt_datetime] = crrt_position

            time_end = max(time_end, crrt_datetime)
            time_start = min(time_start, crrt_datetime)

        dict_extracted_data[crrt_instrument_id] = {}
        dict_extracted_data[crrt_instrument_id]["time_pos"] = crrt_dict_time_pos

# ------------------------------------------------------------------------------------------
# order the instruments with "higher lat higher up" in the plots
list_keys = list(dict_extracted_data.keys())
list_lats = []
for crrt_key in list_keys:
    crrt_dict_time_pos = dict_extracted_data[crrt_key]["time_pos"]
    crrt_list_times = sorted(list(crrt_dict_time_pos.keys()))
    crrt_lat = dict_extracted_data[crrt_key]["time_pos"][crrt_list_times[1]][0]
    list_lats.append(crrt_lat)
list_keys_ordered_by_first_lat = [crrt_key for _, crrt_key in sorted(zip(list_lats, list_keys))]
list_keys_ordered_by_first_lat.reverse()

# ------------------------------------------------------------------------------------------
# plot the data for checking consistency
print("***** plot the data")

# ------------------------------------------------------------------------------------------
# plot the positions on a 2D plot (no map)
# we do not use cartopy or similar so that this runs fast
print("** plot positions on simple 2D plot")

plt.figure()

for crrt_index, crrt_instrument_id in enumerate(list_keys_ordered_by_first_lat):
    crrt_dict_time_pos = dict_extracted_data[crrt_instrument_id]["time_pos"]
    crrt_list_times = sorted(list(crrt_dict_time_pos.keys()))

    ic(crrt_instrument_id)
    ic(crrt_list_times[0])
    ic(crrt_list_times[-1])
    
    crrt_list_pos = [crrt_dict_time_pos[crrt_time] for crrt_time in crrt_list_times]
    crrt_list_lat = [crrt_pos[0] for crrt_pos in crrt_list_pos]
    crrt_list_lon = [crrt_pos[1] for crrt_pos in crrt_list_pos]
    plt.plot(crrt_list_lon, crrt_list_lat, label="{}".format(crrt_instrument_id), marker="*", color=list_colors[crrt_index])

plt.legend()

plt.xlabel("lon [DD]")
plt.ylabel("lat [DD]")
plt.tight_layout()
plt.savefig("trajectories.pdf")

# show all figures at the same time, to be able to compare...
plt.show()
