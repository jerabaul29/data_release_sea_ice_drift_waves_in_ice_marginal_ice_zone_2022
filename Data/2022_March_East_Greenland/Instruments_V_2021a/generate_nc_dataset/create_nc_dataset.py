"""
This is putting the data together into a nc format for doi release.

Since a lot of this is metadata etc, do a bit of boilerplate, and
write one such create file for each deployment. That means that if
one file needs fixing, all files need fixing most likely...

That means a bit of code duplication though...
"""

# NOTE: this is a really ugly script and full of hacks
# the main reason for that is that the prototype instruments
# went through quite a few glitches and issues...
# when writing some "nice" file for analyzing the instruments v2021
# in the future, start again from a clean sheet!

import os
import time

from icecream import ic

import pickle

import netCDF4 as nc4

import datetime
import numpy as np

from decoder import Waves_Packet
from decoder import GNSS_Packet as GNSS_Packet_bin

import geopy.distance

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** using a whitelist of admissible instruments for spectra information")
list_instruments_use_spectra = ["2022_seal1",
                                "2022_seal3",
                                ]
ic(list_instruments_use_spectra)

# ------------------------------------------------------------------------------------------
print("***** using a list of rejected measurements because of faulty quality")
dict_faulty_measurements = {
}
ic(dict_faulty_measurements)

# ------------------------------------------------------------------------------------------
print("***** load the data")

with open("../generate_dict_data/dict_all_data.pkl", "br") as fh:
    all_data = pickle.load(fh, encoding='latin1')

print("find out number of entries, number of instruments, number of entries per instrument")
list_keys_data = sorted(list(all_data.keys()))
dict_metadata = {}

list_instruments_to_use = []

for device in list_keys_data:
    crrt_entry = all_data[device]
    dict_metadata[device] = len(crrt_entry["gnss_fixes"]) + len(crrt_entry["spectra"])
    if dict_metadata[device] > 30:
        list_instruments_to_use.append(device)

list_nbr_entries = [dict_metadata[device] for device in dict_metadata]
max_nbr_of_samples = max(list_nbr_entries)
nbr_of_instruments = len(list_instruments_to_use)

ic(max_nbr_of_samples)
ic(nbr_of_instruments)
ic(list_instruments_to_use)

# some wave frequency stuff for the instrument v2021.a
# note that we only use the instruments with a fftlen of 2048
list_frequencies = all_data["2022_seal1"]["spectra"][0].list_frequencies
nbr_of_frequency_bins = len(list_frequencies)

# ------------------------------------------------------------------------------------------
print("***** prepare the dataset")

output_file = "data_drift_waves_Greenland_2022_seals_cruise.nc"

# TODO under: update metadata

with nc4.Dataset(output_file, "w", format="NETCDF4") as nc4_out:
    nc4_out.set_auto_mask(False)

    # ------------------------------------------------------------
    # metadata

    nc4_out.title = "Sea ice drift and wave measurements from the 'seal cruise', 2022"

    nc4_out.summary = \
        "The sea ice drifter trajectories and wave measurements from the 'seal cruise' 2022, 'SURVEYS TO ASSESS HARP AND HOODED SEAL PUP PRODUCTION IN THE GREENLAND SEA PACK-ICE'. The " +\
        "trajectories and wave measurements were obtained by instruments OpenMetBuoy v2021-a deployed on the ice. For more information " +\
        "about the deployment, see: (XX: add: the report is not yet published). " +\
        "The data are created, stored, and quality checked using the code available at: " +\
        "https://github.com/jerabaul29/data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022/tree/master/Data/2022_March_East_Greenland/Instruments_V_2021a/generate_dict_data . " +\
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
        "GCMDLOC:Geographic Region > Northern Hemisphere, " +\
        "GCMDLOC:Geographic Region > Ocean > Atlantic Ocean > North Atlantic Ocean > East Greenland Sea, " +\
        "GCMDLOC:Geographic Region > Continent > North America > Greenland"
    nc4_out.keywords_vocabulary = \
        "GCMDSK:GCMD Science Keywords:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords, " +\
        "GCMDLOC:GCMD Locations:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations, "

    nc4_out.Conventions = "ACDD-1.3"
    nc4_out.history = "1.0: creation"

    nc4_out.source = "field measurements"

    nc4_out.date_created = "2022-05-10:00:00:Z"
    nc4_out.creator_type = "person"
    nc4_out.creator_institution = "Norwegian Meteorological Institute (MET)"
    nc4_out.creator_name = "Jean Rabault"
    nc4_out.creator_email = "jeanr@met.no"
    nc4_out.creator_url = "https://orcid.org/0000-0002-7244-6592"
    nc4_out.institution = "Norwegian Meteorological Institute (MET)"
    nc4_out.project = "Arven etter Nansen, Nansen Legacy Project, Dynamics of Floating ice, Institute for Marine research: SURVEYS TO ASSESS HARP AND HOODED SEAL PUP PRODUCTION IN THE GREENLAND SEA PACK-ICE IN 2022"

    nc4_out.instrument = "GNSS, IMU, waves in ice"

    nc4_out.references = "XX: report about cruise: not published yet "

    nc4_out.license = "CC-BY-4.0"

    nc4_out.publisher_type = "institution"
    nc4_out.publisher_name = "Norwegian Meteorological Institute"
    nc4_out.publisher_url = "met.no"
    nc4_out.publisher_email = "post@met.no"

    # the "waves in ice instrument" version, can be used to extract data from a variety of waves in ice files while
    # knowing which kind of data / instrument is used
    nc4_out.waves_in_ice_version = "v2021.a"

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
    kind_var.long_name = "whether the current [trajectory, observation] contains GPS [kind G]" +\
        ", or Waves [kind W], or None [kind N, in case of failed transmission] " +\
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

    swh_var = nc4_out.createVariable("swh", "f4", ("trajectory", "observation"))
    swh_var.standard_name = "sea_surface_swell_wave_significant_height"
    swh_var.long_name = "significant wave height of sea ice surface elevation computed as 4*std(eta) [not available for this instrument]"
    swh_var.units = "m"

    hs_var = nc4_out.createVariable("hs", "f4", ("trajectory", "observation"))
    hs_var.standard_name = "sea_surface_swell_wave_significant_height"
    hs_var.long_name = "significant wave height of sea ice surface elevation computed as 4*sqrt(m0)"
    hs_var.units = "m"

    tz_var = nc4_out.createVariable("tp", "f4", ("trajectory", "observation"))
    tz_var.standard_name = "sea_surface_swell_wave_period"
    tz_var.long_name = "period of sea ice surface elevation computed as sqrt(m0/m2)"
    tz_var.units = "s"

    tz0_var = nc4_out.createVariable("tz0", "f4", ("trajectory", "observation"))
    tz0_var.standard_name = "sea_surface_swell_wave_zero_upcrossing_period"
    tz0_var.long_name = "period of sea ice surface elevation computed from zero upcrossing [not available for this instrument]"
    tz0_var.units = "s"

    # ------------------------------------------------------------
    # filling the "meta" data in

    for crrt_ind, crrt_frequency in enumerate(list_frequencies):
        frequency_var[crrt_ind] = crrt_frequency

    # ------------------------------------------------------------
    # filling the data in and get the "extreme bounds"

    # NOTE / TODO: this is actually where the quality controls should take place rather than lower down...

    # clean the bad GNSS measurements

    for crrt_instrument in list_instruments_to_use:
        all_gnss_measurements = all_data[crrt_instrument]["gnss_fixes"]
        good_gnss_measurements = []
        list_already_met_coords = []
        for crrt_middle_ind in range(1, len(all_gnss_measurements)-2):
            try:
                crrt_gnss_measurement = all_gnss_measurements[crrt_middle_ind]
                next_gnss_measurement = all_gnss_measurements[crrt_middle_ind+1]
                previous_gnss_measurement = all_gnss_measurements[crrt_middle_ind-1]

                crrt_coords = (crrt_gnss_measurement.latitude, crrt_gnss_measurement.longitude)

                if crrt_coords in list_already_met_coords:
                    continue
                else:
                    list_already_met_coords.append(crrt_coords)

                next_coords = (next_gnss_measurement.latitude, next_gnss_measurement.longitude)
                previous_coords = (previous_gnss_measurement.latitude, previous_gnss_measurement.longitude)

                distance_to_previous = geopy.distance.geodesic(crrt_coords, previous_coords).km
                distance_to_next = geopy.distance.geodesic(crrt_coords, next_coords).km
                distance_previous_next = geopy.distance.geodesic(previous_coords, next_coords).km

                is_good = True

                # remove the worst outliers: cannot move more than a few km even with some dropouts!
                if distance_to_previous > 25.0 or distance_to_next > 25.0:
                    is_good = False

                # remove the middle bad outliers: further away from the middle of the previous and next point by more than the distance between previous and next
                if distance_previous_next < distance_to_previous and distance_previous_next < distance_to_next:
                    is_good = False

                if is_good:
                    good_gnss_measurements.append(crrt_gnss_measurement)

            except:
                pass

        all_data[crrt_instrument]["gnss_fixes"] = good_gnss_measurements


    lat_min = 90.0
    lat_max = -90.0
    lon_min = 180.0
    lon_max = -180.0
    datetime_start = datetime.datetime.fromtimestamp(2e10)
    datetime_end = datetime.datetime.fromtimestamp(0)

    max_datetime = datetime.datetime(2023, 1, 1, 0, 0, 0)

    all_ordered_data = {}

    # generate list of all entries to use for each instrument
    for crrt_instrument in list_instruments_to_use:
        ic(crrt_instrument)
        if crrt_instrument not in list_instruments_use_spectra:  # is it only a GPS instrument?
            print("is a GNSS only instrument")
            list_measurements_gnss = all_data[crrt_instrument]["gnss_fixes"]
            list_measurements_spectra = []
            list_measurements = list_measurements_gnss

        else:  # or does it also have waves data (in which case, need to fusion both lists of measurements)
            print("has both GNSS and Waves data")
            list_measurements_gnss = all_data[crrt_instrument]["gnss_fixes"]
            list_measurements_spectra = all_data[crrt_instrument]["spectra"]
            list_measurements = []

            index_gnss = 0
            index_spectra = 0

            while (index_gnss < len(list_measurements_gnss) or index_spectra < len(list_measurements_spectra)):
                if index_gnss == len(list_measurements_gnss):  # do we have only spectra left?
                    list_measurements.append(list_measurements_spectra[index_spectra])
                    index_spectra += 1

                elif index_spectra == len(list_measurements_spectra):  # do we have only gnss left?
                    list_measurements.append(list_measurements_gnss[index_gnss])
                    index_gnss += 1

                else:  # if we have both left, we need to check which to add next
                    if list_measurements_spectra[index_spectra].datetime_fix < \
                            list_measurements_gnss[index_gnss].datetime_fix:  # is the next measurement a spectrum?
                        list_measurements.append(list_measurements_spectra[index_spectra])
                        index_spectra += 1
                    else:  # or is it a gnss measurement?
                        list_measurements.append(list_measurements_gnss[index_gnss])
                        index_gnss += 1

        list_measurements_cleaned = []
        # list_measurements_cleaned.append(list_measurements[0])

        for crrt_entry, crrt_next_entry in zip(list_measurements[:-1], list_measurements[1:]):
            assert crrt_entry.datetime_fix <= crrt_next_entry.datetime_fix

            # check if the data are valid
            # this is necessary to make sure that no "gross outliers"
            data_is_valid = True

            timestamp_is_valid = crrt_entry.datetime_fix < crrt_next_entry.datetime_fix
            data_is_valid &= timestamp_is_valid

            timestamp_is_valid = crrt_next_entry.datetime_fix < max_datetime
            data_is_valid &= timestamp_is_valid

            if isinstance(crrt_next_entry, GNSS_Packet_bin):
                position_is_valid = \
                    crrt_next_entry.latitude < 90.0 and crrt_next_entry.latitude > -90.0 and \
                    crrt_next_entry.longitude > -180.0 and crrt_next_entry.longitude < 180.0
                data_is_valid &= position_is_valid

                # TODO: check for jumps, and when jumps happen, ignore the data

            if isinstance(crrt_next_entry, Waves_Packet):
                datetime_is_valid = True
                data_is_valid &= datetime_is_valid

                if crrt_instrument in dict_faulty_measurements:
                    for crrt_faulty_measurement in dict_faulty_measurements[crrt_instrument]:
                        if crrt_faulty_measurement - crrt_next_entry.datetime_fix < datetime.timedelta(seconds=30*60):
                            data_is_valid = False

            if data_is_valid:
                list_measurements_cleaned.append(crrt_next_entry)
            else:
                print("Warning; non valid entry")
                ic(crrt_instrument)
                ic(crrt_next_entry)

        for crrt_entry, crrt_next_entry in zip(list_measurements_cleaned[:-1], list_measurements_cleaned[1:]):
            assert crrt_entry.datetime_fix < crrt_next_entry.datetime_fix

        all_ordered_data[crrt_instrument] = list_measurements_cleaned

    for crrt_instrument in list_instruments_to_use:
        crrt_ordered_data = all_ordered_data[crrt_instrument]  # the data we need to add
        crrt_trajectory = list_instruments_to_use.index(crrt_instrument)  # the trajectory number; so that numbering fits with the index of the instrument to use

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

            if isinstance(crrt_data_entry, GNSS_Packet_bin):  # is it a GNSS entry?
                kind_var[crrt_trajectory, crrt_observation] = "G"
                lon_var[crrt_trajectory, crrt_observation] = crrt_data_entry.longitude
                lat_var[crrt_trajectory, crrt_observation] = crrt_data_entry.latitude

                lat_min = min(lat_min, crrt_data_entry.latitude)
                lat_max = max(lat_max, crrt_data_entry.latitude)
                lon_min = min(lon_min, crrt_data_entry.longitude)
                lon_max = max(lon_max, crrt_data_entry.longitude)
            elif isinstance(crrt_data_entry, Waves_Packet):  # is it a waves packet?
                kind_var[crrt_trajectory, crrt_observation] = "W"
                for crrt_ind_spectrum, crrt_energy_entry in enumerate(crrt_data_entry.list_elevation_energies):
                    spectrum_var[crrt_trajectory, crrt_observation, crrt_ind_spectrum] = crrt_energy_entry
                hs_var[crrt_trajectory, crrt_observation] = crrt_data_entry.Hs
                tz_var[crrt_trajectory, crrt_observation] = crrt_data_entry.Tz
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
