import math
import pickle as pkl
import matplotlib.pyplot as plt
import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

import os
import time

from icecream import ic

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** configure matplotlib")
plt.rcParams.update({'font.size': 14})
list_colors = list(mcolors.TABLEAU_COLORS)
list_colors.append("w")
list_colors.append("k")

dict_bad_data = {
}

with open("./dict_all_data.pkl", "rb") as fh:
    dict_data_each_logger = pkl.load(fh)

list_instruments_with_thermistor = []
instruments_blacklist = []

for crrt_instrument in dict_data_each_logger.keys():
    if len(dict_data_each_logger[crrt_instrument]["thermistor"]) > 20 and crrt_instrument not in instruments_blacklist:
        print("instrument {} has at least a few spectrum data".format(crrt_instrument))
        list_instruments_with_thermistor.append(crrt_instrument)
        ic(dict_data_each_logger[crrt_instrument]["res_thermistor"])

date_start = datetime.datetime(2022,  3, 27, 0, 0, 0)
date_end   = datetime.datetime(2022,  4,  5,  0, 0, 0)

# the instrument was equipped with 3 thermistors
nbr_thermistors_to_plot = 3

plt.figure()

for ind, crrt_instrument in enumerate(list_instruments_with_thermistor):
    list_timestamps = []
    dict_thermistor_readings = {}
    for thermistor_idx in range(nbr_thermistors_to_plot):
        dict_thermistor_readings[thermistor_idx] = []

    for crrt_message in dict_data_each_logger[crrt_instrument]["res_thermistor"]:
        list_timestamps.append(crrt_message.datetime_packet)
        for thermistor_idx in range(nbr_thermistors_to_plot):
            dict_thermistor_readings[thermistor_idx].append(
                crrt_message.thermistors_readings[thermistor_idx].mean_temperature
            )

    for thermistor_idx in range(nbr_thermistors_to_plot):
        plt.plot(list_timestamps, dict_thermistor_readings[thermistor_idx],
                 label=f"instr {crrt_instrument} thermistor {thermistor_idx}")

plt.legend()
plt.xticks(rotation=30)
plt.ylabel("temp [deg C]")
plt.tight_layout()
plt.savefig("temperature_thermistors.png")
plt.savefig("temperature_thermistors.pdf")
plt.show()
