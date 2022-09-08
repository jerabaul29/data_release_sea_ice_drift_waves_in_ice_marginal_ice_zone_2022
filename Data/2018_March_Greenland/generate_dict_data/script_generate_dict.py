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

# From DeploymentMetadata.csv, taking a bit of margin, in UTC times
dict_start_times = {
    "sh1.txt": datetime.datetime(2018, 3, 21, 18, 30, 0, tzinfo=utc_timezone),
    "sh2.txt": datetime.datetime(2018, 3, 20, 15, 0, 0, tzinfo=utc_timezone),
    "sh3.txt": datetime.datetime(2018, 3, 22, 12, 0, 0, tzinfo=utc_timezone),
    "sh4.txt": datetime.datetime(2018, 3, 23, 17, 30, 0, tzinfo=utc_timezone),
    "sh5.txt": datetime.datetime(2018, 3, 21, 14, 0, 0, tzinfo=utc_timezone),
}

dict_all_data = {}

print("load all shX.txt files...")

for crrt_instrument in dict_start_times:
    ic(crrt_instrument)
    crrt_start_time_utc = dict_start_times[crrt_instrument]
    ic(crrt_start_time_utc)

    crrt_instrument_id = crrt_instrument[2]
    ic(crrt_instrument_id)

    dict_all_data[crrt_instrument_id] = {}

    crrt_datetime_previous = crrt_start_time_utc
    has_started = False

    previous_line = None

    with open(crrt_instrument, "r") as fh:
        for crrt_line in reversed(list(fh)):
            crrt_line = crrt_line.replace("\t", " ")
            crrt_line = crrt_line.replace("\n", " ")
            crrt_line = crrt_line.replace("\r", " ")
            crrt_line = crrt_line.replace(",", " ")

            if len(crrt_line) < 32:
                continue

            if crrt_line == previous_line:
                continue
            else:
                previous_line = crrt_line

            assert crrt_line[-13:] == "Altitude: -  "

            line_parts = crrt_line.split()
            assert len(line_parts) == 7

            ymd = line_parts[0].split("/")
            crrt_year_ = int(ymd[0])
            crrt_month = int(ymd[1])
            crrt_day__ = int(ymd[2])

            hms = line_parts[1].split(":")
            crrt_h = int(hms[0])
            crrt_m = int(hms[1])
            crrt_s = int(hms[2])

            crrt_datetime = datetime.datetime(
                crrt_year_, crrt_month, crrt_day__,
                crrt_h, crrt_m, crrt_s,
                tzinfo=utc_timezone
            )

            if not has_started:
                if crrt_datetime > crrt_start_time_utc:
                    has_started = True
                else:
                    continue

            assert crrt_datetime > crrt_datetime_previous
            crrt_datetime_previous = crrt_datetime

            crrt_lat = float(line_parts[2])
            crrt_lon = float(line_parts[3])

            dict_all_data[crrt_instrument_id][crrt_datetime] = {}
            dict_all_data[crrt_instrument_id][crrt_datetime]["lat"] = crrt_lat
            dict_all_data[crrt_instrument_id][crrt_datetime]["lon"] = crrt_lon

print("dump")

# dump with pickle
with open("data_from_Martin_2018.pkl", "bw") as fh:
    pkl.dump(dict_all_data, fh)
