from datetime import datetime

import os
import time

import math
import numpy as np

from icecream import ic

import netCDF4 as nc4

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

# from create_nc_dataset import list_instruments_use_spectra  # problem with this is that the whole file gets executed...

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
# load the nc data


def filter_invalid(value_in):
    if value_in > 1e10:
        return 0
    else:
        return value_in


input_file = "./data_boat_wave_ultrasound_probes_Barents_2018.nc"

with nc4.Dataset(input_file, "r", format="NETCDF4") as nc4_fh:
    number_of_segments = nc4_fh.dimensions["measurement_segment"].size

    # show positions
    plt.figure()
    for crrt_segment in range(number_of_segments):
        crrt_color = list_colors[crrt_segment]

        lon_start_segment = float(nc4_fh["lon_start_segment"][crrt_segment].data)
        lat_start_segment = float(nc4_fh["lat_start_segment"][crrt_segment].data)
        time_start_segment = datetime.fromtimestamp(float(nc4_fh["time_start_segment"][crrt_segment].data))

        lon_end_segment = float(nc4_fh["lon_end_segment"][crrt_segment].data)
        lat_end_segment = float(nc4_fh["lat_end_segment"][crrt_segment].data)
        time_end_segment = datetime.fromtimestamp(float(nc4_fh["time_end_segment"][crrt_segment].data))

        plt.scatter(lon_start_segment, lat_start_segment, color=crrt_color, label=time_start_segment)
        plt.scatter(lon_end_segment, lat_end_segment, color=crrt_color)

    plt.xlabel("lon")
    plt.ylabel("lat")
    plt.legend()
    plt.tight_layout()
    plt.savefig("positions.png")

    # show wave statistics
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    for crrt_segment in range(number_of_segments):
        crrt_color = list_colors[crrt_segment]

        time_start_segment = datetime.fromtimestamp(float(nc4_fh["time_start_segment"][crrt_segment].data))
        swh = filter_invalid(float(nc4_fh["swh"][crrt_segment].data))
        hs = filter_invalid(float(nc4_fh["hs"][crrt_segment].data))
        tp = filter_invalid(float(nc4_fh["tp"][crrt_segment].data))
        tm = filter_invalid(float(nc4_fh["tm"][crrt_segment].data))

        if crrt_segment == number_of_segments-1:
            ax1.scatter(time_start_segment, swh, color=crrt_color, label="swh", marker="+")
            ax1.scatter(time_start_segment, hs, color=crrt_color, label="hs", marker="o")

            ax1.set_xticks([])
            ax1.set_ylabel("SWH (m)")
            ax1.legend()

            ax2.scatter(time_start_segment, tp, color=crrt_color, label="tp", marker="+")
            ax2.scatter(time_start_segment, tm, color=crrt_color, label="tm", marker="o")

            ax2.set_xticklabels(ax2.get_xticks(), rotation=30)
            formatter = mdates.DateFormatter("%Y-%m-%d")
            ax2.xaxis.set_major_formatter(formatter)
            ax2.set_ylabel("WP (s)")
            ax2.legend()

        else:
            ax1.scatter(time_start_segment, swh, color=crrt_color, marker="+")
            ax1.scatter(time_start_segment, hs, color=crrt_color, marker="o")

            ax2.scatter(time_start_segment, tp, color=crrt_color, marker="+")
            ax2.scatter(time_start_segment, tm, color=crrt_color, marker="o")

    plt.tight_layout()
    plt.savefig("wave_statistics.png")

plt.show()
