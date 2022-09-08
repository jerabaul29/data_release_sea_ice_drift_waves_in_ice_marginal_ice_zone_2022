from pathlib import Path

from icecream import ic

import pandas as pd

import pickle

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("*** define global and config variables")

DEFAULT_HEADER = r"Battery Voltage (V),Power (W),Humidity (%rel),Epoch Time,Significant Wave Height (m),Peak Period (s),Mean Period (s),Peak Direction (deg),Peak Directional Spread (deg),Mean Direction (deg),Mean Directional Spread (deg),Latitude (deg),Longitude (deg),f_0,f_1,f_2,f_3,f_4,f_5,f_6,f_7,f_8,f_9,f_10,f_11,f_12,f_13,f_14,f_15,f_16,f_17,f_18,f_19,f_20,f_21,f_22,f_23,f_24,f_25,f_26,f_27,f_28,f_29,f_30,f_31,f_32,f_33,f_34,f_35,f_36,f_37,f_38,df_0,df_1,df_2,df_3,df_4,df_5,df_6,df_7,df_8,df_9,df_10,df_11,df_12,df_13,df_14,df_15,df_16,df_17,df_18,df_19,df_20,df_21,df_22,df_23,df_24,df_25,df_26,df_27,df_28,df_29,df_30,df_31,df_32,df_33,df_34,df_35,df_36,df_37,df_38,a1_0,a1_1,a1_2,a1_3,a1_4,a1_5,a1_6,a1_7,a1_8,a1_9,a1_10,a1_11,a1_12,a1_13,a1_14,a1_15,a1_16,a1_17,a1_18,a1_19,a1_20,a1_21,a1_22,a1_23,a1_24,a1_25,a1_26,a1_27,a1_28,a1_29,a1_30,a1_31,a1_32,a1_33,a1_34,a1_35,a1_36,a1_37,a1_38,b1_0,b1_1,b1_2,b1_3,b1_4,b1_5,b1_6,b1_7,b1_8,b1_9,b1_10,b1_11,b1_12,b1_13,b1_14,b1_15,b1_16,b1_17,b1_18,b1_19,b1_20,b1_21,b1_22,b1_23,b1_24,b1_25,b1_26,b1_27,b1_28,b1_29,b1_30,b1_31,b1_32,b1_33,b1_34,b1_35,b1_36,b1_37,b1_38,a2_0,a2_1,a2_2,a2_3,a2_4,a2_5,a2_6,a2_7,a2_8,a2_9,a2_10,a2_11,a2_12,a2_13,a2_14,a2_15,a2_16,a2_17,a2_18,a2_19,a2_20,a2_21,a2_22,a2_23,a2_24,a2_25,a2_26,a2_27,a2_28,a2_29,a2_30,a2_31,a2_32,a2_33,a2_34,a2_35,a2_36,a2_37,a2_38,b2_0,b2_1,b2_2,b2_3,b2_4,b2_5,b2_6,b2_7,b2_8,b2_9,b2_10,b2_11,b2_12,b2_13,b2_14,b2_15,b2_16,b2_17,b2_18,b2_19,b2_20,b2_21,b2_22,b2_23,b2_24,b2_25,b2_26,b2_27,b2_28,b2_29,b2_30,b2_31,b2_32,b2_33,b2_34,b2_35,b2_36,b2_37,b2_38,varianceDensity_0,varianceDensity_1,varianceDensity_2,varianceDensity_3,varianceDensity_4,varianceDensity_5,varianceDensity_6,varianceDensity_7,varianceDensity_8,varianceDensity_9,varianceDensity_10,varianceDensity_11,varianceDensity_12,varianceDensity_13,varianceDensity_14,varianceDensity_15,varianceDensity_16,varianceDensity_17,varianceDensity_18,varianceDensity_19,varianceDensity_20,varianceDensity_21,varianceDensity_22,varianceDensity_23,varianceDensity_24,varianceDensity_25,varianceDensity_26,varianceDensity_27,varianceDensity_28,varianceDensity_29,varianceDensity_30,varianceDensity_31,varianceDensity_32,varianceDensity_33,varianceDensity_34,varianceDensity_35,varianceDensity_36,varianceDensity_37,varianceDensity_38,direction_0,direction_1,direction_2,direction_3,direction_4,direction_5,direction_6,direction_7,direction_8,direction_9,direction_10,direction_11,direction_12,direction_13,direction_14,direction_15,direction_16,direction_17,direction_18,direction_19,direction_20,direction_21,direction_22,direction_23,direction_24,direction_25,direction_26,direction_27,direction_28,direction_29,direction_30,direction_31,direction_32,direction_33,direction_34,direction_35,direction_36,direction_37,direction_38,directionalSpread_0,directionalSpread_1,directionalSpread_2,directionalSpread_3,directionalSpread_4,directionalSpread_5,directionalSpread_6,directionalSpread_7,directionalSpread_8,directionalSpread_9,directionalSpread_10,directionalSpread_11,directionalSpread_12,directionalSpread_13,directionalSpread_14,directionalSpread_15,directionalSpread_16,directionalSpread_17,directionalSpread_18,directionalSpread_19,directionalSpread_20,directionalSpread_21,directionalSpread_22,directionalSpread_23,directionalSpread_24,directionalSpread_25,directionalSpread_26,directionalSpread_27,directionalSpread_28,directionalSpread_29,directionalSpread_30,directionalSpread_31,directionalSpread_32,directionalSpread_33,directionalSpread_34,directionalSpread_35,directionalSpread_36,directionalSpread_37,directionalSpread_38,Wind Speed (m/s),Wind Direction (deg),Surface Temperature (°C),Partition0 Start Frequency (hz),Partition0 End Frequency (hz),Partition0 Significant Wave Height (m),Partition0 Mean Period (s),Partition0 Mean Direction (deg),Partition0 Mean Directional Spread (deg),Partition1 Start Frequency (hz),Partition1 End Frequency (hz),Partition1 Significant Wave Height (m),Partition1 Mean Period (s),Partition1 Mean Direction (deg),Partition1 Mean Directional Spread (deg)"
DEFAULT_FREQS = [0.0293, 0.03906, 0.04883, 0.058589999999999996, 0.06836, 0.07812999999999999, 0.08789, 0.09766, 0.10742, 0.11719, 0.12695, 0.13672, 0.14648, 0.15625, 0.16602, 0.17578, 0.18555, 0.19530999999999998, 0.20508, 0.21484, 0.22461, 0.23438, 0.24414, 0.25390999999999997, 0.26366999999999996, 0.27344, 0.2832, 0.29297, 0.30273, 0.3125, 0.32227, 0.33203, 0.35156, 0.38086, 0.41016, 0.43945, 0.46875, 0.49805, 0.6543]
DEFAULT_EMPTY_FREQS = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']

# ------------------------------------------------------------------------------------------
print("*** find list of files to read")

path_to_data = Path.cwd() / ".." / "data"
ic(path_to_data)

list_all_data_files = list(path_to_data.glob("SPOT-*.csv"))
ic(list_all_data_files)

dict_path_to_instrument = {}
list_instruments = []

for crrt_file in list_all_data_files:
    crrt_instr = "SPOT-1386"
    if crrt_instr not in list_instruments:
        list_instruments.append(crrt_instr)

    with open(crrt_file, "r") as fh:
        line_1 = fh.readline()[:-1]

    if line_1 == DEFAULT_HEADER:
        dict_path_to_instrument[crrt_file] = crrt_instr
    else:
        ic(line_1)
        raise RuntimeError("invalid header")

# ------------------------------------------------------------------------------------------
print("*** parse each of the files")


def convert_to_list_floats(list_in):
    list_out = []

    for crrt_entry in list_in:
        if crrt_entry is float:
            list_out.append(crrt_entry)
        else:
            list_out.append(float(crrt_entry))

    return list_out


def two_lists_equal_within_uncertainty(list_1, list_2, uncertainty=1e-6):
    assert len(list_1) == len(list_2)

    for crrt_1, crrt_2 in zip(list_1, list_2):
        if abs(crrt_1 - crrt_2) > uncertainty:
            return False

    return True


dict_all_data = {}
for crrt_instr in list_instruments:
    dict_all_data[crrt_instr] = {}

for crrt_file in list_all_data_files:
    with open(crrt_file, "r") as fh:
        header = fh.readline()[:-1]
        assert header == DEFAULT_HEADER

    crrt_instrument = dict_path_to_instrument[crrt_file]

    parsed = pd.read_csv(crrt_file, delimiter=",")

    # get the data we are interested in...

    # how many entries
    nbr_entries = parsed.shape[0]

    # epoch time
    all_epoch_time = parsed.loc[:, "Epoch Time"]

    # lat lon
    all_lat_lon = parsed.loc[:, ["Latitude (deg)", "Longitude (deg)"]]

    # frequencies and spectra
    all_frequencies = parsed.loc[:, "f_0":"f_38"]
    all_wave_spectrum = parsed.loc[:, "varianceDensity_0":"varianceDensity_38"]

    # wave statistics
    all_wave_stats = parsed.loc[:, ["Significant Wave Height (m)", "Peak Period (s)", "Mean Period (s)"]]

    for crrt_row in range(nbr_entries):
        # get the time
        crrt_epoch_time = all_epoch_time.iloc[crrt_row].tolist()
        epoch_time = float(crrt_epoch_time)

        # get the lat lon
        crrt_lat_lon_row = all_lat_lon.iloc[crrt_row].tolist()
        lat_lon = convert_to_list_floats(crrt_lat_lon_row)

        # get the spectrum data
        crrt_freq_row = all_frequencies.iloc[crrt_row].tolist()
        crrt_wave_row = all_wave_spectrum.iloc[crrt_row].tolist()
        if crrt_freq_row == DEFAULT_EMPTY_FREQS:
            has_spectrum = False
        elif two_lists_equal_within_uncertainty(convert_to_list_floats(crrt_freq_row), DEFAULT_FREQS):
            # get the wave spectrum
            spectrum = convert_to_list_floats(crrt_wave_row)
            has_spectrum = True
        else:
            raise RuntimeError(f"unknown freq entry: {crrt_freq_row}")

        # get the wave statistics
        crrt_wave_stats = all_wave_stats.iloc[crrt_row].tolist()
        wave_stats = convert_to_list_floats(crrt_wave_stats)

        dict_crrt_row = {}

        dict_crrt_row["lat"] = lat_lon[0]
        dict_crrt_row["lon"] = lat_lon[1]
        dict_crrt_row["hs"] = wave_stats[0]
        dict_crrt_row["peak_period"] = wave_stats[1]
        dict_crrt_row["mean_period"] = wave_stats[2]

        if has_spectrum:
            dict_crrt_row["kind"] = "B"  # "both" kind
            dict_crrt_row["frequencies"] = DEFAULT_FREQS
            dict_crrt_row["spectrum"] = spectrum
        else:
            dict_crrt_row["kind"] = "S"  # "small" kind

        dict_all_data[crrt_instrument][epoch_time] = dict_crrt_row

with open("dict_all_data.pkl", "bw") as fh:
    pickle.dump(dict_all_data, fh)
