import pickle as pkl

import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from utils import get_index_of_first_list_elem_greater_starting_smaller

# ------------------------------------------------------------------------------------------
# a few quick and dirty utils

# ------------------------------------------------------------------------------------------
# load all trajectory data
with open("./dict_all_data.pkl", "rb") as fh:
    dict_data_each_logger = pkl.load(fh)

for type_plot in ["Norway", "Svalbard"]:
    # ------------------------------------------------------------------------------------------
    # show the trajectories on the map

    # The data to plot are defined in lat/lon coordinate system, so PlateCarree()
    # is the appropriate choice of coordinate reference system:
    _ = ccrs.PlateCarree()

    # the map projection properties.
    proj = ccrs.LambertConformal(central_latitude=77.0,
                                 central_longitude=24.0,
                                 standard_parallels=(74.5, 79.0))

    # let's have a large figure
    plt.figure(figsize=(15, 18))
    ax = plt.axes(projection=proj)

    # what to include on the map
    resol = '50m'
    land = cartopy.feature.NaturalEarthFeature('physical', 'land',
                                               scale=resol, edgecolor='k', facecolor=cfeature.COLORS['land'])
    ocean = cartopy.feature.NaturalEarthFeature('physical', 'ocean',
                                                scale=resol, edgecolor='none', facecolor=cfeature.COLORS['water'])

    # display the land and ocean
    ax.add_feature(land, zorder=0)
    ax.add_feature(ocean, linewidth=0.2, zorder=0)

    # choose the extent of the map
    if type_plot == "Norway":
        ax.set_extent([6, 36, 70.0, 80.5]) # until Norway
    elif type_plot == "Svalbard":
        ax.set_extent([13, 34, 75.0, 79.5]) # only close to Svalbard

    list_colors = list(mcolors.TABLEAU_COLORS)
    list_colors.append("w")
    list_colors.append("k")

    # plot the trajectories
    for ind, crrt_instrument in enumerate(dict_data_each_logger.keys()):
        # get the data
        list_datetime = [crrt_fix.datetime_fix for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]
        list_latitude = [crrt_fix.latitude for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]
        list_longitude = [crrt_fix.longitude for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]

        # get instrument ID
        ID = crrt_instrument

        size_scatter_markers = 100

        # plot full trajectory
        plt.scatter(list_longitude, list_latitude, s=size_scatter_markers/8.0, transform=ccrs.PlateCarree(), zorder=3, label=ID, color=list_colors[ind])

    for ind, crrt_instrument in enumerate(dict_data_each_logger.keys()):
        # get the data
        list_datetime = [crrt_fix.datetime_fix for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]
        list_latitude = [crrt_fix.latitude for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]
        list_longitude = [crrt_fix.longitude for crrt_fix in dict_data_each_logger[crrt_instrument]["gnss_fixes"]]

        # get instrument ID
        ID = crrt_instrument

        size_scatter_markers = 100

        # plot initial position
        if ind == 0:
            plt.scatter(list_longitude[0], list_latitude[0], transform=ccrs.PlateCarree(), color='k', s=size_scatter_markers, label="start", zorder=10)
        else:
            plt.scatter(list_longitude[0], list_latitude[0], transform=ccrs.PlateCarree(), color='k', s=size_scatter_markers, zorder=10)

        # plot location at a few times
        list_positions_to_plot = [
            datetime.datetime(2021, 2, 20, 0, 0, 0),
            datetime.datetime(2021, 2, 27, 0, 0, 0),
            datetime.datetime(2021, 3, 10, 0, 0, 0),
            datetime.datetime(2021, 3, 20, 0, 0, 0),
            datetime.datetime(2021, 3, 28, 0, 0, 0),
        ]

        list_markers = [
            "*",
            "+",
            "x",
            "v",
            "s",
            "P"
        ]

        for crrt_marker, crrt_time in zip(list_markers, list_positions_to_plot):
            if ind == 0:
                plt.scatter([], [], marker=crrt_marker, color='k', s=size_scatter_markers, label=str(crrt_time))

        for ind_time, crrt_time in enumerate(list_positions_to_plot):
            crrt_index = get_index_of_first_list_elem_greater_starting_smaller(list_datetime, crrt_time)
            if crrt_index is not None:
                plt.scatter(list_longitude[crrt_index], list_latitude[crrt_index], transform=ccrs.PlateCarree(), marker=list_markers[ind_time], color="k", s=size_scatter_markers, zorder=10)
        

    # the meridians and parallels to show
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=2, color='gray', alpha=0.7, linestyle='--')
    # gl.top_labels = False
    # gl.bottom_labels = True
    gl.top_labels = True
    gl.right_labels = True
    gl.left_labels = False
    gl.right_labels = True
    # gl.xlines = False
    # gl.ylines = False
    # gl.xlocator = mticker.FixedLocator([-180, -45, 0, 45, 180])
    # gl.xformatter = LONGITUDE_FORMATTER
    # gl.yformatter = LATITUDE_FORMATTER
    # gl.xlabel_style = {'size': 15, 'color': 'gray'}
    # gl.xlabel_style = {'color': 'red', 'weight': 'bold'}

    plt.legend()

    if type_plot == "Norway":
        plt.savefig("all_trajectories_AeN2021_instrumentsv2021_Norway.png")
        plt.savefig("all_trajectories_AeN2021_instrumentsv2021_Norway.pdf")
    elif type_plot == "Svalbard":
        plt.savefig("all_trajectories_AeN2021_instrumentsv2021_Svalbard.png")
        plt.savefig("all_trajectories_AeN2021_instrumentsv2021_Svalbard.pdf")

    plt.show()

