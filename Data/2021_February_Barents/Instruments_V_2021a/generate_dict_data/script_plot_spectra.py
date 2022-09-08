import math
import pickle as pkl
import matplotlib.pyplot as plt
import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

import os
import time

# ------------------------------------------------------------------------------------------
print("***** Put the interpreter in UTC, to make sure no TZ issues")
os.environ["TZ"] = "UTC"
time.tzset()

# ------------------------------------------------------------------------------------------
print("***** configure matplotlib")
plt.rcParams.update({'font.size': 14})
list_colors = list(mcolors.TABLEAU_COLORS)
list_colors.append("w")
list_colors.append("k")

dict_bad_data = {
    "19648": [datetime.datetime(2021, 3, 6, 0, 0, 0), datetime.datetime(2021, 3, 6, 4, 0, 0)]
}

with open("./dict_all_data.pkl", "rb") as fh:
    dict_data_each_logger = pkl.load(fh)

list_instruments_with_spectra = []
# instruments_blacklist = ["19641"]
instruments_blacklist = ["19641"]

for crrt_instrument in dict_data_each_logger.keys():
    if len(dict_data_each_logger[crrt_instrument]["spectra"]) > 20 and crrt_instrument not in instruments_blacklist:
        print("instrument {} has at least a few spectrum data".format(crrt_instrument))
        list_instruments_with_spectra.append(crrt_instrument)

date_start = datetime.datetime(2021, 2, 25, 18, 0, 0)

for show_spectrum in ["normalized_elevation"]:
    print("we are looking at spectra for {}".format(show_spectrum))

    # date end:
    for look_at_case in ["in_ice"]:  # these instruments can only be used on the ice, as they are not reliable as wave buoys and may have a very strange hydrodynamic response; only keep the data corresponding to in_ice conditions in the end
        if show_spectrum == "normalized_elevation":
            if look_at_case == "full":
                # this is to look at the full data
                date_end   = datetime.datetime(2021, 5,  1,  0, 0, 0)
                vmin_pcolor = -3.0
                vmax_pcolor = 1.0
            elif look_at_case == "in_ice":
                # this is to look only at "in ice data"
                date_end   = datetime.datetime(2021, 3, 18, 18, 0, 0)
                vmin_pcolor = -3.0
                vmax_pcolor = 1.0
        else:
            raise RuntimeError("only use normalized_elevation in recent scripts!")

        date_start_md = mdates.date2num(date_start)
        date_end_md = mdates.date2num(date_end)

        fig, axes = plt.subplots(nrows=len(list_instruments_with_spectra), ncols=1)

        for ind, crrt_instrument in enumerate(list_instruments_with_spectra):

            val = 100 * len(list_instruments_with_spectra) + 10 + ind + 1
            plt.subplot(val)

            list_spectra_data = dict_data_each_logger[crrt_instrument]["spectra"]

            list_frequencies = list_spectra_data[0].list_frequencies

            list_datetimes = [list_spectra_data[0].datetime_fix]
            list_spectra = [list_spectra_data[0].list_elevation_normalized_energies]
            shape_spectrum = (len(list_spectra[0]), )

            for crrt_entry in list_spectra_data[1:]:
                if (crrt_entry.datetime_fix - list_datetimes[-1] > datetime.timedelta(hours=6)):
                    list_datetimes.append(list_datetimes[-1] + datetime.timedelta(hours=2))
                    list_datetimes.append(crrt_entry.datetime_fix - datetime.timedelta(hours=2))
                    list_spectra.append(np.full(shape_spectrum, np.nan))
                    list_spectra.append(np.full(shape_spectrum, np.nan))

                list_datetimes.append(crrt_entry.datetime_fix)

                if show_spectrum == "normalized_elevation":
                    crrt_spectrum = crrt_entry.list_elevation_normalized_energies
                    list_spectra.append(crrt_spectrum)

            pclr = plt.pcolor(list_datetimes, list_frequencies, np.log10(np.transpose(np.array(list_spectra))), vmin=vmin_pcolor, vmax=vmax_pcolor)
            plt.xlim([date_start_md, date_end_md])
            plt.ylim([0.05, 0.25])

            if ind < len(list_instruments_with_spectra)-1:
                plt.xticks([])
            plt.xticks(rotation=30)

            plt.ylabel("f [Hz]\n({})".format(crrt_instrument))

        plt.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(pclr, cax=cbar_ax)
        if show_spectrum == "normalized_elevation":
            cbar.set_label('log$_{10}$(S) [m$^2$/Hz]')

        # plt.tight_layout()
        plt.savefig("spectra_" + show_spectrum + "_" + look_at_case + ".png")

        plt.show()

        plt.figure()

        for ind, crrt_instrument in enumerate(list_instruments_with_spectra):
            crrt_color = list_colors[ind]

            list_spectra_data = dict_data_each_logger[crrt_instrument]["spectra"]

            list_datetimes = [crrt_data.datetime_fix for crrt_data in list_spectra_data]
            list_swh = [crrt_data.hs for crrt_data in list_spectra_data]
            list_tp = [crrt_data.tp for crrt_data in list_spectra_data]
            list_spectra = [crrt_data.list_elevation_normalized_energies for crrt_data in list_spectra_data]
            list_frequencies = [crrt_data.list_frequencies for crrt_data in list_spectra_data]

            def compute_spectral_moment(list_frequencies, list_elevation_energies, order):
                list_to_integrate = [
                    math.pow(crrt_freq, order) * crrt_energy for (crrt_freq, crrt_energy) in zip(list_frequencies, list_elevation_energies)
                ]
                moment = np.trapz(list_to_integrate, list_frequencies)
                return moment

            list_processed_swh = []
            list_processed_tp = []

            for crrt_entry in list_spectra_data:
                m0 = compute_spectral_moment(crrt_entry.list_frequencies, crrt_entry.list_elevation_normalized_energies, 0)
                m2 = compute_spectral_moment(crrt_entry.list_frequencies, crrt_entry.list_elevation_normalized_energies, 2)
                m4 = compute_spectral_moment(crrt_entry.list_frequencies, crrt_entry.list_elevation_normalized_energies, 4)

                list_processed_tp.append(math.sqrt(m0/m2))
                list_processed_swh.append(4.0 * math.sqrt(m0))

            plt.plot(list_datetimes, list_swh, color=crrt_color, marker=".", label="swh {}".format(crrt_instrument))
            plt.plot(list_datetimes, 0.001 + np.array(list_processed_swh), marker="o", color=crrt_color, label="swh processed")
            plt.plot(list_datetimes, list_tp, color=crrt_color, label="tp", marker="+")
            plt.plot(list_datetimes, 0.001 + np.array(list_processed_tp), color=crrt_color, marker="*", label="tp processed")

        plt.xlim([date_start_md, date_end_md])
        plt.legend()
        plt.savefig("swh_tp.png")
        plt.show()

