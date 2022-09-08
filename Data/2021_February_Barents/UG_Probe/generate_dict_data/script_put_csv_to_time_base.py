"""
NOTES:
- a bit of hack on the common time base... But that should be ok
- Yaw, Pitch, Roll are in degrees
- Yaw, Pitch, Roll are in degrees
- the IMU data used in the following have columns (yaw, pitch, roll, accelNorth, accelEast, accelDown)
"""

import datetime
import pytz

import time
import os

from operator import itemgetter

import math
import numpy as np

import tqdm

import pickle

import matplotlib.pyplot as plt

# make sure we use UTC in all our work
os.environ["TZ"] = "UTC"
time.tzset()


def get_timestamp_end(file_in):
    with open(file_in, "r") as fh:
        for crrt_line in fh:
            pass

    print("last line: {}".format(crrt_line))
    timestamp = crrt_line[17:43]
    print("timestamp: {}".format(timestamp))
    datetime_end = datetime.datetime.strptime(timestamp, "%Y-%m-%d-%H:%M:%S.%f")
    datetime_end = pytz.utc.localize(datetime_end)

    print("datetime: {}".format(datetime_end))

    return datetime_end


def timestamp_data(datetime_end, data, list_of_columns, sampling_timedelta):
    list_datetimes = []
    list_data = []

    crrt_datetime = datetime_end

    for crrt_data in reversed(data):
        crrt_extracted_data = itemgetter(*list_of_columns)(crrt_data)
        list_data.append(crrt_extracted_data)
        list_datetimes.append(crrt_datetime)
        crrt_datetime -= sampling_timedelta

    list_data = list(reversed(list_data))
    list_datetimes = list(reversed(list_datetimes))

    print("done putting timestamps on all entries")
    print("first entry: {}: {}".format(list_datetimes[0], list_data[0]))
    print("last entry: {}: {}".format(list_datetimes[-1], list_data[-1]))

    return (list_datetimes, list_data)


def put_data_on_sampled_base(list_datetimes, list_data, time_resolution=datetime.timedelta(milliseconds=100)):
    # from now on, think in terms of UNIX timestamps
    list_timestamps = [crrt_datetime.timestamp() for crrt_datetime in list_datetimes]
    array_timestamps = np.array(list_timestamps)

    array_data = np.array(list_data)

    # interpolate each of the "channels"
    if len(array_data.shape) == 1:
        number_of_channels = 1
        array_data = np.expand_dims(array_data, 1)
    elif len(array_data.shape) == 2:
        number_of_channels = array_data.shape[1]
    else:
        raise RuntimeError("data in must have rank 1 or 2")
    print("number_of_channels: {}".format(number_of_channels))

    # build the time base on which to interpolate
    min_time = math.floor(list_timestamps[0]) + 1
    max_time = math.floor(list_timestamps[-1]) - 1
    interpolation_resolution = time_resolution.total_seconds()

    array_interpolated_timestamps = np.arange(min_time, max_time, interpolation_resolution)
    number_of_interpolated_timestamps = array_interpolated_timestamps.shape[0]
    print("number_of_interpolated_timestamps: {}".format(number_of_interpolated_timestamps))

    # the array of output
    array_interpolated_data = np.zeros((number_of_interpolated_timestamps, number_of_channels))

    for crrt_channel in range(number_of_channels):
        crrt_interpolated_data = np.interp(
            array_interpolated_timestamps,
            array_timestamps,
            array_data[:, crrt_channel]
        )

        array_interpolated_data[:, crrt_channel] = crrt_interpolated_data

    return (array_interpolated_timestamps, array_interpolated_data)


def read_VN100_file(file_in):
    assert file_in[-9:] == "VN100.csv", "{} is not a VN100 file".format(file_in)

    COLUMNS_DATA_IMU = [11, 12, 13, 26, 27, 28]  # yaw pitch roll, accelNorth, accelEast, accelDown
    SAMPLING_TIMEDELTA_IMU = datetime.timedelta(milliseconds=100)

    data = np.genfromtxt(fname=file_in,
                         skip_header=2, skip_footer=1, delimiter=" ")
    datetime_end = get_timestamp_end(file_in)

    list_datetimes, list_readings = timestamp_data(
        datetime_end, data,
        COLUMNS_DATA_IMU, SAMPLING_TIMEDELTA_IMU
    )

    return (list_datetimes, list_readings)


def read_UG_file(file_in):
    print("look at UG {}".format(file_in))
    assert file_in[-9:] == "gauge.csv", "{} is not a gauge file".format(file_in)

    COLUMNS_DATA_UG = [3]
    SAMPLING_TIMEDELTA_UG = datetime.timedelta(milliseconds=20)

    data = np.genfromtxt(fname=file_in,
                         skip_header=2, skip_footer=1, delimiter=" ")
    datetime_end = get_timestamp_end(file_in)

    list_datetimes, list_readings = timestamp_data(
        datetime_end, data,
        COLUMNS_DATA_UG, SAMPLING_TIMEDELTA_UG
    )

    # scale; this is self-teaching, 1m window centered on the taught position
    list_readings = [(crrt_data - 512.0) * 1.0 / 1024.0 for crrt_data in list_readings]

    return (list_datetimes, list_readings)


def find_out_file_kind(file_in):
    if file_in[-9:] == "gauge.csv":
        return "GAUGE"
    elif file_in[-9:] == "VN100.csv":
        return "VN100"
    else:
        raise RuntimeError("unknown file kind: {}".format(file_in))


# ------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # process a whole folder
    folder_in = "/home/jrmet/Desktop/Data/bow_sensor/UGauge/"
    folder_out = "/home/jrmet/Desktop/Data/bow_sensor/on_time_base/"
    log_error = "./errors_put_csv_to_time_base.log"

    if True:
        list_all_files = os.listdir(folder_in)

        print("process all files in {}".format(folder_in))

        list_messages_error = []

        for crrt_file in tqdm.tqdm(list_all_files):
            print("")
            try:
                crrt_file_in = folder_in + crrt_file
                crrt_file_out = folder_out + crrt_file[:-4] + ".pkl"
                print("look at {}, write in {}".format(crrt_file_in, crrt_file_out))

                kind = find_out_file_kind(crrt_file_in)

                if kind == "GAUGE":
                    list_datetimes, list_readings = read_UG_file(crrt_file_in)
                elif kind == "VN100":
                    list_datetimes, list_readings = read_VN100_file(crrt_file_in)
                else:
                    raise RuntimeError("invalid kind")

                interpolated_timestamps, interpolated_readings = put_data_on_sampled_base(
                    list_datetimes, list_readings
                )

                dict_file_data = {}
                dict_file_data["interpolated_timestamps"] = interpolated_timestamps
                dict_file_data["interpolated_readings"] = interpolated_readings

                with open(crrt_file_out, "wb") as fh:
                    pickle.dump(dict_file_data, fh)

            except Exception as e:
                list_messages_error.append("------------------------------\n")
                list_messages_error.append("in: {}, out: {}\n".format(crrt_file_in, crrt_file_out))
                list_messages_error.append(str(e))
                list_messages_error.append("\n")

        with open(log_error, "w") as fh:
            for message in list_messages_error:
                fh.write(message)

    # ------------------------------------------------------------------------------------------
    # look at some examples
    if False:
        list_datetimes, list_readings = read_UG_file("2021-02-22-12:20:43_gauge.csv")
        interpolated_timestamps, interpolated_readings = put_data_on_sampled_base(
            list_datetimes, list_readings
        )

        if False:
            print(list_datetimes[:5])
            print(list_readings[:5])
            print(list_datetimes[300:330])
            print(list_readings[300:330])
            print(list_datetimes[-5:])
            print(list_readings[-5:])

        if True:
            interpolated_datetimes = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in list(interpolated_timestamps)]
            plt.figure()
            plt.plot(interpolated_datetimes, interpolated_readings, label="interpolated")
            plt.plot(list_datetimes, list_readings, label="raw")
            plt.legend()
            plt.show()


        print("")

        list_datetimes, list_readings = read_VN100_file("2021-02-22-12:20:43_VN100.csv")
        interpolated_timestamps, interpolated_readings = put_data_on_sampled_base(
            list_datetimes, list_readings
        )

        if False:
            print(list_datetimes[:5])
            print(list_readings[:5])
            print(list_datetimes[300:330])
            print(list_readings[300:330])
            print(list_datetimes[-5:])
            print(list_readings[-5:])

        if True:
            interpolated_datetimes = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in list(interpolated_timestamps)]
            plt.figure()
            plt.plot(interpolated_datetimes, interpolated_readings, label="interpolated")
            plt.plot(list_datetimes, list_readings, label="raw")
            plt.legend()
            plt.show()


