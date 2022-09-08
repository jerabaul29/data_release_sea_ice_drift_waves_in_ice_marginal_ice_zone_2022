import pickle

import datetime

import os
import time

import matplotlib.pyplot as plt

import math

from icecream import ic

import itertools

from dataclasses import dataclass

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** Configure icecream")
ic.configureOutput(prefix='', outputFunction=print)

# ------------------------------------------------------------------------------------------
print("***** define csv boat data header")
header = ["Station type", "Time", "Ref. no", "Loc.St.No", "Log",
          "Latitude", "Longitude", "Depth", "Heading", "Speed",
          "Water temp", "Wind", "Wind dir", "Air temp", "Air pressure",
          "Humidity", "Weather", "Seastate", "Clouds", "Ice",
          "Quantity", "Code", "Number", "Serial no.", "Wirelength",
          "Min depth", "Max depth", "Opening", "Spread", "Comment"]


# ------------------------------------------------------------------------------------------
@dataclass
class BoatPacket:
    datetime_fix: datetime.datetime
    latitude: float
    longitude: float
    speed: float
    heading: float


# ------------------------------------------------------------------------------------------
def coord_to_dd(dms):
    # minutes are in dms but in decimal form (no seconds seems like)
    minutes_dms = int(dms) % 100 + dms - int(dms)
    minutes_dd = minutes_dms * 100.0 / 60.0

    # degrees are always in dms
    degrees = int(dms / 100)

    return degrees + minutes_dd / 100.0


def csv_boat_entry_to_dict(header_datetime_date, csv_entry):
    """a csv entry looks like:
    "  -->","00:00:00","","","1520.505","7819.596625 N","02713.180820 E","273.02","24.63","4.7","-1.8","7.6","186","-7.8","1024.8","83","","","","","","","","","","","","","",""
    """
    list_entries = csv_entry.replace('"', '').replace("\n", "").split(",")

    id_time = header.index("Time")
    id_lat = header.index("Latitude")
    id_lon = header.index("Longitude")
    id_speed = header.index("Speed")
    id_heading = header.index("Heading")

    time = list_entries[id_time]
    lat = list_entries[id_lat]
    lon = list_entries[id_lon]
    speed = float(list_entries[id_speed])  # suppose the speed in is knots, but not sure, if use speed, should investigate
    heading = float(list_entries[id_heading])

    datetime_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
    datetime_fix = datetime.datetime.combine(header_datetime_date, datetime_time)

    latitude = coord_to_dd(float(lat[:-2]))
    longitude = coord_to_dd(float(lon[:-2]))

    result = BoatPacket(
        datetime_fix=datetime_fix,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        heading=heading
    )

    return result


def parse_boat_file(path_to_file):

    list_entries = []

    with open(path_to_file, "r") as fh:
        metadata = fh.readline().replace('"', '').replace("\n", "").split(",")
        date = metadata[7]
        datetime_date = datetime.datetime.strptime(date, "%d.%m.%Y").date()

        fh.readline()
        fh.readline()

        for crrt_line in fh:
            try:
                crrt_entry = csv_boat_entry_to_dict(datetime_date, fh.readline())
                list_entries.append(crrt_entry)
            except Exception:
                # print("received exception: {}".format(e))
                break

    return list_entries


def parse_all_boat_files_in_folder(path_to_folder):
    list_all_files = os.listdir(path_to_folder)
    list_all_files = sorted(list_all_files)
    list_all_files = [crrt_entry for crrt_entry in list_all_files if crrt_entry[-3:] == "csv"]

    list_entries = []
    for crrt_file in list_all_files:
        print("parse {}".format(crrt_file))
        crrt_entries = parse_boat_file(path_to_folder + "/" + crrt_file)
        list_entries += crrt_entries

    return list_entries


def plot_list_entries(list_entries, plot_immobile=True):
    list_lats = [crrt_entry.latitude for crrt_entry in list_entries]
    list_lons = [crrt_entry.longitude for crrt_entry in list_entries]
    list_headings = [crrt_entry.heading for crrt_entry in list_entries]
    list_speeds = [crrt_entry.speed for crrt_entry in list_entries]

    immobile_threshold = 0.35
    list_immobile_speeds = [crrt_entry.speed if crrt_entry.speed < immobile_threshold else math.nan for crrt_entry in list_entries]

    list_ones = [10 for _ in list_entries]

    """
    arrow_coords_x = []
    arrow_coords_y = []
    for (crrt_heading, crrt_speed) in zip(list_headings, list_speeds):
        ic(crrt_heading)
        ic(crrt_speed)
        heading_rad = crrt_heading * math.pi / 180.0
        arrow_coords_x.append(crrt_speed * math.sin(heading_rad))
        arrow_coords_y.append(crrt_speed * math.cos(heading_rad))
    """

    plt.figure()
    plt.scatter(list_lons, list_lats, list_ones, list_speeds)
    plt.colorbar()

    if plot_immobile:
        plt.figure()
        plt.scatter(list_lons, list_lats, list_ones, list_immobile_speeds)
        plt.colorbar()
        plt.clim(0, immobile_threshold)


def find_list_immobile_segments(list_entries):
    # we want to find the list of segments (list of positions) when the boat is immobile
    # for this: 1) do a thresholding pass
    #           2) group together by set of points that have at most 2 minutes between consecutive points

    list_immobile_points = []

    for crrt_entry in list_entries:
        if crrt_entry.speed < 0.35:
            list_immobile_points.append(crrt_entry)

    list_immobile_segments = []
    crrt_segment = [list_entries[0]]

    for crrt_entry in list_immobile_points[1:]:
        if (abs(crrt_entry.datetime_fix - crrt_segment[-1].datetime_fix)) <= datetime.timedelta(seconds=2*60+15):
            crrt_segment.append(crrt_entry)
        else:
            if len(crrt_segment) >= 5:
                list_immobile_segments.append(crrt_segment)
            crrt_segment = [crrt_entry]

    print("found {} segments of immobile points".format(len(list_immobile_segments)))
    for crrt_segment in list_immobile_segments:
        print("***")
        ic(len(crrt_segment))
        ic(crrt_segment[0].datetime_fix)
        ic(crrt_segment[-1].datetime_fix)
        ic(crrt_segment[-1].datetime_fix - crrt_segment[0].datetime_fix)

    list_immobile_points = list(itertools.chain(*list_immobile_segments))

    plot_list_entries(list_immobile_points, plot_immobile=False)

    return list_immobile_segments


if __name__ == "__main__":
    crrt_path = "../boat_data/"
    list_entries = parse_all_boat_files_in_folder(crrt_path)
    plot_list_entries(list_entries)
    list_immobile_segments = find_list_immobile_segments(list_entries)

    file_dump_segments = "./list_segments_immobile.pkl"

    with open(file_dump_segments, "bw") as fh:
        pickle.dump(list_immobile_segments, fh)

    plt.show()
