import pickle as pkl
import datetime

import math

import readchar
from scipy.signal import butter, lfilter, freqz

import numpy as np
import matplotlib.pyplot as plt

from scipy import integrate
from scipy import signal

import os
import time

from dataclasses import dataclass

os.environ["TZ"] = "UTC"
time.tzset()


@dataclass
class PairPacket:
    datetime_start: datetime.datetime
    datetime_end: datetime.datetime
    path_vn100_file: str
    path_ug_file: str


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


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


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

    if False:
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


def compute_spectral_properties(M0, M2, M4, wave_spectrum, list_frequencies, min_freq=0.055, max_freq=0.11):
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


def welch_spectrum(data_in, sampling_rate=10.0, overlap_proportion=0.9, segment_duration_seconds=400, smooth=True, plot=False):
    nperseg = int(segment_duration_seconds * sampling_rate)
    noverlap = int(overlap_proportion * nperseg)

    f, Pxx_den = signal.welch(data_in, sampling_rate, nperseg=nperseg, noverlap=noverlap)

    if smooth:
        Pxx_den = signal.savgol_filter(Pxx_den, window_length=9, polyorder=2)

    if plot:
        plt.figure()
        plt.plot(f, Pxx_den)
        plt.xlim([0.02, 0.2])
        plt.show()

    return(f, Pxx_den)


def compute_SWH(elevation):
    SWH = 4.0 * np.std(elevation)
    if False:
        print("SWH = {}".format(SWH))
    return SWH


def find_list_pkl_files(folder_pkl):
    # all the data files available
    list_all_files = sorted(os.listdir(folder_pkl))

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


def plot_ug_vn_files_pair(crrt_pair, label=False, renormalize=False, undersample=10):
    with open(crrt_pair.path_vn100_file, "br") as fh:
        dict_in_vn = pkl.load(fh)

    with open(crrt_pair.path_ug_file, "br") as fh:
        dict_in_ug = pkl.load(fh)

    ug_time_base = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in dict_in_ug["interpolated_timestamps"][::undersample]]
    vn_time_base = [datetime.datetime.fromtimestamp(crrt_timestamp) for crrt_timestamp in dict_in_vn["interpolated_timestamps"][::undersample]]

    ug_signal = dict_in_ug["interpolated_readings"][::undersample]
    mean_ug = np.mean(ug_signal)
    std_ug = np.std(ug_signal)

    vn_signal = dict_in_vn["interpolated_readings"][:, 5][::undersample]
    mean_vn = np.mean(vn_signal)
    std_vn = np.std(vn_signal)

    if renormalize:
        ug_normalized = (ug_signal - mean_ug) / std_ug
        vn_normalized = (vn_signal - mean_vn) / std_vn
    else:
        ug_normalized = ug_signal
        vn_normalized = vn_signal
        

    if label:
        plt.plot(ug_time_base, ug_normalized, label="ug normalized", color="r")
        plt.plot(vn_time_base, vn_normalized, label="accel down normalized", color="k")
    else:
        plt.plot(ug_time_base, ug_normalized, color="r")
        plt.plot(vn_time_base, vn_normalized, color="k")
