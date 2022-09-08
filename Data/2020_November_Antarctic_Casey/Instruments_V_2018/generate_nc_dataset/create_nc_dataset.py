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

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** using a whitelist of admissible instruments")
list_instruments = ["RockBLOCK 17328 - Antarctica-AAD",
                    "RockBLOCK 18655 - Antarctica-AAD",
                   ]
ic(list_instruments)

# ------------------------------------------------------------------------------------------
print("***** load the data")

with open("../generate_dict_data/all.pkl", "br") as fh:
    all_data = pickle.load(fh, encoding='latin1')

print("find out number of entries, number of instruments, number of entries per instrument")
list_keys_data = sorted(list(all_data.keys()))
dict_metadata = {}

for crrt_key in list_keys_data:
    crrt_entry = all_data[crrt_key]
    device = crrt_entry["Device"].split(" ")[1]
    if crrt_entry["Device"] not in list_instruments:
        print("{} not in {}: ignore".format(crrt_entry["Device"], list_instruments))
        continue
    if device not in dict_metadata:
        dict_metadata[device] = 0
    dict_metadata[device] += 1

list_nbr_entries = [dict_metadata[device] for device in dict_metadata]
list_instrument_ids = list(dict_metadata.keys())
max_nbr_of_samples = max(list_nbr_entries)
nbr_of_instruments = len(list_nbr_entries)

for crrt_key in dict_metadata:
    print("instrument with ID {} has {} entries".format(crrt_key, dict_metadata[crrt_key]))
ic(max_nbr_of_samples)
ic(nbr_of_instruments)
ic(list_instrument_ids)

# some wave frequency stuff for the instruments v2018.1
fmin = 0.05
fmax = 0.25
nfreq = 25
freq = np.exp(np.linspace(np.log(fmin), np.log(fmax), nfreq))
nbr_of_frequency_bins = len(freq)

# ------------------------------------------------------------------------------------------
print("***** prepare the dataset")

output_file = "data_waves_Antarctic_Casey_2020_10.nc"

with nc4.Dataset(output_file, "w", format="NETCDF4") as nc4_out:
    nc4_out.set_auto_mask(False)

    # ------------------------------------------------------------
    # metadata

    nc4_out.title = "Waves in ice measurements close to the Casey Antarctic station october 2020"

    nc4_out.summary = \
        "Waves in landfast ice data obtained outside of the Casey station from the Australian Antarctic Program, projects 4593 and 4506. The " +\
        "wave measurements were obtained by instruments deployed on the ice. For more information " +\
        "about the deployment, see: Voermans, J. (2021) Wave-ice interactions collected on landfast ice near Casey Station, 2020. " +\
        "Data are reproduced here, but primary hosting is taking place at https://data.aad.gov.au/metadata/records/AAS_4593_IB_2020_Casey . " +\
        "The data presented here are created, stored, and quality checked using the code available at: " +\
        "https://github.com/jerabaul29/data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022/tree/master/Data/2020_November_Antarctic_Casey . " +\
        "More data may be available at the data.aad.gov.au website and in the github repo than in this nc file. " +\
        "Please discuss any question / issue about the present data inside the issue tracker of the github repository."

    # documentation for keywords and keywords vocabulary: https://adc.met.no/node/96
    # GCMD keyword viewer: https://gcmd.earthdata.nasa.gov/KeywordViewer/scheme/Earth%20Science?gtm_scheme=Earth%20Science
    nc4_out.keywords = \
        "GCMDSK:Earth Science > Cryosphere > Sea Ice > Sea Ice Motion, " +\
        "GCMDSK:Earth Science > Oceans > Sea Ice > Sea Ice Motion, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Spectra, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Significant Wave Height, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Period, " +\
        "GCMDLOC:Geographic Region > Southern Hemisphere, " +\
        "GCMDLOC:Geographic Region > Antarctica, "
    nc4_out.keywords_vocabulary = \
        "GCMDSK:GCMD Science Keywords:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords, " +\
        "GCMDLOC:GCMD Locations:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations, "

    nc4_out.Conventions = "ACDD-1.3"
    nc4_out.history = "1.0: creation"

    nc4_out.source = "field measurements"

    nc4_out.date_created = "2021-10-11T12:00:00:Z"
    nc4_out.creator_type = "persons"
    nc4_out.creator_institution = "University of Melbourne, Norwegian Meteorological Institute (MET)"
    nc4_out.creator_name = "Joey Voermans, Jean Rabault"
    nc4_out.creator_email = "jvoermans@unimelb.edu.au, jeanr@met.no"
    nc4_out.creator_url = " https://orcid.org/0000-0002-2963-3763, https://orcid.org/0000-0002-7244-6592"
    nc4_out.institution = "University of Melbourne, Norwegian Meteorological Institute (MET)"
    nc4_out.project = "Australian Antarctic Program, projects 4593 and 4506"

    nc4_out.instrument = "GNSS, IMU, waves in ice"

    nc4_out.references = "Voermans, J. (2021) Wave-ice interactions collected on landfast ice near Casey Station, 2020, Ver. 1, Australian Antarctic Data Centre - doi:10.26179/2drt-2j12, Accessed: 2021-10-11"

    nc4_out.license = "CC-BY-4.0"

    nc4_out.publisher_type = "institution"
    nc4_out.publisher_name = "Norwegian Meteorological Institute"
    nc4_out.publisher_url = "met.no"
    nc4_out.publisher_email = "post@met.no"

    # the "waves in ice instrument" version, can be used to extract data from a variety of waves in ice files while
    # knowing which kind of data / instrument is used
    nc4_out.waves_in_ice_version = "v2018.1"

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
    swh_var.long_name = "significant wave height of sea ice surface elevation computed as 4*std(eta)"
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
    tz0_var.long_name = "period of sea ice surface elevation computed from zero upcrossing"
    tz0_var.units = "s"

    # ------------------------------------------------------------
    # filling the "meta" data in

    for crrt_ind, crrt_frequency in enumerate(freq):
        frequency_var[crrt_ind] = crrt_frequency

    # ------------------------------------------------------------
    # filling the data in and get the "extreme bounds"

    lat_min = 90.0
    lat_max = -90.0
    lon_min = 180.0
    lon_max = -180.0
    datetime_start = datetime.datetime.fromtimestamp(2e10)
    datetime_end = datetime.datetime.fromtimestamp(0)

    dict_crrt_observations = {}
    for crrt_instrument in list_instrument_ids:
        dict_crrt_observations[crrt_instrument] = 0

    for crrt_ind, crrt_entry_key in enumerate(list_keys_data):
        crrt_entry = all_data[crrt_entry_key]
        if crrt_entry['Device'] not in list_instruments:
            print("{} not in {}: jumping over".format(crrt_entry['Device'], list_instruments))
            continue
        crrt_instrument = crrt_entry['Device'].split(" ")[1]
        crrt_trajectory = list_instrument_ids.index(crrt_instrument)
        crrt_observation = dict_crrt_observations[crrt_instrument]
        dict_crrt_observations[crrt_instrument] += 1

        print("***")
        ic(crrt_ind)
        ic(crrt_entry)

        ic(crrt_instrument)
        ic(crrt_trajectory)
        ic(crrt_observation)

        # fill the name variable
        for crrt_ind, crrt_char in enumerate(crrt_instrument):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = crrt_char

        for crrt_ind in range(crrt_ind+1, length_of_name):
            nc4_out["trajectory_id"][crrt_trajectory, crrt_ind] = "\0"

        # need to check that a valid transmission
        if crrt_entry["parsed_data"] is not None:
            # the base datetime is the one of the transmission; we will refine later
            # on if this is actually a GPS message
            time_var[crrt_trajectory, crrt_observation] = \
                crrt_entry['datetime'].timestamp()

            # find the kind of data, and fill the correct data
            if crrt_entry['data_kind'] == "status":
                kind_var[crrt_trajectory, crrt_observation] = "G"

                # we actually use the correct time, not the iridium transmission time
                crrt_datetime = \
                    datetime.datetime.combine(
                        crrt_entry['parsed_data']['GPRMC_binary_payload'].datestamp,
                        crrt_entry['parsed_data']['GPRMC_binary_payload'].timestamp
                    )

                crrt_lat = crrt_entry['parsed_data']['GPRMC_binary_payload'].latitude
                crrt_lon = crrt_entry['parsed_data']['GPRMC_binary_payload'].longitude
                time_var[crrt_trajectory, crrt_observation] = crrt_datetime.timestamp()

                lon_var[crrt_trajectory, crrt_observation] = crrt_lon
                lat_var[crrt_trajectory, crrt_observation] = crrt_lat

                datetime_start = min(datetime_start, crrt_datetime)
                datetime_end = max(datetime_end, crrt_datetime)
                lat_min = min(lat_min, crrt_lat)
                lat_max = max(lat_max, crrt_lat)
                lon_min = min(lon_min, crrt_lon)
                lon_max = max(lon_max, crrt_lon)

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

    nc4_out.geospatial_lat_min = str(lat_min)
    nc4_out.geospatial_lat_max = str(lat_max)
    nc4_out.geospatial_lon_min = str(lon_min)
    nc4_out.geospatial_lon_max = str(lon_max)
    nc4_out.time_coverage_start = datetime_start.isoformat()
    nc4_out.time_coverage_end = datetime_end.isoformat()
