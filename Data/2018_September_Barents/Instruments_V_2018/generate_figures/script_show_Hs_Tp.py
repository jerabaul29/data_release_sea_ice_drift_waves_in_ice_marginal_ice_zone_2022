from datetime import datetime, timedelta
import pickle
import pytz
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import integrate
from utils import sort_dict_keys_by_date

# initially from ../generate_dict_data/load_Iridium_wave_data ugly but...
def expand_raw_variables(dict_data):
    SWH = dict_data["raw_data"]["SWH"]
    T_z0 = dict_data["raw_data"]["T_z0"]
    Hs = dict_data["raw_data"]["Hs"]
    T_z = dict_data["raw_data"]["T_z"]
    freq = dict_data["raw_data"]["freq"]
    fmin = dict_data["raw_data"]["fmin"]
    fmax = dict_data["raw_data"]["fmax"]
    nfreq = dict_data["raw_data"]["nfreq"]
    a0_proc = dict_data["raw_data"]["a0_proc"]
    a1_proc = dict_data["raw_data"]["a1_proc"]
    a2_proc = dict_data["raw_data"]["a2_proc"]
    b1_proc = dict_data["raw_data"]["b1_proc"]
    b2_proc = dict_data["raw_data"]["b2_proc"]
    R_proc = dict_data["raw_data"]["R_proc"]

    return(SWH, T_z0, Hs, T_z, freq, fmin, fmax, nfreq, a0_proc, a1_proc, a2_proc, b1_proc, b2_proc, R_proc)

# ------------------------------------------------------------------------------
# load the data
path_to_dump = "../generate_dict_data/all.pkl"
with open(path_to_dump, 'rb') as fh:
    dict_data = pickle.load(fh)

# ------------------------------------------------------------------------------
# list of colors at https://stackoverflow.com/questions/22408237/named-colors-in-matplotlib
list_colors = ['k', 'r', 'b', 'orange', 'gray', 'purple']

plt.rcParams.update({'font.size': 14})
# plt.rcParams.update({'figure.autolayout': True})

# %% a few parameters
REMOVE_NOISE = True
MAX_DURATION_BETWEEN_DATA = timedelta(hours=6)
DURATION_BEFORE_AFTER_INSERTION = timedelta(hours=3)

# %% some helper function
class Iridium_object_wrapper(object):
    pass


iridium_object = Iridium_object_wrapper()
iridium_object.verbose = 0


def compute_wave_spectrum_moments(self):
    """Compute the moments of the wave spectrum."""

    omega = 2 * np.pi * self.freq

    # note: integrate only on the 'valid' part of the spectrum

    self.M0 = integrate.trapz(self.a0, x=omega)
    self.M1 = integrate.trapz(self.a0 * (omega), x=omega)
    self.M2 = integrate.trapz(self.a0 * (omega**2), x=omega)
    self.M3 = integrate.trapz(self.a0 * (omega**3), x=omega)
    self.M4 = integrate.trapz(self.a0 * (omega**4), x=omega)
    self.MM1 = integrate.trapz(self.a0 * (omega**(-1)), x=omega)
    self.MM2 = integrate.trapz(self.a0 * (omega**(-2)), x=omega)

    if self.verbose > 1:
        print('min, max of freq is {}, {}'.format(self.freq.min(), self.freq.max()))
        print('f shape is {}'.format(self.freq.shape))

def compute_spectral_properties(self):
    """Compute SWH and the peak period, both zero up-crossing and peak-to-peak,
    from spectral moments."""

    self.Hs = np.sqrt(self.M0) * 4.0 / np.sqrt(2 * np.pi)
    self.T_z = 2.0 * np.pi * np.sqrt(self.M0 / self.M2)
    self.T_c = 2.0 * np.pi * np.sqrt(self.M2 / self.M4)
    self.T_p = 1.0 / self.freq[np.argmax(self.a0)]

    if self.verbose > 2:
        print('Hs (from M0) = {}'.format(self.Hs))
        print('T_z = {}'.format(self.T_z))
        print('T_c = {}'.format(self.T_c))
        print('T_p = {}'.format(self.T_p))


def remove_noise_PSD(PSD, PSD_noise):
    """remove the noise out of a PSD.

    Idea:

    - PSD(f) = E [ |FFT(f)|**2 ] = E [ (FFT(f)) * conj(FFT(f)) ]
    - but some noise: FFT(f) = FFTsignal(f) + FFTnoise(f)
    - ie PSD(f) = E [ (FFTsignal(f) + FFTnoise(f)) * conj(FFTsignal(f) + FFTnoise(f)) ]
                = E [ FFTsignal(f) * conj(FFTsignal(f)) + FFTnoise(f) * conj(FFTnoise(f)) + 2 * Re( FFTsignal(f) * conj( FFTnoise(f) ) ) ]
    - then have to make some hypothesis: - noise and signal uncorrelated
         PSD(f) =         PSDsignal(f)              +          PSDnoise(f)            + 2 * Re( E[ FFTsignal(f) * conj( FFTnoise(f) ) ] )
                =         PSDsignal(f)              +          PSDnoise(f)            + 2 * Re( E[FFTsignal(f)] * E[ conj( FFTnoise ) ] )
                                         - the phase of the signals is random, ie E(Im) = E(Re) = 0, ie:
                =         PSDsignal(f)              +          PSDnoise(f)
    """

    denoised_value = PSD - PSD_noise
    index_too_low = np.where(denoised_value < 1e-14)
    denoised_value[index_too_low] = 1e-14

    return(denoised_value)


# to put into UTC
now_utc = datetime.now(pytz.utc)
today_utc = now_utc.date()

""" later on, want to look at damping, and compare with models?"""


time_start = datetime(year=2018, month=9, day=15, hour=00, tzinfo=None)  # the beginning of the cruise
# THE VALUE UNDER IS IN CASE OǸLY 3 LAST INSTRUMENTS
# time_start = datetime(year=2020, month=8, day=20, hour=00, tzinfo=None)  # the beginning of the cruise
time_end = datetime(year=2018, month=10, day=15, hour=23, tzinfo=None)  # long enough later that all stopped to work

# %% sort dictionary by date of transmission
keys_sorted_by_date = sort_dict_keys_by_date(dict_data)

# %% load the whole data; this is ugly and should be broken in a series of functions, but...
dict_data_each_logger = {}

for crrt_key in keys_sorted_by_date:
    crrt_time = dict_data[crrt_key]['datetime']

    # check if within the time
    if crrt_time > time_start and crrt_time < time_end:
        crrt_logger_ID = dict_data[crrt_key]['Device']

        # if a spectrum file, fill in the status
        if dict_data[crrt_key]['data_kind'] == 'spectrum':

            # create the lists if necessary
            if crrt_logger_ID not in dict_data_each_logger:
                dict_data_each_logger[crrt_logger_ID] = {}
                dict_data_each_logger[crrt_logger_ID]["datetime"] = []
                dict_data_each_logger[crrt_logger_ID]["freq"] = []
                dict_data_each_logger[crrt_logger_ID]["a0_proc"] = []
                dict_data_each_logger[crrt_logger_ID]["R_proc"] = []

                dict_data_each_logger[crrt_logger_ID]["SWH"] = []
                dict_data_each_logger[crrt_logger_ID]["Hs"] = []
                dict_data_each_logger[crrt_logger_ID]["T_z0"] = []
                dict_data_each_logger[crrt_logger_ID]["T_z"] = []
                # re processed from reduced spectra
                dict_data_each_logger[crrt_logger_ID]["Hs_proc"] = []
                dict_data_each_logger[crrt_logger_ID]["T_z_proc"] = []
                dict_data_each_logger[crrt_logger_ID]["T_c_proc"] = []
                dict_data_each_logger[crrt_logger_ID]["T_p_proc"] = []

            crrt_dict = dict_data[crrt_key]['parsed_data']
            (SWH, T_z0, Hs, T_z, freq, fmin, fmax, nfreq, a0_proc, a1_proc, a2_proc, b1_proc, b2_proc, R_proc) = expand_raw_variables(crrt_dict)

            iridium_object.freq = freq
            iridium_object.a0 = a0_proc

            compute_wave_spectrum_moments(iridium_object)
            compute_spectral_properties(iridium_object)

            noise = (0.24 * 9.81e-3)**2 * ((2 * np.pi * freq)**(-4))
            if REMOVE_NOISE:
                a0_proc = remove_noise_PSD(a0_proc, noise)

            dict_data_each_logger[crrt_logger_ID]["a0_proc"].append(a0_proc)
            dict_data_each_logger[crrt_logger_ID]["R_proc"].append(R_proc)
            dict_data_each_logger[crrt_logger_ID]["freq"].append(freq)
            dict_data_each_logger[crrt_logger_ID]["datetime"].append(crrt_time)

            dict_data_each_logger[crrt_logger_ID]["SWH"].append(SWH)
            dict_data_each_logger[crrt_logger_ID]["Hs"].append(Hs)
            dict_data_each_logger[crrt_logger_ID]["T_z0"].append(T_z0)
            dict_data_each_logger[crrt_logger_ID]["T_z"].append(T_z)

            dict_data_each_logger[crrt_logger_ID]["Hs_proc"].append(iridium_object.Hs)
            dict_data_each_logger[crrt_logger_ID]["T_z_proc"].append(iridium_object.T_z)
            dict_data_each_logger[crrt_logger_ID]["T_c_proc"].append(iridium_object.T_c)
            dict_data_each_logger[crrt_logger_ID]["T_p_proc"].append(iridium_object.T_p)

            # dict_data_each_logger[crrt_logger_ID]["aggregated_a0_proc"] = np.array(dict_data_each_logger[crrt_logger_ID]["a0_proc"])

list_instruments = list(dict_data_each_logger.keys())
# THE VALUE UNDER IS IN CASE SHOW ONLY 3 LAST INSTRUMENTS
# list_instruments = ['RockBLOCK 18958', 'RockBLOCK 18715', 'RockBLOCK 17330']
print(list_instruments)

# take care of missing data, find where too large hole withoug data, and insert NaNs
for crrt_index, crrt_logger_ID in enumerate(list_instruments):
    crrt_datetime_list = dict_data_each_logger[crrt_logger_ID]["datetime"]
    crrt_a0_proc_list = dict_data_each_logger[crrt_logger_ID]["a0_proc"]
    crrt_R_proc_list = dict_data_each_logger[crrt_logger_ID]["R_proc"]
    crrt_SWH_list = dict_data_each_logger[crrt_logger_ID]["SWH"]
    crrt_Hs_list = dict_data_each_logger[crrt_logger_ID]["Hs"]
    crrt_T_z0_list = dict_data_each_logger[crrt_logger_ID]["T_z0"]
    crrt_T_z_list = dict_data_each_logger[crrt_logger_ID]["T_z"]

    crrt_Hs_proc_list = dict_data_each_logger[crrt_logger_ID]["Hs_proc"]
    crrt_T_z_proc_list = dict_data_each_logger[crrt_logger_ID]["T_z_proc"]
    crrt_T_c_proc_list = dict_data_each_logger[crrt_logger_ID]["T_c_proc"]
    crrt_T_p_proc_list = dict_data_each_logger[crrt_logger_ID]["T_p_proc"]

    shape_a0_proc = np.shape(crrt_a0_proc_list[0])
    shape_R_proc = np.shape(crrt_R_proc_list[0])
    # NaN_a0_proc = np.nan(shape_a0_proc)
    NaN_a0_proc = np.full(shape_a0_proc, np.nan)
    NaN_R_proc = np.full(shape_R_proc, np.nan)

    new_datetime_list = []
    new_a0_proc_list = []
    new_R_proc_list = []
    new_SWH_list = []
    new_Hs_list = []
    new_T_z0_list = []
    new_T_z_list = []

    new_Hs_proc_list = []
    new_T_z_proc_list = []
    new_T_c_proc_list = []
    new_T_p_proc_list = []

    crrt_datetime_previous = crrt_datetime_list[0]

    new_datetime_list.append(crrt_datetime_list[0])
    new_a0_proc_list.append(crrt_a0_proc_list[0])
    new_R_proc_list.append(crrt_R_proc_list[0])
    new_SWH_list.append(crrt_SWH_list[0])
    new_Hs_list.append(crrt_Hs_list[0])
    new_T_z0_list.append(crrt_T_z0_list[0])
    new_T_z_list.append(crrt_T_z_list[0])

    new_Hs_proc_list.append(crrt_Hs_proc_list[0])
    new_T_z_proc_list.append(crrt_T_z_proc_list[0])
    new_T_c_proc_list.append(crrt_T_c_proc_list[0])
    new_T_p_proc_list.append(crrt_T_p_proc_list[0])

    for (crrt_index, crrt_datetime) in enumerate(crrt_datetime_list[1:]):
        crrt_duration = crrt_datetime - crrt_datetime_previous

        if crrt_duration > MAX_DURATION_BETWEEN_DATA:
            # add the necessary points and timestamps
            new_a0_proc_list.append(NaN_a0_proc)
            new_a0_proc_list.append(NaN_a0_proc)

            new_R_proc_list.append(NaN_R_proc)
            new_R_proc_list.append(NaN_R_proc)

            new_SWH_list.append(np.NaN)
            new_SWH_list.append(np.NaN)

            new_Hs_list.append(np.NaN)
            new_Hs_list.append(np.NaN)

            new_T_z0_list.append(np.NaN)
            new_T_z0_list.append(np.NaN)

            new_T_z_list.append(np.NaN)
            new_T_z_list.append(np.NaN)

            new_Hs_proc_list.append(np.NaN)
            new_T_z_proc_list.append(np.NaN)
            new_T_c_proc_list.append(np.NaN)
            new_T_p_proc_list.append(np.NaN)
            new_Hs_proc_list.append(np.NaN)
            new_T_z_proc_list.append(np.NaN)
            new_T_c_proc_list.append(np.NaN)
            new_T_p_proc_list.append(np.NaN)

            new_datetime_list.append(crrt_datetime_previous + DURATION_BEFORE_AFTER_INSERTION)
            new_datetime_list.append(crrt_datetime - DURATION_BEFORE_AFTER_INSERTION)

        new_datetime_list.append(crrt_datetime)
        new_a0_proc_list.append(crrt_a0_proc_list[crrt_index])
        new_R_proc_list.append(crrt_R_proc_list[crrt_index])
        new_SWH_list.append(crrt_SWH_list[crrt_index])
        new_Hs_list.append(crrt_Hs_list[crrt_index])
        new_T_z0_list.append(crrt_T_z0_list[crrt_index])
        new_T_z_list.append(crrt_T_z_list[crrt_index])

        new_Hs_proc_list.append(crrt_Hs_proc_list[crrt_index])
        new_T_z_proc_list.append(crrt_T_z_proc_list[crrt_index])
        new_T_c_proc_list.append(crrt_T_c_proc_list[crrt_index])
        new_T_p_proc_list.append(crrt_T_p_proc_list[crrt_index])

        crrt_datetime_previous = crrt_datetime

    dict_data_each_logger[crrt_logger_ID]['datetime'] = new_datetime_list
    dict_data_each_logger[crrt_logger_ID]["a0_proc"] = new_a0_proc_list
    dict_data_each_logger[crrt_logger_ID]["R_proc"] = new_R_proc_list
    dict_data_each_logger[crrt_logger_ID]["SWH"] = new_SWH_list
    dict_data_each_logger[crrt_logger_ID]["Hs"] = new_Hs_list
    dict_data_each_logger[crrt_logger_ID]["T_z0"] = new_T_z0_list
    dict_data_each_logger[crrt_logger_ID]["T_z"] = new_T_z_list

    dict_data_each_logger[crrt_logger_ID]["Hs_proc"] = new_Hs_proc_list
    dict_data_each_logger[crrt_logger_ID]["T_z_proc"] = new_T_z_proc_list
    dict_data_each_logger[crrt_logger_ID]["T_c_proc"] = new_T_c_proc_list
    dict_data_each_logger[crrt_logger_ID]["T_p_proc"] = new_T_p_proc_list

    dict_data_each_logger[crrt_logger_ID]["aggregated_a0_proc"] = np.array(dict_data_each_logger[crrt_logger_ID]["a0_proc"])
    dict_data_each_logger[crrt_logger_ID]["aggregated_R_proc"] = np.array(dict_data_each_logger[crrt_logger_ID]["a0_proc"])

# time_end = datetime(year=2018, month=9, day=28, hour=23, tzinfo=None)  # long enough later that all stopped to work

with open("./dict_data_each_logger_wave.pkl", "wb") as fh:
    pickle.dump(dict_data_each_logger, fh)

if True:
    # %% plot of SWH and T_z0
    fig, axes = plt.subplots(nrows=2, ncols=1)

    time_start_md = mdates.date2num(time_start)
    time_end_md = mdates.date2num(time_end)

    plt.subplot(2, 1, 1)

    for crrt_index, crrt_logger_ID in enumerate(list_instruments):
        crrt_datetime = dict_data_each_logger[crrt_logger_ID]["datetime"]

        crrt_color = list_colors[crrt_index]

        # using the SWH from time series
        crrt_SWH = dict_data_each_logger[crrt_logger_ID]["SWH"]
        plt.plot(crrt_datetime, crrt_SWH, color=crrt_color, linestyle='-', label=str(crrt_logger_ID)[10:] + " H$_{S0}$")

        # using the Hs from time series
        crrt_Hs = dict_data_each_logger[crrt_logger_ID]["Hs"]
        plt.plot(crrt_datetime, crrt_Hs, color=crrt_color, linestyle='--', label=str(crrt_logger_ID)[10:] + " H$_{St}$ ")

    plt.xlim([time_start_md, time_end_md])
    plt.ylim([-0.1, 2.5])
    plt.xticks([])
    plt.legend(loc="upper left", ncol=3, fontsize=12)
    plt.ylabel("SWH (m)")

    plt.subplot(2, 1, 2)

    for crrt_index, crrt_logger_ID in enumerate(list_instruments):
        crrt_datetime = dict_data_each_logger[crrt_logger_ID]["datetime"]

        crrt_color = list_colors[crrt_index]

        # wave period from Tz0
        crrt_T_z0 = dict_data_each_logger[crrt_logger_ID]["T_z0"]
        plt.plot(crrt_datetime, crrt_T_z0, label=str(crrt_logger_ID)[10:] + " $T_{z0}$", color=crrt_color, linestyle="-")

        # wave period from Tz
        crrt_T_z = dict_data_each_logger[crrt_logger_ID]["T_z"]
        plt.plot(crrt_datetime, crrt_T_z, label=str(crrt_logger_ID)[10:] + " $T_z$", color=crrt_color, linestyle="--")

    plt.ylim([-0.2, 23.0])
    plt.xlim([time_start_md, time_end_md])
    plt.xticks(rotation=30)
    plt.ylabel("WP (s)")

    plt.tight_layout()
    plt.legend(ncol=3, loc="upper left", fontsize=12)

    plt.savefig("script_show_Hs_Tp__doubleplot.pdf")

if True:
    # %% perform the plotting as a spectrogram in multi figure
    fig, axes = plt.subplots(nrows=len(list_instruments), ncols=1)

    time_start_md = mdates.date2num(time_start)
    time_end_md = mdates.date2num(time_end)

    for crrt_index, crrt_logger_ID in enumerate(list_instruments):
        plt.subplot(len(list_instruments), 1, crrt_index + 1)

        crrt_freq = dict_data_each_logger[crrt_logger_ID]["freq"]
        crrt_datetime = dict_data_each_logger[crrt_logger_ID]["datetime"]
        crrt_spectra = dict_data_each_logger[crrt_logger_ID]["aggregated_a0_proc"]

        crrt_spectra_logged = np.log10(crrt_spectra)
        pclr = plt.pcolor(crrt_datetime[1:], crrt_freq[0], np.transpose(crrt_spectra_logged)[:, 1:], vmin=-3.0, vmax=1.0)  # we ignore the first spectrum: corrupted by deployment

        if crrt_index < len(list_instruments)-1:
            plt.xticks([])

        plt.xticks(rotation=30)

        plt.ylabel("f [Hz]\n(instr. {})".format(str(crrt_logger_ID)[10:]))
        plt.xlim([time_start_md, time_end_md])

        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(pclr, cax=cbar_ax)
        # cbar = fig.colorbar(pclr)
        cbar.set_label('log$_{10}$(S) [m$^2$/Hz]')

        # plt.tight_layout()
        plt.savefig("script_show_Hs_Tp__spectra.pdf")

plt.show()
