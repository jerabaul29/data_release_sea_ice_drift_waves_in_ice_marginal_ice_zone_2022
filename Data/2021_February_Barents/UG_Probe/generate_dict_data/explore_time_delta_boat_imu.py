import pickle

import icecream

from script_create_boat_position_data import BoatPacket, plot_list_entries

from icecream import ic

from utils import find_list_pkl_files, PairPacket, plot_ug_vn_files_pair

import matplotlib.pyplot as plt

from dataclasses import dataclass

import datetime

from params import datetime_start_ice, datetime_end_ice

import time
import os


# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** Load immobile boat segments")
file_segments_boat = "./list_segments_immobile.pkl"
with open(file_segments_boat, "br") as fh:
    list_segments_boat_immobile = pickle.load(fh)

# ------------------------------------------------------------------------------------------
print("***** Create list of ordered (start, end) timestamps for gauge data files")
folder_pkl = "/home/jrmet/Desktop/Data/bow_sensor/on_time_base/"
list_file_pairs = find_list_pkl_files(folder_pkl)
list_file_pairs_data = []

for crrt_file_pair in list_file_pairs:
    with open(crrt_file_pair[0], "br") as fh:
        dict_data = pickle.load(fh)
    crrt_pair = PairPacket(
        path_ug_file=crrt_file_pair[0],
        path_vn100_file=crrt_file_pair[1],
        datetime_start=datetime.datetime.fromtimestamp(dict_data["interpolated_timestamps"][0]),
        datetime_end=datetime.datetime.fromtimestamp(dict_data["interpolated_timestamps"][-1]),
    )
    list_file_pairs_data.append(crrt_pair)

number_immobile_segments = len(list_segments_boat_immobile)
ic(number_immobile_segments)


# ------------------------------------------------------------------------------------------
# no need to redo this each time
if False:
    print("***** Look at a single segment to find out if (and what) time shift value boat vs gauges")
    print("***** consider these segments only if they are fully in the ice")

    # use a segment when the boat is immobile
    segment_number = 51  # good example
    segment_number = 93  # good example
    crrt_segment = list_segments_boat_immobile[segment_number]

    # start and end dates
    first_datetime = crrt_segment[0].datetime_fix
    last_datetime = crrt_segment[-1].datetime_fix
    ic(first_datetime)
    ic(last_datetime)

    # show how the motion looks like
    plot_list_entries(crrt_segment, plot_immobile=False)

    # find which ug system segments have overlap
    list_relevant_data_pairs = []

    for crrt_pair in list_file_pairs_data:
        crrt_pair_start = crrt_pair.datetime_start
        crrt_pair_end = crrt_pair.datetime_end

        if (crrt_pair_start < last_datetime and crrt_pair_start > first_datetime) or \
                (crrt_pair_end < last_datetime and crrt_pair_end > first_datetime):
            list_relevant_data_pairs.append(crrt_pair)

    ic(list_relevant_data_pairs)

    if len(list_relevant_data_pairs) > 0:

        # actually, take a bit before and after
        index_start = list_file_pairs_data.index(list_relevant_data_pairs[0])
        index_end = list_file_pairs_data.index(list_relevant_data_pairs[-1])

        list_extended_relevant_data_pairs = []
        for crrt_index in range(index_start-3, index_end+3):
            list_extended_relevant_data_pairs.append(list_file_pairs_data[crrt_index])

        list_relevant_data_pairs = list_extended_relevant_data_pairs

        plt.figure()
        for crrt_pair in list_relevant_data_pairs[:-1]:
            try:
                plot_ug_vn_files_pair(crrt_pair)
            except Exception as e:
                print("failed to plot with exception: {}".format(e))
        try:
            plot_ug_vn_files_pair(list_relevant_data_pairs[-1], label=True, renormalize=False)
        except Exception as e:
            print("failed to plot with exception: {}".format(e))

        plt.axvline(x=first_datetime, color='k', linestyle='--')
        plt.axvline(x=last_datetime, color='k', linestyle='--')

        plt.legend()
        plt.show()

    # this confirms that the time is the same (UTC) for both the GPS and the UG data :) .
    print("OK, both probe and the UG are in UTC")

# ------------------------------------------------------------------------------------------
print("***** look at all segments to find promising ones")

# no need to re do this each time
if False:
    for segment_number in range(10, number_immobile_segments):
        print()
        print("*** LOOK AT SEGMENT NUMBER:")
        ic(segment_number)
        # use a segment when the boat is immobile
        # segment_number = 89
        crrt_segment = list_segments_boat_immobile[segment_number]

        # start and end dates
        first_datetime = crrt_segment[0].datetime_fix
        last_datetime = crrt_segment[-1].datetime_fix
        ic(first_datetime)
        ic(last_datetime)

        # if first_datetime < datetime_start_ice or last_datetime > datetime_end_ice:
        #     print("outside of ice time, do not consider this segment")
        #     continue

        # show how the motion looks like
        # plot_list_entries(crrt_segment, plot_immobile=False)

        # find which ug system segments have overlap
        list_relevant_data_pairs = []

        for crrt_pair in list_file_pairs_data:
            crrt_pair_start = crrt_pair.datetime_start
            crrt_pair_end = crrt_pair.datetime_end

            if (crrt_pair_start < last_datetime and crrt_pair_start > first_datetime) or \
                    (crrt_pair_end < last_datetime and crrt_pair_end > first_datetime):
                list_relevant_data_pairs.append(crrt_pair)

        ic(list_relevant_data_pairs)

        if len(list_relevant_data_pairs) > 0:

            # actually, take a bit before and after
            index_start = list_file_pairs_data.index(list_relevant_data_pairs[0])
            index_end = list_file_pairs_data.index(list_relevant_data_pairs[-1])

            list_extended_relevant_data_pairs = []
            for crrt_index in range(index_start-2, index_end+2):
                list_extended_relevant_data_pairs.append(list_file_pairs_data[crrt_index])

            list_relevant_data_pairs = list_extended_relevant_data_pairs

            plt.figure()
            for crrt_pair in list_relevant_data_pairs[:-1]:
                try:
                    plot_ug_vn_files_pair(crrt_pair, renormalize=True)
                except Exception as e:
                    print("failed to plot with exception: {}".format(e))
            try:
                plot_ug_vn_files_pair(list_relevant_data_pairs[-1], True)
            except Exception as e:
                print("failed to plot with exception: {}".format(e))

            plt.axvline(x=first_datetime, color='k', linestyle='--')
            plt.axvline(x=last_datetime, color='k', linestyle='--')

            plt.legend()
            plt.show()

list_relevant_segment_indexes = [
    18,
    19,
    20,
    25,
    30,
    31,
    32,
    33,
    70,
    92,
    93
]

print()
print("***")
print("list of relevant segments:")

list_relevant_segments = []

for crrt_segment_index in list_relevant_segment_indexes:
    crrt_segment = list_segments_boat_immobile[crrt_segment_index]
    list_relevant_segments.append(crrt_segment)
    print("segment start - end: {} - {}".format(crrt_segment[0].datetime_fix, crrt_segment[-1].datetime_fix))

with open("list_relevant_segments.pkl", "bw") as fh:
    pickle.dump(list_relevant_segments, fh)
