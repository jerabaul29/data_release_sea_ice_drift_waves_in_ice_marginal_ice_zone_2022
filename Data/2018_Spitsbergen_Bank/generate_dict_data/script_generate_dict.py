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

utc_timezone = pytz.timezone("UTC")

ic.configureOutput(prefix="", outputFunction=print)

# ------------------------------------------------------------------------------------------

input_file = "raw_data_sigma2_archive.csv"
ic(input_file)

dict_all_data = {}

with open(input_file, "r") as fh:
    for crrt_line in fh:
        line_splitted = crrt_line.split(",")
        if not len(line_splitted) > 10:
            # ignore leak no data lines
            continue
        if not (line_splitted[6] == "la" and line_splitted[7] == "" and line_splitted[9] == "long"):
            # if a data line has wrong format, raise error
            raise RuntimeError(f"got invalid line: {crrt_line}")
        try:
            if line_splitted[8] == "None":
                continue  # ignore missing GPS fix
            if line_splitted[10] == "":
                year   = int(line_splitted[0])
                month  = int(line_splitted[1])
                day    = int(line_splitted[2])
                hour   = int(line_splitted[3])
                minute = int(line_splitted[4])
                second = int(line_splitted[5])
                lat    = float(line_splitted[8])
                lon    = float(line_splitted[11])
            else:
                year   = int(line_splitted[0])
                month  = int(line_splitted[1])
                day    = int(line_splitted[2])
                hour   = int(line_splitted[3])
                minute = int(line_splitted[4])
                second = int(line_splitted[5])
                lat    = float(line_splitted[8])
                lon    = float(line_splitted[10])
        except:
            print(f"error with line {crrt_line}, ignore it")

        timestamp = datetime.datetime(year, month, day, hour, minute, second, tzinfo=utc_timezone)
        dict_all_data[timestamp] = {}
        dict_all_data[timestamp]["lat"] = lat
        dict_all_data[timestamp]["lon"] = lon

for crrt_entry in dict_all_data:
    print(f"{crrt_entry}: {dict_all_data[crrt_entry]['lat']} - {dict_all_data[crrt_entry]['lon']}")

print("dump")

# dump with pickle
with open("data_from_drifter_Aleksey.pkl", "bw") as fh:
    pkl.dump(dict_all_data, fh)

