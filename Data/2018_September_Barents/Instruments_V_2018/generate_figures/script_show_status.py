from datetime import datetime, timedelta
import pytz
import pickle
from utils import sort_dict_keys_by_date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

plt.rcParams.update({'font.size': 14})

# to put into UTC
now_utc = datetime.now(pytz.utc)
today_utc = now_utc.date()

time_start = datetime(year=2018, month=9, day=15, hour=00, tzinfo=None)  # the beginning of the cruise
time_end = datetime(year=2018, month=10, day=15, hour=23, tzinfo=None)  # long enough later that all stopped to work

# load the data
path_to_dump = "../generate_dict_data/all.pkl"
with open(path_to_dump, 'rb') as fh:
    dict_data = pickle.load(fh)

# sort dictionary by date of transmission
keys_sorted_by_date = sort_dict_keys_by_date(dict_data)

# load the whole data for each logger in a separated dict entry
dict_data_each_logger = {}

for crrt_key in keys_sorted_by_date:
    crrt_time = dict_data[crrt_key]['datetime']

    # check if within the time
    if crrt_time > time_start and crrt_time < time_end:
        crrt_logger_ID = dict_data[crrt_key]['Device']

        # if a status file, fill in the status
        if dict_data[crrt_key]['data_kind'] == 'status':

            # add to the right list
            if crrt_logger_ID not in dict_data_each_logger:
                dict_data_each_logger[crrt_logger_ID] = {}
                dict_data_each_logger[crrt_logger_ID]["datetime"] = []
                dict_data_each_logger[crrt_logger_ID]["GPS"] = []
                dict_data_each_logger[crrt_logger_ID]["File"] = []
                dict_data_each_logger[crrt_logger_ID]["VBat"] = []

            dict_data_each_logger[crrt_logger_ID]["datetime"].append(dict_data[crrt_key]['datetime'])
            dict_data_each_logger[crrt_logger_ID]["GPS"].append(dict_data[crrt_key]['parsed_data']['GPRMC_binary_payload'])
            dict_data_each_logger[crrt_logger_ID]["File"].append(dict_data[crrt_key]['parsed_data']['filename'])
            dict_data_each_logger[crrt_logger_ID]["VBat"].append(float(dict_data[crrt_key]['parsed_data']['battery_level_V']))

    else:
        raise RuntimeError("time out of bounds!")
        
with open("./dict_data_each_logger_status.pkl", "wb") as fh:
    pickle.dump(dict_data_each_logger, fh)

# list of loggers
list_of_loggers = dict_data_each_logger.keys()

# a few sanity checks
for crrt_logger_ID in list_of_loggers:
    list_datetimes = dict_data_each_logger[crrt_logger_ID]["datetime"]
    for date_1, date_2 in zip(list_datetimes[:-1], list_datetimes[1:]):
        pass
        # assert (date_2 - date_1).total_seconds() > 60 * 60

# show the status information
# for the plot, use some modified time start and end
time_start_std = datetime(year=time_start.year, month=time_start.month, day=time_start.day - 1)
time_end_std = datetime(year=time_end.year, month=time_end.month, day=time_end.day + 1)

delta = time_end_std - time_start_std

for crrt_logger_ID in list_of_loggers:
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # show std day and night for illustration
    for i in range(delta.days + 1):
        current_day = time_start_std + timedelta(days=i)

        start_day = current_day + timedelta(hours=6)
        end_day = current_day + timedelta(hours=18)

        # convert to matplotlib date representation
        start = mdates.date2num(start_day)
        end = mdates.date2num(end_day)
        width = end - start

        # Plot rectangle
        rect = Rectangle((start, 0), width, 100, color='yellow', alpha=0.8)
        ax.add_patch(rect)

        start_night = current_day + timedelta(hours=18)
        end_might = current_day + timedelta(hours=24 + 6)

        # convert to matplotlib date representation
        start = mdates.date2num(start_night)
        end = mdates.date2num(end_might)
        width = end - start

        # Plot rectangle
        rect = Rectangle((start, 0), width, 100, color='gray', alpha=0.7)
        ax.add_patch(rect)

    # show the battery level and reference levels
    plt.hlines(2.7, dict_data_each_logger[crrt_logger_ID]["datetime"][0], dict_data_each_logger[crrt_logger_ID]["datetime"][-1], linewidth=2.5)
    plt.text(dict_data_each_logger[crrt_logger_ID]["datetime"][0], 2.65, "empty", fontsize=18)

    plt.hlines(3.3, dict_data_each_logger[crrt_logger_ID]["datetime"][0], dict_data_each_logger[crrt_logger_ID]["datetime"][-1], linewidth=2.5)
    plt.text(dict_data_each_logger[crrt_logger_ID]["datetime"][0], 3.31, "full", fontsize=18)

    plt.plot(dict_data_each_logger[crrt_logger_ID]["datetime"], dict_data_each_logger[crrt_logger_ID]["VBat"], color='red', marker='*', linestyle='-', linewidth=2)
    plt.text(dict_data_each_logger[crrt_logger_ID]["datetime"][0], dict_data_each_logger[crrt_logger_ID]["VBat"][0] - 0.065, "battery", fontsize=18)

    plt.xticks(rotation=30)
    plt.ylabel("battery (V) Ird {}".format(crrt_logger_ID))
    plt.xlim(dict_data_each_logger[crrt_logger_ID]["datetime"][0], dict_data_each_logger[crrt_logger_ID]["datetime"][-1])
    plt.ylim(2.6, 3.4)
    plt.tight_layout()

    plt.savefig("script_show_status__battery_{}.pdf".format(crrt_logger_ID[10:]))

plt.show()

# %% show the GPS trajectories
plt.figure()

markers_list = ['o', 'v', 's', 'X', 'P', 'D']

for crrt_ind, crrt_logger_ID in enumerate(list_of_loggers):
    # using latitude longitude (DD) instead of lat and lon (DMS)
    list_lat = [x.latitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
    list_lon = [x.longitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
    plt.plot(list_lon, list_lat, label=crrt_logger_ID, marker=markers_list[crrt_ind])

    print("positions for logger {}".format(crrt_logger_ID))
    for crrt_GPRMC in dict_data_each_logger[crrt_logger_ID]["GPS"]:
        print("{} {} (UTC) : {} {}, {} {} (DD) {} {}, {} {} (DMS)".format(crrt_GPRMC.datestamp, crrt_GPRMC.timestamp, crrt_GPRMC.latitude, crrt_GPRMC.lat_dir, crrt_GPRMC.longitude, crrt_GPRMC.lon_dir, crrt_GPRMC.lat, crrt_GPRMC.lat_dir, crrt_GPRMC.lon, crrt_GPRMC.lon_dir))

plt.xlabel('Lon [DD E]')
plt.ylabel('lat [DD N]')

plt.legend()


# %% show the GPS trajectories showing the position of the sensors at different days
plt.figure()

colors_list = ['k', 'r', 'b', 'orange', 'gray', 'purple']

for crrt_ind, crrt_logger_ID in enumerate(list_of_loggers):
    # using latitude longitude (DD) instead of lat and lon (DMS)
    list_lat = [x.latitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
    list_lon = [x.longitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
    plt.plot(list_lon, list_lat, label=crrt_logger_ID, marker=markers_list[crrt_ind], color=colors_list[crrt_ind])

# add the days on which to put markers
# TODO: could automate the choosing of equi-spaced days within the measurement range
list_days = [datetime(year=2020, month=7, day=16, hour=00, tzinfo=None),
             datetime(year=2020, month=8, day=1, hour=00, tzinfo=None),
             datetime(year=2020, month=8, day=15, hour=00, tzinfo=None),
             datetime(year=2020, month=9, day=1, hour=00, tzinfo=None),
             datetime(year=2020, month=9, day=13, hour=00, tzinfo=None),
             ]
dict_points_start_days = {}

markers_list = ["${}$".format(crrt_date.strftime("%m/%d")) for crrt_date in list_days]

for crrt_ind_day, crrt_day in enumerate(list_days):
    dict_points_start_days[crrt_day] = {}
    dict_points_start_days[crrt_day]['lat'] = []
    dict_points_start_days[crrt_day]['lon'] = []

    for crrt_ind, crrt_logger_ID in enumerate(list_of_loggers):
        if dict_data_each_logger[crrt_logger_ID]["datetime"][0] < crrt_day:
            # using latitude longitude (DD) instead of lat and lon (DMS)
            crrt_list_lat = [x.latitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
            crrt_list_lon = [x.longitude for x in dict_data_each_logger[crrt_logger_ID]["GPS"]]
            crrt_list_days = [x for x in dict_data_each_logger[crrt_logger_ID]["datetime"]]

            points_after = [i for (i, j) in enumerate(crrt_list_days) if j >= crrt_day]

            if points_after:
                first_point = points_after[0]
                crrt_point_lat = crrt_list_lat[first_point] + 0.2
                crrt_point_lon = crrt_list_lon[first_point]

                plt.plot(crrt_point_lon, crrt_point_lat,
                        marker=markers_list[crrt_ind_day],
                        markersize=32,
                        linestyle='None',
                        color=colors_list[crrt_ind])

plt.xlabel('Lon [DD E]')
plt.ylabel('lat [DD N]')

plt.legend()
plt.tight_layout()

plt.savefig("script_show_status__trajectories.pdf")

plt.show()
