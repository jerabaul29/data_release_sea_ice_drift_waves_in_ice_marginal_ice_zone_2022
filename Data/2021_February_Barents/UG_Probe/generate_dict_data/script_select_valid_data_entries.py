import pickle as pkl
import datetime

import math

import readchar

import numpy as np
import matplotlib.pyplot as plt

from scipy import integrate
from scipy import signal

import os
import time

os.environ["TZ"] = "UTC"
time.tzset()

PERFORM_KET_PLOTS = False

# ------------------------------------------------------------------------------------------
# reminder from script_put_csv_to_time_base.py:
# the order of the VN100 fields for each entry is:
# yaw pitch roll, accelNorth, accelEast, accelDown

# note about the orientation of the IMU on the boat
# the X direction was pointing to the left
# the Y direction was pointing forward
# the Z direction was pointing downwards


def find_out_file_kind(file_in):
    if file_in[-9:] == "gauge.pkl":
        return "GAUGE"
    elif file_in[-9:] == "VN100.pkl":
        return "VN100"
    elif file_in[-9:] == "stats.pkl":
        return "STATS"
    else:
        raise RuntimeError("unknown file kind: {}".format(file_in))


def integrate_twice(data_in):
    '''integrate twice using fft and ifft'''

    # calculate fft, filter, and then ifft to get heights
    SAMPLING_FRQ = 10.0
    ACC_SIZE = data_in.shape[0]

    # suppress divide by 0 warning
    np.seterr(divide='ignore')

    Y = np.fft.fft(data_in)

    # calculate weights before applying ifft
    freq = np.fft.fftfreq(ACC_SIZE, d=1.0 / SAMPLING_FRQ)
    weights = -1.0 / ((2 * np.pi * freq)**2)
    # need to do some filtering for low frequency (from Kohout)
    f1 = 0.03
    f2 = 0.04
    Yf = np.zeros_like(Y)
    ind = np.argwhere(np.logical_and(freq >= f1, freq <= f2))
    Yf[ind] = Y[ind] * 0.5 * (1 - np.cos(np.pi * (freq[ind] - f1) / (f2 - f1))) * weights[ind]
    Yf[freq > f2] = Y[freq > f2] * weights[freq > f2]

    # apply ifft to get height
    elev = np.real(np.fft.ifft(2 * Yf))

    if False:
        plt.figure()
        plt.plot(data_in, label="data_in")
        plt.plot(elev, label="elev")
        plt.legend()
        plt.show()

    return elev


def find_close_index(array_in, value, tol=1e-3):
    array_deviation = np.abs(array_in - value)
    locations_close = np.where(array_deviation < tol)
    number_of_close = len(locations_close[0])
    assert number_of_close == 1, "found {} close values".format(number_of_close)
    return locations_close[0][0]


def find_index_of_fist_element_greater_than_value(array, value):
    indexes_where_greater_than = np.where(array > value)[0]
    if len(indexes_where_greater_than) == 0:
        return None
    else:
        return indexes_where_greater_than[0]


def compute_wave_spectrum_moments(wave_spectrum, list_frequencies, min_freq=0.04, max_freq=0.5):
    """Compute the moments of the wave spectrum."""

    min_ind = find_index_of_fist_element_greater_than_value(list_frequencies, min_freq)
    max_ind = find_index_of_fist_element_greater_than_value(list_frequencies, max_freq)

    wave_spectrum = wave_spectrum[min_ind:max_ind]
    list_frequencies = list_frequencies[min_ind:max_ind]

    if PERFORM_KET_PLOTS:
        plt.figure()
        plt.plot(list_frequencies, wave_spectrum)
        plt.show()

    omega = 2 * np.pi * list_frequencies

    M0 = integrate.trapz(wave_spectrum, x=omega)
    M1 = integrate.trapz(wave_spectrum * (omega), x=omega)
    M2 = integrate.trapz(wave_spectrum * (omega**2), x=omega)
    M3 = integrate.trapz(wave_spectrum * (omega**3), x=omega)
    M4 = integrate.trapz(wave_spectrum * (omega**4), x=omega)
    MM1 = integrate.trapz(wave_spectrum * (omega**(-1)), x=omega)
    MM2 = integrate.trapz(wave_spectrum * (omega**(-2)), x=omega)

    return(M0, M1, M2, M3, M4, MM1, MM2)


def compute_spectral_properties(M0, M2, M4, wave_spectrum, list_frequencies, min_freq=0.04, max_freq=0.5):
    """Compute SWH and the peak period, both zero up-crossing and peak-to-peak,
    from spectral moments."""

    min_ind = find_index_of_fist_element_greater_than_value(list_frequencies, min_freq)
    max_ind = find_index_of_fist_element_greater_than_value(list_frequencies, max_freq)

    wave_spectrum = wave_spectrum[min_ind:max_ind]
    list_frequencies = list_frequencies[min_ind:max_ind]

    Hs = np.sqrt(M0) * 4.0 / np.sqrt(2 * np.pi)
    T_z = 2.0 * np.pi * np.sqrt(M0 / M2)
    T_c = 2.0 * np.pi * np.sqrt(M2 / M4)
    T_p = 1.0 / list_frequencies[np.argmax(wave_spectrum)]

    if False:
        print('Hs (from M0) = {} m'.format(Hs))
        print('T_z = {} s | {} Hz'.format(T_z, 1.0 / T_z))
        print('T_p = {} s | {} Hz'.format(T_p, 1.0 / T_p))

    return(Hs, T_z, T_c, T_p)


def welch_spectrum(data_in, sampling_rate=10.0, overlap_proportion=0.9, segment_duration_seconds=400, smooth=True):
    nperseg = int(segment_duration_seconds * sampling_rate)
    noverlap = int(overlap_proportion * nperseg)

    f, Pxx_den = signal.welch(data_in, sampling_rate, nperseg=nperseg, noverlap=noverlap)

    if smooth:
        Pxx_den = signal.savgol_filter(Pxx_den, window_length=9, polyorder=2)

    if False:
        plt.figure()
        plt.plot(f, Pxx_den)
        plt.show()

    return(f, Pxx_den)


def compute_SWH(elevation):
    SWH = 4.0 * np.std(elevation)
    if False:
        print("SWH = {}".format(SWH))
    return SWH


def find_list_pkl_files(folder_pkl):
    # all the data files available
    list_all_files = os.listdir(folder_pkl)

    # go through the UG files, and check that there is a VN100 file available
    list_file_pairs = []
    for crrt_file in list_all_files:
        if find_out_file_kind(crrt_file) == "GAUGE":
            crrt_file_ug = crrt_file
            crrt_file_vn = crrt_file[:-9] + "VN100.pkl"

            if crrt_file_vn in list_all_files:
                if False:
                    print("files {} and {} are a pair".format(crrt_file_ug, crrt_file_vn))
                list_file_pairs.append((folder_pkl + crrt_file_ug, folder_pkl + crrt_file_vn))

    return list_file_pairs


def check_if_pair_is_valid(crrt_pair):
    print("working on file pair {} & {} in order to check if the data look valid.".format(crrt_pair[0], crrt_pair[1]))

    with open(crrt_pair[0], "rb") as fh:
        dict_data_ug = pkl.load(fh)

    with open(crrt_pair[1], "rb") as fh:
        dict_data_vn = pkl.load(fh)

    # check if the IMU data has a vertical acceleration that is centered around -9.81
    data_accel_down = dict_data_vn["interpolated_readings"][:, 5]
    mean_accel_down = float(np.mean(data_accel_down))
    if abs(-9.81 - mean_accel_down) > 0.10 * 9.81:
        print("looks like problematic mean_acc_D value: {}".format(mean_accel_down))
        print("ignore this pair of files")
        return (False, None)

    # check if the UG data has less than 20% saturated data
    # this checks for both saturated data, and possible freezing of the gauge
    squeezed_ug = np.squeeze(dict_data_ug["interpolated_readings"])
    nbr_of_points = len(squeezed_ug)
    saturated_high = np.sum(squeezed_ug >= 0.47)
    saturated_low = np.sum(squeezed_ug <= -0.47)
    ug_saturation_high_proportion = 1.0 * saturated_high / nbr_of_points
    ug_saturation_low_proportion = 1.0 * saturated_low / nbr_of_points
    total_amount_saturated = ug_saturation_low_proportion + ug_saturation_high_proportion

    if total_amount_saturated > 0.2:
        print("looks like problematic amount of saturated data: {}".format(total_amount_saturated))
        print("ignore this pair of files")
        return (False, None)

    # perform the analysis

    # integrate twice in time the IMU data, to get displacement downwards
    # first, remove the mean acceleration: do not accelerate at -G...
    # basic acceleration value is -9.81; this means that, if we accelerate up, we feel heavier, and g becomes more negative
    # i.e., when we integrate acceleration from the VN twice, we get motion downwards
    data_accel_down = data_accel_down - mean_accel_down
    data_vn_elevation_down = integrate_twice(data_accel_down)

    # find the common part of the time signal
    time_start = max(dict_data_ug["interpolated_timestamps"][0], dict_data_vn["interpolated_timestamps"][0])
    time_end = min(dict_data_ug["interpolated_timestamps"][-1], dict_data_vn["interpolated_timestamps"][-1])

    index_start_ug = find_close_index(dict_data_ug["interpolated_timestamps"], time_start)
    index_end_ug = find_close_index(dict_data_ug["interpolated_timestamps"], time_end)

    index_start_vn = find_close_index(dict_data_vn["interpolated_timestamps"], time_start)
    index_end_vn = find_close_index(dict_data_vn["interpolated_timestamps"], time_end)

    assert dict_data_ug["interpolated_timestamps"][index_start_ug] - dict_data_vn["interpolated_timestamps"][index_start_vn] < 1e-3
    assert dict_data_ug["interpolated_timestamps"][index_end_ug] - dict_data_vn["interpolated_timestamps"][index_end_vn] < 1e-3
    assert (index_end_ug - index_start_ug) == (index_end_vn - index_start_vn)

    common_time_base = dict_data_ug["interpolated_timestamps"][index_start_ug: index_end_ug]

    if len(common_time_base) < 10 * 60 * 8:
        print("not enough points, abort analysis of this pair")
        return (False, None)

    # compute the actual wave elevation
    #
    # if the elevation vn100 down goes up at constant UG reading, then the probe goes down and the water is at the same distance; i.e., water goes down
    # so, we need a sign - in from of VN elevation down
    #
    # if the UG reading goes up at constant probe absolute height (constant vn100 elevation down), then the water is getting further, i.e. it is going
    # down; we need a sign - in from of UG reading
    #
    # we need to take into account pitch and roll: 1) they change the apparent distance to the water due to projection effects
    # the "0-distance" to the water is 5m
    # this means that distance UG to water is: 5m + reading, so the compensation for pitch and roll is: (5_m + ug_m) * cos(pitch) * cos(roll)
    # at first order (going into more details, would need to apply full 3D rotation...)
    # 2) they change the location of the probe, because the IMU is not located at the exact same location as the probes
    # in our case, X is pointing to the left, Y is pointing to the front of the boat
    # ie the true pitch of the boat is imu_roll
    #    the true roll of the boat is -imu_pitch
    squeezed_ug = np.squeeze(dict_data_ug["interpolated_readings"])
    data_pitch_rad = dict_data_vn["interpolated_readings"][:, 1][index_start_vn:index_end_vn] * np.pi / 180.0
    data_roll_rad = dict_data_vn["interpolated_readings"][:, 2][index_start_vn:index_end_vn] * np.pi / 180.0
    boat_pitch_rad = data_roll_rad - np.mean(data_roll_rad)
    boat_roll_rad = - data_pitch_rad + np.mean(data_pitch_rad)
    data_water_elevation_no_pitch_roll = -data_vn_elevation_down[index_start_vn:index_end_vn] - squeezed_ug[index_start_ug:index_end_ug]
    data_water_elevation = -data_vn_elevation_down[index_start_vn:index_end_vn] \
        - (5 + squeezed_ug[index_start_ug:index_end_ug]) * np.cos(data_pitch_rad) * np.cos(data_roll_rad) + 5 \
        - 6.0 * (1 - np.cos(boat_roll_rad)) \
        - 2.5 * np.sin(boat_pitch_rad)

    # now, perform a wave properties analysis using the spectral method. We do not use other methods than the spectra method because it is
    # the only way to remove noise (which will be far outside of the frequency band of interst for us)
    SWH = compute_SWH(data_water_elevation)
    f, Pxx_den = welch_spectrum(data_water_elevation)
    M0, M1, M2, M3, M4, MM1, MM2 = compute_wave_spectrum_moments(Pxx_den, f)
    Hs, T_z, T_c, T_p = compute_spectral_properties(M0, M2, M4, Pxx_den, f)

    # the data we produce as a dict
    dict_data = {}

    dict_data["first_timestamp"] = common_time_base[0]

    dict_data["SWH"] = SWH
    dict_data["Hs"] = Hs
    dict_data["T_z"] = T_z
    dict_data["T_c"] = T_c
    dict_data["T_p"] = T_p
    dict_data["f"] = f
    dict_data["Pxx_den"] = Pxx_den

    if True:
        print("proportion saturated high: {}".format(ug_saturation_high_proportion))
        print("proportion saturated low: {}".format(ug_saturation_low_proportion))
        print("SWH = {}".format(SWH))
        print("Hs = {}".format(Hs))
        print("T_z = {}".format(T_z))
        print("T_c = {}".format(T_c))
        print("T_p = {}".format(T_p))

    if True:
        plt.figure()
        plt.plot(common_time_base, data_water_elevation_no_pitch_roll, label="water elevation no pitch roll")
        plt.plot(common_time_base, data_water_elevation, label="water elevation")
        plt.plot(common_time_base, -data_vn_elevation_down[index_start_vn:index_end_vn], label="-vn_elevation_down")
        plt.plot(common_time_base, -squeezed_ug[index_start_ug:index_end_ug], label="-ug_reading")
        plt.legend()

    # plot and ask for user feedback
    if True:
        print("ask for user feedback to visually check the quality of the file...")

        if False:
            plt.figure()
            plt.plot(dict_data_vn["interpolated_timestamps"], dict_data_vn["interpolated_readings"][:, 5], label="acc_D [m/s2]")
            plt.plot(dict_data_vn["interpolated_timestamps"], dict_data_vn["interpolated_readings"][:, 1], label="pitch [deg]")
            plt.plot(dict_data_vn["interpolated_timestamps"], dict_data_vn["interpolated_readings"][:, 2], label="roll [deg]")
            plt.legend()

        if False:
            plt.figure()
            plt.plot(dict_data_ug["interpolated_timestamps"], np.squeeze(dict_data_ug["interpolated_readings"]), label="UG reading [m]")
            plt.legend()

        if True:
            plt.figure()
            plt.plot(dict_data_vn["interpolated_timestamps"][::5], dict_data_vn["interpolated_readings"][:, 5][::5]+9.81, label="acc_D [m/s2]")
            plt.plot(dict_data_vn["interpolated_timestamps"][::5], dict_data_vn["interpolated_readings"][:, 1][::5], label="pitch [deg]")
            plt.plot(dict_data_vn["interpolated_timestamps"][::5], dict_data_vn["interpolated_readings"][:, 2][::5], label="roll [deg]")
            plt.plot(dict_data_ug["interpolated_timestamps"][::5], np.squeeze(dict_data_ug["interpolated_readings"])[::5], label="UG reading [m]")
            plt.legend()

            plt.show()

        while True:
            print("do you want to accept this pair of files? [y/n]:")
            char_in = readchar.readchar()

            if char_in == "y":
                print("use")
                break
            elif char_in == "n":
                print("ignore")
                return (False, None)
            else:
                print("answer a single keystroke y or n")

        plt.close('all')

    return (True, dict_data)


# ------------------------------------------------------------------------------------------

if __name__ == "__main__":
    folder_pkl = "/home/jrmet/Desktop/Data/bow_sensor/on_time_base/"
    list_file_pairs = find_list_pkl_files(folder_pkl)

    for crrt_pair in list_file_pairs:
        print("")
        print("########################################")
        to_use, dict_results = check_if_pair_is_valid(crrt_pair)
        if to_use:
            file_out = crrt_pair[0][:-9] + "stats.pkl"
            with open(file_out, "wb") as fh:
                print("dump results in {}".format(file_out))
                pkl.dump(dict_results, fh)
