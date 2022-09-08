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

import geopy.distance

from dataclasses import dataclass


@dataclass
class GNSS_Packet:
    datetime_fix: datetime.datetime
    latitude: float
    longitude: float


# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

import pytz

utc_timezone = pytz.timezone("UTC")

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** load the data")

with open("../generate_dict_data/data_from_Martin_2018.pkl", "br") as fh:
    all_data = pickle.load(fh, encoding='latin1')

nbr_of_instruments = len(all_data)
max_nbr_of_samples = 0

for crrt_instrument in all_data:
    max_nbr_of_samples = max(max_nbr_of_samples, len(all_data[crrt_instrument]))

ic(nbr_of_instruments)
ic(max_nbr_of_samples)

# ------------------------------------------------------------------------------------------
print("***** prepare the dataset")

output_file = "data_drift_2018_March_Greenland.nc"

with nc4.Dataset(output_file, "w", format="NETCDF4") as nc4_out:
    nc4_out.set_auto_mask(False)

    # ------------------------------------------------------------
    # metadata

    nc4_out.title = "Sea ice drift from the March 2018 deployment East of Greenland."

    nc4_out.summary = \
        "The sea ice drifter trajectories from the 2018 deployment East of Greenland, performed by Biuw et. al., " +\
        "in the context of the seals pup production study 2018, generated with the code at: " +\
        "https://github.com/jerabaul29/data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022/tree/master/Data/2018_March_Greenland . " +\
        "More data may be available at this address than in this nc file. " +\
        "Please discuss any question / issue about the present data inside the issue tracker of the github repository."

    # documentation for keywords and keywords vocabulary: https://adc.met.no/node/96
    # GCMD keyword viewer: https://gcmd.earthdata.nasa.gov/KeywordViewer/scheme/Earth%20Science?gtm_scheme=Earth%20Science
    nc4_out.keywords = \
        "GCMDSK:Earth Science > Cryosphere > Sea Ice > Sea Ice Motion, " +\
        "GCMDSK:Earth Science > Oceans > Sea Ice > Sea Ice Motion, " +\
        "GCMDLOC:Geographic Region > Northern Hemisphere, " +\
        "GCMDLOC:Geographic Region > Ocean > Atlantic Ocean > North Atlantic Ocean > East Greenland Sea, " +\
        "GCMDLOC:Geographic Region > Continent > North America > Greenland, "
    nc4_out.keywords_vocabulary = \
        "GCMDSK:GCMD Science Keywords:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords, " +\
        "GCMDLOC:GCMD Locations:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations, "

    nc4_out.Conventions = "ACDD-1.3"
    nc4_out.history = "1.0: creation"

    nc4_out.source = "field measurements"

    nc4_out.date_created = "2022-07-12:00:00:Z"
    nc4_out.creator_type = "person"
    nc4_out.creator_institution = "Havforskningsinstituttet, data packaged at the Norwegian Meteorological Institute (MET)"
    nc4_out.creator_name = "data from Martin Biuw, packaged by Jean Rabault"
    nc4_out.creator_email = "jeanr@met.no"
    nc4_out.creator_url = "https://orcid.org/0000-0002-7244-6592"
    nc4_out.institution = "Havforskningsinstituttet, packaged by Norwegian Meteorological Institute (MET)"
    nc4_out.project = "Survey to assess harp and hooded seal pup production in the Greenland sea pack-ice in 2018, Havforskningsinstituttet"

    nc4_out.instrument = "GNSS"

    nc4_out.references = "Report from surveys to assess harp and hooded seal pup production in the Greenland sea pack-ice in 2018 " +\
        "Toktrapport / Havforskningsinstituttet / ISSN 15036294/ Nr. 7–2018, Biuw et. al. " +\
        "Recent Harp and Hooded Seal Pup Production Estimates in the Greenland Sea Suggest Ecology-Driven Declines, " +\
        "Biuw et. al., NAMMCO Scientific Publications, DOI: https://doi.org/10.7557/3.5821" 

    nc4_out.license = "CC-BY-4.0"

    nc4_out.publisher_type = "institution"
    nc4_out.publisher_name = "Norwegian Meteorological Institute"
    nc4_out.publisher_url = "met.no"
    nc4_out.publisher_email = "post@met.no"

    # the "waves in ice instrument" version, can be used to extract data from a variety of waves in ice files while
    # knowing which kind of data / instrument is used
    nc4_out.waves_in_ice_version = "GNSS drifter"

    # topic and activity type:
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#iso-topic-categories
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#activity-type
    nc4_out.iso_topic_category = "oceans"
    nc4_out.activity_type = "In Situ Ice-based station"

    # operational status: https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#operational-status
    nc4_out.operational_status = "Scientific"

    # ------------------------------------------------------------
    # dimensions

    # trajectory number, one per instrument
    trajectory_dim = nc4_out.createDimension("trajectory", nbr_of_instruments)

    # max number of observations per instrument
    observation_dim = nc4_out.createDimension("observation", max_nbr_of_samples)

    # since str is not supported by CF conventions, need an array of chars
    length_of_name = 16
    len_of_name_dim = nc4_out.createDimension("len_of_name", length_of_name)

    # ------------------------------------------------------------
    # variables

    trajectory_var = nc4_out.createVariable("trajectory_id", "c", ("trajectory", "len_of_name"))
    trajectory_var.standard_name = "platform_id"
    trajectory_var.long_name = "platform name"

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

    # ------------------------------------------------------------
    # filling the data in and get the "extreme bounds"

    # NOTE / TODO: this is actually where the quality controls should take place rather than lower down...

    lat_min = 90.0
    lat_max = -90.0
    lon_min = 180.0
    lon_max = -180.0
    datetime_start = datetime.datetime(2030, 1, 1, 0, 0, 0, tzinfo=utc_timezone)
    datetime_end = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=utc_timezone)

    max_datetime = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=utc_timezone)

    all_ordered_data = {}

    # generate list of all entries to use for each instrument
    for crrt_instrument in all_data:
        crrt_dict_instr = all_data[crrt_instrument]

        list_measurements = []
        for crrt_datetime in sorted(list(crrt_dict_instr.keys())):
            crrt_measurement = GNSS_Packet(
                crrt_datetime,
                crrt_dict_instr[crrt_datetime]["lat"],
                crrt_dict_instr[crrt_datetime]["lon"],
                )
            list_measurements.append(crrt_measurement)

        list_measurements_cleaned = []

        for crrt_entry, crrt_next_entry in zip(list_measurements[:-1], list_measurements[1:]):
            assert crrt_entry.datetime_fix <= crrt_next_entry.datetime_fix

            # check if the data are valid
            # this is necessary to make sure that no "gross outliers"
            data_is_valid = True

            timestamp_is_valid = crrt_entry.datetime_fix < crrt_next_entry.datetime_fix
            data_is_valid &= timestamp_is_valid

            timestamp_is_valid = crrt_next_entry.datetime_fix < max_datetime
            data_is_valid &= timestamp_is_valid

            if isinstance(crrt_next_entry, GNSS_Packet):
                position_is_valid = \
                    crrt_next_entry.latitude < 90.0 and crrt_next_entry.latitude > -90.0 and \
                    crrt_next_entry.longitude > -180.0 and crrt_next_entry.longitude < 180.0
                data_is_valid &= position_is_valid

                # TODO: check for jumps, and when jumps happen, ignore the data

            if data_is_valid:
                list_measurements_cleaned.append(crrt_next_entry)
            else:
                print("Warning; non valid entry")
                ic(crrt_instrument)
                ic(crrt_next_entry)

        for crrt_entry, crrt_next_entry in zip(list_measurements_cleaned[:-1], list_measurements_cleaned[1:]):
            assert crrt_entry.datetime_fix < crrt_next_entry.datetime_fix

        all_ordered_data[crrt_instrument] = list_measurements_cleaned

    for crrt_instrument in all_data:
        crrt_ordered_data = all_ordered_data[crrt_instrument]  # the data we need to add
        crrt_trajectory = list(all_data.keys()).index(crrt_instrument)  # the trajectory number; so that numbering fits with the index of the instrument to use

        # fill the name variable
        for crrt_ind, crrt_char in enumerate(crrt_instrument):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = crrt_char

        for crrt_ind in range(crrt_ind+1, length_of_name):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = "\0"

        for crrt_observation, crrt_data_entry in enumerate(crrt_ordered_data):
            time_var[crrt_trajectory, crrt_observation] = \
                crrt_data_entry.datetime_fix.timestamp()

            datetime_start = min(datetime_start, crrt_data_entry.datetime_fix)
            datetime_end = max(datetime_end, crrt_data_entry.datetime_fix)

            if isinstance(crrt_data_entry, GNSS_Packet):  # is it a GNSS entry?
                lon_var[crrt_trajectory, crrt_observation] = crrt_data_entry.longitude
                lat_var[crrt_trajectory, crrt_observation] = crrt_data_entry.latitude

                lat_min = min(lat_min, crrt_data_entry.latitude)
                lat_max = max(lat_max, crrt_data_entry.latitude)
                lon_min = min(lon_min, crrt_data_entry.longitude)
                lon_max = max(lon_max, crrt_data_entry.longitude)
            else:
                print(f"WARNING: unknown kind for packet: {crrt_data_entry}")
                #raise RuntimeError("unknown kind for packet: {}".format(crrt_data_entry))

    nc4_out.geospatial_lat_min = str(lat_min)
    nc4_out.geospatial_lat_max = str(lat_max)
    nc4_out.geospatial_lon_min = str(lon_min)
    nc4_out.geospatial_lon_max = str(lon_max)
    nc4_out.time_coverage_start = datetime_start.isoformat()
    nc4_out.time_coverage_end = datetime_end.isoformat()

# the end
