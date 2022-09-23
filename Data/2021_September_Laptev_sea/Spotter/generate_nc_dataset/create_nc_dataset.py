"""
This is putting the data together into a nc format for doi release.

Since a lot of this is metadata etc, do a bit of boilerplate, and
write one such create file for each deployment. That means that if
one file needs fixing, all files need fixing most likely...

That means a bit of code duplication though...
"""

import os
import time

from icecream import ic

import pickle

import netCDF4 as nc4

import datetime
import numpy as np

DEFAULT_FREQS = [0.0293, 0.03906, 0.04883, 0.058589999999999996, 0.06836, 0.07812999999999999, 0.08789, 0.09766, 0.10742, 0.11719, 0.12695, 0.13672, 0.14648, 0.15625, 0.16602, 0.17578, 0.18555, 0.19530999999999998, 0.20508, 0.21484, 0.22461, 0.23438, 0.24414, 0.25390999999999997, 0.26366999999999996, 0.27344, 0.2832, 0.29297, 0.30273, 0.3125, 0.32227, 0.33203, 0.35156, 0.38086, 0.41016, 0.43945, 0.46875, 0.49805, 0.6543]
nbr_of_frequency_bins = len(DEFAULT_FREQS)

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** load the data")

with open("../generate_dict_data/dict_all_data.pkl", "br") as fh:
    all_data = pickle.load(fh, encoding='latin1')

print("find out number of entries, number of instruments, number of entries per instrument")
dict_metadata = {}
list_instruments = sorted(list(all_data.keys()))
nbr_instruments = len(list_instruments)
max_nbr_of_samples = 0

for crrt_instrument in list_instruments:
    dict_metadata[crrt_instrument] = {}
    ic(crrt_instrument)
    list_timestamps = sorted(list(all_data[crrt_instrument].keys()))
    dict_metadata[crrt_instrument]["timestamps"] = list_timestamps
    nbr_timestamps = len(list_timestamps)
    ic(nbr_timestamps)
    max_nbr_of_samples = max(max_nbr_of_samples, nbr_timestamps)

for crrt_key in dict_metadata:
    print("instrument with ID {} has {} entries".format(crrt_key, len(dict_metadata[crrt_key]["timestamps"])))
ic(max_nbr_of_samples)
ic(nbr_instruments)

# ------------------------------------------------------------------------------------------
print("***** prepare the dataset")

output_file = "data_Spotter_Laptev_2021.nc"

with nc4.Dataset(output_file, "w", format="NETCDF4") as nc4_out:
    nc4_out.set_auto_mask(False)

    # ------------------------------------------------------------
    # metadata

    nc4_out.title = "Sea ice drift and wave measurements from the NABOS Laptev sea cruise, 2021, using the Spotter"

    nc4_out.summary = \
        "The sea ice drifter trajectories and wave measurements from the Laptev sea cruise, 2021, performed in the context of the NABOS project. " +\
        "Trajectories and wave measurements in this file were obtained by instruments a Sofar Spotter deployed on the ice. For more information " +\
        "about the deployment, see: (XX: add: the paper is not yet published). " +\
        "The data are created, stored, and quality checked using the code available at: " +\
        "https://github.com/jerabaul29/data_release_waves_in_ice_2018_2021/tree/main/Data/2021_September_Laptev_sea/Spotter . " +\
        "More data may be available at this address than in this nc file. " +\
        "Please discuss any question / issue about the present data inside the issue tracker of the github repository."

    # documentation for keywords and keywords vocabulary: https://adc.met.no/node/96
    # GCMD keyword viewer: https://gcmd.earthdata.nasa.gov/KeywordViewer/scheme/Earth%20Science?gtm_scheme=Earth%20Science
    nc4_out.keywords = \
        "GCMDSK:Earth Science > Cryosphere > Sea Ice > Sea Ice Motion, " +\
        "GCMDSK:Earth Science > Oceans > Sea Ice > Sea Ice Motion, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Spectra, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Significant Wave Height, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Period, " +\
        "GCMDLOC:Geographic Region > Ocean > Arctic Ocean, "
    nc4_out.keywords_vocabulary = \
        "GCMDSK:GCMD Science Keywords:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords, " +\
        "GCMDLOC:GCMD Locations:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations, "

    nc4_out.Conventions = "ACDD-1.3"
    nc4_out.history = "1.0: creation"

    nc4_out.source = "field measurements"

    nc4_out.date_created = "2022-08-24T12:00:00:Z"
    nc4_out.creator_type = "persons"
    nc4_out.creator_institution = "University of Tokyo, Norwegian Meteorological Institute (MET)"
    nc4_out.creator_name = "Takehiko Nose, Jean Rabault"
    nc4_out.creator_email = "jeanr@met.no"
    nc4_out.creator_url = " https://orcid.org/0000-0002-7244-6592"
    nc4_out.institution = "University of Tokyo, Norwegian Meteorological Institute (MET)"
    nc4_out.project = "Arctic Challenge for Sustainability II (ArCS II) Project (Program Grant Number JPMXD1420318865), JSPS KAKENHI Grant Numbers JP 19H00801, 19H05512, 21K14357, and 22H00241, Arven etter Nansen, Nansen Legacy Project"

    nc4_out.instrument = "GNSS, differential GPS, waves in ice"

    nc4_out.references = "XX: todo: add when paper published"

    nc4_out.license = "CC-BY-4.0"

    nc4_out.publisher_type = "institution"
    nc4_out.publisher_name = "Norwegian Meteorological Institute"
    nc4_out.publisher_url = "met.no"
    nc4_out.publisher_email = "post@met.no"

    # the "waves in ice instrument" version, can be used to extract data from a variety of waves in ice files while
    # knowing which kind of data / instrument is used
    nc4_out.waves_in_ice_version = "Sofar Spotter"

    # topic and activity type:
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#iso-topic-categories
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#activity-type
    nc4_out.iso_topic_category = "oceans"
    nc4_out.activity_type = "In Situ Ice-based station"

    # operational status: https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#operational-status
    nc4_out.operational_status = "Scientific"

    # feature type:
    nc4_out.featureType = "trajectory"
    
    # ------------------------------------------------------------
    # dimensions

    # trajectory number, one per instrument
    trajectory_dim = nc4_out.createDimension("trajectory", nbr_instruments)

    # max number of observations per instrument
    observation_dim = nc4_out.createDimension("observation", max_nbr_of_samples)

    # since str is not supported by CF conventions, need an array of chars
    length_of_name = 16
    len_of_name_dim = nc4_out.createDimension("len_of_name", length_of_name)

    # nbr of frequency bins per spectrum
    frequency_dim = nc4_out.createDimension("frequency", nbr_of_frequency_bins)

    # ------------------------------------------------------------
    # variables

    # --------------------
    # "metadata" variables

    # the frequency base used for the spectra
    frequency_var = nc4_out.createVariable("frequency", "f4", ("frequency"))
    frequency_var.long_name = "frequency bins of the spectra"
    frequency_var.units = "s-1"

    # --------------------
    # instrument names
    trajectory_var = nc4_out.createVariable("trajectory_id", "c", ("trajectory", "len_of_name"))
    trajectory_var.standard_name = "platform_id"
    trajectory_var.long_name = "platform name"

    # --------------------
    # time and kind of message variables

    # the kind of each entry: 'G' for GPS entry, 'W' for wave spectrum entry, 'N' for no entry
    kind_var = nc4_out.createVariable("message_kind", "c", ("trajectory", "observation"))
    kind_var.long_name = "whether the current [trajectory, observation] is a 'small' packet with GPS and wave stats [kind S]" +\
        ", or both GNSS, wave stats, and wave spectra [kind B], or None [kind N, in case of failed transmission] " +\
        "data."

    time_var = nc4_out.createVariable("time", "f8", ("trajectory", "observation"))
    time_var.standard_name = "time"
    time_var.long_name = "time"
    time_var.units = "seconds since 1970-01-01 00:00:00 +0000"

    # --------------------
    # geographic location variables

    lon_var = nc4_out.createVariable("lon", "f4", ("trajectory", "observation"))
    lon_var.standard_name = "longitude"
    lon_var.long_name = "longitude"
    lon_var.units = "degrees_east"

    lat_var = nc4_out.createVariable("lat", "f4", ("trajectory", "observation"))
    lat_var.standard_name = "latitude"
    lat_var.long_name = "latitude"
    lat_var.units = "degrees_north"

    # --------------------
    # wave information variables

    spectrum_var = nc4_out.createVariable("wave_spectrum", "f4", ("trajectory", "observation", "frequency"))
    spectrum_var.long_name = "under sampled wave spectrum S of the sea ice surface elevation"
    spectrum_var.units = "m2.s"

    hs_var = nc4_out.createVariable("hs", "f4", ("trajectory", "observation"))
    hs_var.standard_name = "sea_surface_swell_wave_significant_height"
    hs_var.long_name = "significant wave height of sea ice surface elevation computed as 4*sqrt(m0)"
    hs_var.units = "m"

    tp_var = nc4_out.createVariable("tp", "f4", ("trajectory", "observation"))
    tp_var.standard_name = "sea_surface_swell_wave_period"
    tp_var.long_name = "period of sea ice surface elevation computed as sqrt(m0/m2)"
    tp_var.units = "s"

    tm_var = nc4_out.createVariable("tm", "f4", ("trajectory", "observation"))
    tm_var.standard_name = "sea_surface_swell_wave_peak_period"
    tm_var.long_name = "peak period of sea ice surface elevation"
    tm_var.units = "s"

    # ------------------------------------------------------------
    # filling the "meta" data in

    for crrt_ind, crrt_frequency in enumerate(DEFAULT_FREQS):
        frequency_var[crrt_ind] = crrt_frequency

    # ------------------------------------------------------------
    # filling the data in and get the "extreme bounds"

    lat_min = 90.0
    lat_max = -90.0
    lon_min = 180.0
    lon_max = -180.0
    datetime_start = datetime.datetime.fromtimestamp(2e10)
    datetime_end = datetime.datetime.fromtimestamp(0)

    for crrt_trajectory, crrt_instrument in enumerate(list_instruments):

        # fill the name variable
        for crrt_ind, crrt_char in enumerate(crrt_instrument):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = crrt_char
        for crrt_ind in range(crrt_ind+1, length_of_name):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = "\0"

        # fill in all observations
        for crrt_observation, crrt_timestamp in enumerate(dict_metadata[crrt_instrument]["timestamps"]):

            crrt_entry = all_data[crrt_instrument][crrt_timestamp]

            print("***")
            ic(crrt_trajectory)
            ic(crrt_instrument)
            ic(crrt_observation)
            ic(crrt_timestamp)
            ic(crrt_entry)

            crrt_datetime = datetime.datetime.fromtimestamp(crrt_timestamp)
            crrt_lat = crrt_entry["lat"]
            crrt_lon = crrt_entry["lon"]

            time_var[crrt_trajectory, crrt_observation] = crrt_timestamp
            lon_var[crrt_trajectory, crrt_observation] = crrt_lon
            lat_var[crrt_trajectory, crrt_observation] = crrt_lat

            datetime_start = min(datetime_start, crrt_datetime)
            datetime_end = max(datetime_end, crrt_datetime)
            lat_min = min(lat_min, crrt_lat)
            lat_max = max(lat_max, crrt_lat)
            lon_min = min(lon_min, crrt_lon)
            lon_max = max(lon_max, crrt_lon)

            hs_var[crrt_trajectory, crrt_observation] = crrt_entry["hs"]
            tp_var[crrt_trajectory, crrt_observation] = crrt_entry["mean_period"]
            tm_var[crrt_trajectory, crrt_observation] = crrt_entry["peak_period"]

            # if both, put also the spectrum
            if crrt_entry["kind"] == "B":
                kind_var[crrt_trajectory, crrt_observation] = "B"
                for crrt_frq_ind in range(nbr_of_frequency_bins):
                    spectrum_var[crrt_trajectory, crrt_observation, crrt_frq_ind] = crrt_entry["spectrum"][crrt_frq_ind]
            elif crrt_entry["kind"] == "S":
                kind_var[crrt_trajectory, crrt_observation] = "S"
            else:
                raise RuntimeError(f"got entry kind {crrt_entry['kind']}, not a valid entry")

        """
        # need to check that a valid transmission
        if crrt_entry["parsed_data"] is not None:
            # the base datetime is the one of the transmission; we will refine later
            # on if this is actually a GPS message
            time_var[crrt_trajectory, crrt_observation] = \
                crrt_entry['datetime'].timestamp()

            # find the kind of data, and fill the correct data
            if crrt_entry['data_kind'] == "status":
                kind_var[crrt_trajectory, crrt_observation] = "G"

            elif crrt_entry['data_kind'] == "spectrum":
                kind_var[crrt_trajectory, crrt_observation] = "W"

                # no need to rewrite the time_var, we will not get better estimate
                # than iridium date

                for crrt_ind_spectrum, crrt_freq_entry in enumerate(crrt_entry['parsed_data']['raw_data']['a0_proc']):
                    spectrum_var[crrt_trajectory, crrt_observation, crrt_ind_spectrum] = crrt_freq_entry
                swh_var[crrt_trajectory, crrt_observation] = crrt_entry['parsed_data']['raw_data']['SWH']
                hs_var[crrt_trajectory, crrt_observation] = crrt_entry['parsed_data']['raw_data']['Hs']
                tz_var[crrt_trajectory, crrt_observation] = crrt_entry['parsed_data']['raw_data']['T_z']
                tz0_var[crrt_trajectory, crrt_observation] = crrt_entry['parsed_data']['raw_data']['T_z0']

            else:
                raise RuntimeError("unknown data_kind: {}".format(crrt_entry['data_kind']))

        else:
            kind_var[crrt_trajectory, crrt_observation] = "N"
    """

    nc4_out.geospatial_lat_min = str(lat_min)
    nc4_out.geospatial_lat_max = str(lat_max)
    nc4_out.geospatial_lon_min = str(lon_min)
    nc4_out.geospatial_lon_max = str(lon_max)
    nc4_out.time_coverage_start = datetime_start.isoformat()
    nc4_out.time_coverage_end = datetime_end.isoformat()
