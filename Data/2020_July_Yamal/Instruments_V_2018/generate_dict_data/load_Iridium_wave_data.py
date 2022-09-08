"""Load iridium wave data from a binary string."""

import numpy as np
import struct


def load_data(bin_data):
    """A function to load the Iridium data.

    Returns the normalized Iridium transmitted data."""

    dict_data = {}
    dict_data["raw_data"] = {}

    # some frequency stuff
    fmin = 0.05
    fmax = 0.25
    nfreq = 25
    freq = np.exp(np.linspace(np.log(fmin), np.log(fmax), nfreq))

    # some format stuff
    fmt_all = '<' + 'f' * 10 + 'h' * nfreq * 6

    data = struct.unpack(fmt_all, bin_data)

    # extract the data
    SWH = data[0]
    T_z0 = data[1]
    Hs = data[2]
    T_z = data[3]
    a0_max = data[4]
    a1_max = data[5]
    b1_max = data[6]
    a2_max = data[7]
    b2_max = data[8]
    R_max = data[9]
    a0 = np.array(data[10:35])
    a1 = np.array(data[35:60])
    b1 = np.array(data[60:85])
    a2 = np.array(data[85:110])
    b2 = np.array(data[110:135])
    R = np.array(data[135:160])

    max_val = 2**15 - 1.0

    a0_proc = a0 * a0_max / max_val
    a1_proc = a1 * a1_max / max_val
    b1_proc = b1 * b1_max / max_val
    a2_proc = a2 * a2_max / max_val
    b2_proc = b2 * b2_max / max_val
    R_proc = R * R_max / max_val

    dict_data["raw_data"]["SWH"] = SWH
    dict_data["raw_data"]["T_z0"] = T_z0
    dict_data["raw_data"]["Hs"] = Hs
    dict_data["raw_data"]["T_z"] = T_z
    dict_data["raw_data"]["freq"] = freq
    dict_data["raw_data"]["fmin"] = fmin
    dict_data["raw_data"]["fmax"] = fmax
    dict_data["raw_data"]["nfreq"] = nfreq
    dict_data["raw_data"]["a0_proc"] = a0_proc
    dict_data["raw_data"]["a1_proc"] = a1_proc
    dict_data["raw_data"]["a2_proc"] = a2_proc
    dict_data["raw_data"]["b1_proc"] = b1_proc
    dict_data["raw_data"]["b2_proc"] = b2_proc
    dict_data["raw_data"]["R_proc"] = R_proc

    return(dict_data)


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
