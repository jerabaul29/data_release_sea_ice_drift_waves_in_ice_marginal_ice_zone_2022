import pickle
import math
import numpy as np

from utils import butter_lowpass_filter, integrate_twice, compute_SWH, welch_spectrum, compute_wave_spectrum_moments, compute_spectral_properties

from icecream import ic

import datetime

from utils import find_list_pkl_files, PairPacket, plot_ug_vn_files_pair

import matplotlib.pyplot as plt
from script_create_boat_position_data import BoatPacket, plot_list_entries

import time
import os

from script_create_boat_position_data import parse_all_boat_files_in_folder

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
# parse the boat data
list_entries_boat_positions = parse_all_boat_files_in_folder("./../boat_data/")

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

# ------------------------------------------------------------------------------------------
# the list of selected segments with intersting data
print("***** List of selected segments with interesting data")


list_relevant_segment_indexes = [
    25,
    30,
    32,
    33,
    70,
    92,
]

list_hand_tuned_segments = [
    (datetime.datetime(2021, 2, 15, 17, 18), datetime.datetime(2021, 2, 15, 17, 31)),
    (datetime.datetime(2021, 2, 15, 22, 16), datetime.datetime(2021, 2, 15, 22, 31)),
    (datetime.datetime(2021, 2, 16, 12, 25), datetime.datetime(2021, 2, 16, 12, 35)),
    (datetime.datetime(2021, 2, 16, 12, 40), datetime.datetime(2021, 2, 16, 12, 55)),
    (datetime.datetime(2021, 2, 23, 10, 40), datetime.datetime(2021, 2, 23, 11, 20)),
    (datetime.datetime(2021, 2, 25, 10, 54), datetime.datetime(2021, 2, 25, 11, 3)),
]

# ------------------------------------------------------------------------------------------
# look at segments, each at a time
print("***** Look at individual segments of data")

if False:
    use_hand_tuned = True

    crrt_relevant_segment_number = 6

    # by looking at the previously generated segments
    if not use_hand_tuned:
        crrt_segment_number = list_relevant_segment_indexes[crrt_relevant_segment_number]
        crrt_segment = list_segments_boat_immobile[crrt_segment_number]
        first_datetime = crrt_segment[0].datetime_fix
        last_datetime = crrt_segment[-1].datetime_fix
    # done by hand tuning the segments
    else:
        crrt_segment = list_hand_tuned_segments[crrt_relevant_segment_number]
        first_datetime = crrt_segment[0]
        last_datetime = crrt_segment[-1]

    # start and end dates
    ic(first_datetime)
    ic(last_datetime)

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

# ------------------------------------------------------------------------------------------
# dump the segments, one at a time

dict_valid_results = {}

for crrt_datetimes_segment in list_hand_tuned_segments:
    print()
    dict_valid_results[crrt_datetimes_segment] = {}
    ic(crrt_datetimes_segment)
    datetime_start_segment = crrt_datetimes_segment[0]
    datetime_end_segment = crrt_datetimes_segment[1]
    ic(datetime_end_segment - datetime_start_segment)

    crrt_list_datetimes_common_time_base = []
    crrt_list_ug_readings_common_time_base = []
    crrt_list_vn100_accD_common_time_base = []
    crrt_list_vn100_twice_integrated_common_time_base = []
    crrt_list_water_elevation_common_time_base = []

    list_relevant_boat_positions = []
    for crrt_boat_position in list_entries_boat_positions:
        crrt_datetime = crrt_boat_position.datetime_fix
        if crrt_datetime > datetime_start_segment and crrt_datetime < datetime_end_segment:
            list_relevant_boat_positions.append(crrt_boat_position)

    for crrt_pair in list_file_pairs_data:
        crrt_pair_start = crrt_pair.datetime_start
        crrt_pair_end = crrt_pair.datetime_end

        # are there some relevant data in this pair?
        if (crrt_pair_start < datetime_end_segment and crrt_pair_start > datetime_start_segment) or \
                (crrt_pair_end < datetime_end_segment and crrt_pair_end > datetime_start_segment):
            with open(crrt_pair.path_vn100_file, "br") as fh:
                dict_in_vn = pickle.load(fh)

            with open(crrt_pair.path_ug_file, "br") as fh:
                dict_in_ug = pickle.load(fh)

            ug_time_base = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in dict_in_ug["interpolated_timestamps"]]
            vn_time_base = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in dict_in_vn["interpolated_timestamps"]]

            common_time_base_start = max(ug_time_base[0], vn_time_base[0])
            common_time_base_end = min(ug_time_base[-1], vn_time_base[-1])

            if common_time_base_start < datetime_start_segment:
                common_time_base_start = datetime_start_segment

            if common_time_base_end > datetime_end_segment:
                common_time_base_end = datetime_end_segment

            common_time_base_ug = []
            common_time_base_ug_signal = []

            for (crrt_time, crrt_ug) in zip(ug_time_base, dict_in_ug["interpolated_readings"]):
                if crrt_time < common_time_base_end and crrt_time > common_time_base_start:
                    common_time_base_ug.append(crrt_time)
                    common_time_base_ug_signal.append(crrt_ug)

            mean_ug = np.mean(common_time_base_ug_signal)
            common_time_base_ug_signal_raw = common_time_base_ug_signal
            common_time_base_ug_signal = []
            for crrt_val in common_time_base_ug_signal_raw:
                common_time_base_ug_signal.append(crrt_val-mean_ug)

            common_time_base_ug_signal_raw = common_time_base_ug_signal
            common_time_base_ug_signal = []
            last_valid = None
            for crrt_ug in common_time_base_ug_signal_raw:
                if crrt_ug < 0.25 and crrt_ug > -0.25:
                    common_time_base_ug_signal.append(crrt_ug)
                    last_valid = crrt_ug
                else:
                    common_time_base_ug_signal.append(last_valid)

            common_time_base_vn = []
            common_time_base_vn_signal = []

            for (crrt_time, crrt_vn) in zip(vn_time_base, dict_in_vn["interpolated_readings"][:, 5]):
                if crrt_time < common_time_base_end and crrt_time > common_time_base_start:
                    common_time_base_vn.append(crrt_time)
                    common_time_base_vn_signal.append(crrt_vn)

            assert(len(common_time_base_ug) == len(common_time_base_vn))
            for (crrt_time_ug, crrt_time_vn) in zip(common_time_base_ug, common_time_base_vn):
                assert (crrt_time_ug - crrt_time_vn).total_seconds() * 1000 < 50

            common_time_base = common_time_base_ug
            common_time_ug_signal = np.array(common_time_base_ug_signal).squeeze()
            common_time_vn_signal = np.array(common_time_base_vn_signal).squeeze()
            common_time_vn_elevation = integrate_twice(common_time_vn_signal)
            common_time_water_elevation = -common_time_vn_elevation + common_time_ug_signal
            common_time_water_elevation_filtered = butter_lowpass_filter(common_time_water_elevation, cutoff=0.5, fs=10.0, order=8)

            if False:
                plt.figure()
                plt.plot(common_time_base, common_time_ug_signal, label="ug signal")
                plt.plot(common_time_base, common_time_vn_elevation, label="vn twice integrated elevation")
                plt.plot(common_time_base, common_time_water_elevation, label="water elevation")
                plt.plot(common_time_base, common_time_water_elevation_filtered, label="water elevation filtered")
                plt.legend()
                plt.show()

            crrt_list_datetimes_common_time_base += common_time_base
            crrt_list_ug_readings_common_time_base += list(common_time_ug_signal)
            crrt_list_vn100_accD_common_time_base += list(common_time_vn_signal)
            crrt_list_water_elevation_common_time_base += list(common_time_water_elevation_filtered)
            crrt_list_vn100_twice_integrated_common_time_base += list(common_time_vn_elevation)

    if True:
        plt.figure()
        plt.plot(crrt_list_datetimes_common_time_base, crrt_list_ug_readings_common_time_base, label="ug readings")
        plt.plot(crrt_list_datetimes_common_time_base, crrt_list_vn100_twice_integrated_common_time_base, label="vn100 twice integrated")
        plt.plot(crrt_list_datetimes_common_time_base, crrt_list_water_elevation_common_time_base, label="water elevation filtered")
        plt.legend()
        plt.show()

    dict_valid_results[crrt_datetimes_segment]["common_time_base"] = crrt_list_datetimes_common_time_base
    dict_valid_results[crrt_datetimes_segment]["ug_readings"] = crrt_list_ug_readings_common_time_base
    dict_valid_results[crrt_datetimes_segment]["vn100_twice_integrated"] = crrt_list_vn100_twice_integrated_common_time_base
    dict_valid_results[crrt_datetimes_segment]["water_elevation"] = crrt_list_water_elevation_common_time_base
    dict_valid_results[crrt_datetimes_segment]["boat_positions"] = list_relevant_boat_positions

    ic(len(crrt_list_datetimes_common_time_base))

    ic(list_relevant_boat_positions[0])
    ic(list_relevant_boat_positions[-1])

    SWH = compute_SWH(crrt_list_water_elevation_common_time_base)
    ic(SWH)

    f, Pxx_den = welch_spectrum(crrt_list_water_elevation_common_time_base, segment_duration_seconds=200, plot=True, smooth=False)

    M0, M1, M2, M3, M4, MM1, MM2 = compute_wave_spectrum_moments(Pxx_den, f)
    Hs, T_z, T_c, T_p = compute_spectral_properties(M0, M2, M4, Pxx_den, f)

    ic(Hs)
    ic(T_z)
    ic(T_p)

    dict_valid_results[crrt_datetimes_segment]["SWH"] = SWH
    dict_valid_results[crrt_datetimes_segment]["Hs"] = Hs
    dict_valid_results[crrt_datetimes_segment]["Tz"] = T_z
    dict_valid_results[crrt_datetimes_segment]["Tp"] = T_p

with open("./dict_valid_results.pkl", "bw") as fh:
    pickle.dump(dict_valid_results, fh)
