import os
import time

from icecream import ic

import pickle

import netCDF4 as nc4

import datetime

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** Load the data")

with open("../generate_dict_data/dict_pkl_data.pkl", "br") as fh:
    dict_observations = pickle.load(fh)

# a few params for dumping, some of them hard coded values for simplicity
number_of_valid_measurements = 10

# ------------------------------------------------------------------------------------------
print("***** prepare the dataset")

output_file = "data_boat_wave_ultrasound_probes_Barents_2018.nc"

with nc4.Dataset(output_file, "w", format="NETCDF4") as nc4_out:
    nc4_out.set_auto_mask(False)

    # ------------------------------------------------------------
    # metadata

    nc4_out.title = "Ultrasound altimeter-based measurements of waves from the Nansen Legacy Physical Process Cruise 2018"

    nc4_out.summary = \
        "The wave measurements using ship-based ultrasound anemometer and IMU from the Nansen Legacy Physical Processes Cruise 2018. The " +\
        "trajectories are from the boat navigation system. Wave measurements are from a custom ultrasound altimeter and IMU system. For more information " +\
        "about the deployment, see: Fer, Ilker, et al. Physical Process Cruise 2018. The Nansen Legacy Report Series 2. " +\
        "The data are created, stored, and quality checked using the code available at: " +\
        "https://github.com/jerabaul29/data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022/tree/master/Data/2018_September_Barents/UG_Probe . " +\
        "More data may be available at this address than in this nc file. " +\
        "The instruments are based on the design from Løken, Trygve K., et al. 'Wave measurements from ship mounted sensors in the Arctic marginal ice zone.' " +\
        "Cold Regions Science and Technology 182 (2021): 103207. " +\
        "Please discuss any question / issue about the present data inside the issue tracker of the github repository. " +\
        "This dataset is organized around the idea of 'measurement segments'. Each measurement segment is a time interval " +\
        "during which the boat was immobile in the ice, and when data were collected and quality controlled."

    # documentation for keywords and keywords vocabulary: https://adc.met.no/node/96
    # GCMD keyword viewer: https://gcmd.earthdata.nasa.gov/KeywordViewer/scheme/Earth%20Science?gtm_scheme=Earth%20Science
    nc4_out.keywords = \
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Spectra, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Significant Wave Height, " +\
        "GCMDSK:Earth Science > Oceans > Ocean Waves > Wave Period, " +\
        "GCMDLOC:Geographic Region > Northern Hemisphere, " +\
        "GCMDLOC:Geographic Region > Svalbard And Jan Mayen, " +\
        "GCMDLOC:Geographic Region > Barents Sea, "
    nc4_out.keywords_vocabulary = \
        "GCMDSK:GCMD Science Keywords:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords, " +\
        "GCMDLOC:GCMD Locations:https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations, "

    nc4_out.Conventions = "ACDD-1.3"
    nc4_out.history = "1.0: creation"

    nc4_out.source = "field measurements"

    nc4_out.date_created = "2021-10-5:00:00:Z"
    nc4_out.creator_type = "person"
    nc4_out.creator_institution = "Norwegian Meteorological Institute (MET)"
    nc4_out.creator_name = "Jean Rabault"
    nc4_out.creator_email = "jeanr@met.no"
    nc4_out.creator_url = "https://orcid.org/0000-0002-7244-6592"
    nc4_out.institution = "Norwegian Meteorological Institute (MET)"
    nc4_out.project = "Arven etter Nansen, Nansen Legacy Project, Dynamics of Floating ice"

    nc4_out.instrument = "GNSS, ultrasound altimeter, inertial motion unit, waves in ice"

    nc4_out.references = "Løken, Trygve K., et al. 'Wave measurements from ship mounted sensors in the Arctic marginal ice zone, " +\
        "Fer, Ilker, et al. Physical Process Cruise 2018. The Nansen Legacy Report Series 2"

    nc4_out.license = "CC-BY-4.0"

    nc4_out.publisher_type = "institution"
    nc4_out.publisher_name = "Norwegian Meteorological Institute"
    nc4_out.publisher_url = "met.no"
    nc4_out.publisher_email = "post@met.no"

    # topic and activity type:
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#iso-topic-categories
    # https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#activity-type
    nc4_out.iso_topic_category = "oceans"
    nc4_out.activity_type = "In Situ Ice-based station"

    # operational status: https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html#operational-status
    nc4_out.operational_status = "Scientific"

    # ------------------------------------------------------------
    # dimensions

    # measurement segment, one per time interval when we are able to take a good time series in the ice
    measurement_segment_dim = nc4_out.createDimension("measurement_segment", number_of_valid_measurements)

    # ------------------------------------------------------------
    # variables

    # --------------------
    # time of start and end of measurement segment
    time_start_segment_var = nc4_out.createVariable("time_start_segment", "f8", ("measurement_segment"))
    time_start_segment_var.standard_name = "time"
    time_start_segment_var.long_name = "time start of measurement segment"
    time_start_segment_var.units = "seconds since 1970-01-01 00:00:00 +0000"

    time_end_segment_var = nc4_out.createVariable("time_end_segment", "f8", ("measurement_segment"))
    time_end_segment_var.standard_name = "time"
    time_end_segment_var.long_name = "time end of measurement segment"
    time_end_segment_var.units = "seconds since 1970-01-01 00:00:00 +0000"

    # --------------------
    # latitude and longitude of start and end of measurement segment

    lat_start_segment_var = nc4_out.createVariable("lat_start_segment", "f4", ("measurement_segment"))
    lat_start_segment_var.standard_name = "latitude"
    lat_start_segment_var.long_name = "latitude at start of measurement segment"
    lat_start_segment_var.units = "degrees_north"

    lat_end_segment_var = nc4_out.createVariable("lat_end_segment", "f4", ("measurement_segment"))
    lat_end_segment_var.standard_name = "latitude"
    lat_end_segment_var.long_name = "latitude at end of measurement segment"
    lat_end_segment_var.units = "degrees_north"

    lon_start_segment_var = nc4_out.createVariable("lon_start_segment", "f4", ("measurement_segment"))
    lon_start_segment_var.standard_name = "longitude"
    lon_start_segment_var.long_name = "longitude at start of measurement segment"
    lon_start_segment_var.units = "degrees_east"

    lon_end_segment_var = nc4_out.createVariable("lon_end_segment", "f4", ("measurement_segment"))
    lon_end_segment_var.standard_name = "longitude"
    lon_end_segment_var.long_name = "longitude at end of measurement segment"
    lon_end_segment_var.units = "degrees_east"

    # --------------------
    # scalar statistics of measurement segment: Hs, SWH, Tz, Tp

    hs_var = nc4_out.createVariable("hs", "f4", ("measurement_segment"))
    hs_var.standard_name = "sea_surface_swell_wave_significant_height"
    hs_var.long_name = "significant wave height of sea ice surface elevation computed as 4*sqrt(m0)"
    hs_var.units = "m"

    swh_var = nc4_out.createVariable("swh", "f4", ("measurement_segment"))
    swh_var.standard_name = "sea_surface_swell_wave_significant_height"
    swh_var.long_name = "significant wave height of sea ice surface elevation computed as 4*std(eta)"
    swh_var.units = "m"

    tz_var = nc4_out.createVariable("tp", "f4", ("measurement_segment"))
    tz_var.standard_name = "sea_surface_swell_wave_period"
    tz_var.long_name = "period of sea ice surface elevation computed as sqrt(m0/m2)"
    tz_var.units = "s"

    tm_var = nc4_out.createVariable("tm", "f4", ("measurement_segment"))
    tm_var.standard_name = "sea_surface_swell_wave_maximum_spectrum"
    tm_var.long_name = "period of sea ice surface elevation computed from the maximum of the wave spectrum"
    tm_var.units = "s"

    # ------------------------------------------------------------
    # filling the data in and get the "extreme bounds"

    lat_min = 90.0
    lat_max = -90.0
    lon_min = 180.0
    lon_max = -180.0
    datetime_start = datetime.datetime.fromtimestamp(2e10)
    datetime_end = datetime.datetime.fromtimestamp(0)

    for crrt_key in dict_observations:
        crrt_lat = dict_observations[crrt_key]["lat"]
        crrt_lon = dict_observations[crrt_key]["lon"]
        crrt_datetime = crrt_key

        lat_min = min(lat_min, crrt_lat)
        lat_max = max(lat_max, crrt_lat)
        lon_min = min(lon_min, crrt_lon)
        lon_max = max(lon_max, crrt_lon)
        datetime_start = min(datetime_start, crrt_datetime)
        datetime_end = max(datetime_end, crrt_datetime)

    nc4_out.geospatial_lat_min = str(lat_min)
    nc4_out.geospatial_lat_max = str(lat_max)
    nc4_out.geospatial_lon_min = str(lon_min)
    nc4_out.geospatial_lon_max = str(lon_max)
    nc4_out.time_coverage_start = datetime_start.isoformat()
    nc4_out.time_coverage_end = datetime_end.isoformat()

    # ------------------------------------------------------------
    # filling the data themselves

    for crrt_segment_ind, crrt_segment_key in enumerate(dict_observations):
        time_start_segment_var[crrt_segment_ind] = crrt_segment_key.timestamp()
        time_end_segment_var[crrt_segment_ind] = (crrt_segment_key + datetime.timedelta(minutes=20)).timestamp()

        lat_start_segment_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["lat"]
        lat_end_segment_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["lat"]

        lon_start_segment_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["lon"]
        lon_end_segment_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["lon"]

        hs_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["hs"]
        swh_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["swh"]
        tz_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["tp"]
        tm_var[crrt_segment_ind] = dict_observations[crrt_segment_key]["tm"]
