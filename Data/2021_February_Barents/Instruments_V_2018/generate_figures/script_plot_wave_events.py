import pickle as pkl

from utils import get_index_of_first_list_elem_greater_starting_smaller

import datetime

import numpy as np
import matplotlib.pyplot as plt

with open("./dict_data_each_logger_wave.pkl", "br") as fh:
    dict_data_each_logger = pkl.load(fh)

# show a waves in ice event
list_dates_waves_in_ice = [
         (datetime.datetime(2021, 2, 21, 0, 0, 0), datetime.datetime(2021, 2, 25, 0, 0, 0)),
         (datetime.datetime(2021, 2, 28, 0, 0, 0), datetime.datetime(2021, 3, 6, 0, 0, 0)),
         (datetime.datetime(2021, 3, 6, 0, 0, 0), datetime.datetime(2021, 3, 9, 0, 0, 0)),
]

for crrt_event_start_end in list_dates_waves_in_ice:
    date_start = crrt_event_start_end[0]
    date_end = crrt_event_start_end[1]

    plt.figure()

    # show the SWH and Tp
    for crrt_station in dict_data_each_logger.keys():
        crrt_list_datetime = dict_data_each_logger[crrt_station]["datetime"]
        crrt_list_SWH = dict_data_each_logger[crrt_station]["SWH"]
        crrt_list_Tp = dict_data_each_logger[crrt_station]["T_z0"]

        crrt_ID = crrt_station[11:]
        while len(crrt_ID) < 5:
            crrt_ID = "0" + crrt_ID

        crrt_first_index = get_index_of_first_list_elem_greater_starting_smaller(
                 crrt_list_datetime,
                 date_start
        )

        crrt_last_index = get_index_of_first_list_elem_greater_starting_smaller(
                 crrt_list_datetime,
                 date_end
        )
         
        if crrt_first_index is not None and crrt_last_index is not None:

            list_datetimes_no_NaN = []
            list_SWH_no_NaN = []
            list_Tp_no_NaN = []

            for crrt_ind in range(crrt_first_index, crrt_last_index):
                if crrt_list_SWH[crrt_ind] >= 0.0:
                    list_datetimes_no_NaN.append(crrt_list_datetime[crrt_ind])
                    list_SWH_no_NaN.append(crrt_list_SWH[crrt_ind])
                    list_Tp_no_NaN.append(crrt_list_Tp[crrt_ind])

            plt.subplot(211)
            plt.plot(list_datetimes_no_NaN, list_SWH_no_NaN,
                           label=crrt_ID, linewidth=3.0,
                        )
            plt.ylabel("SWH [m]")
            plt.xticks([])

            plt.subplot(212)
            plt.plot(list_datetimes_no_NaN, list_Tp_no_NaN,
                           label=crrt_ID, linewidth=3.0
                        )
            plt.ylabel("T_p [s]")

            plt.xticks(rotation=30)

    plt.subplot(211)
    plt.legend()
    plt.tight_layout()

    fig_name = "SWH_Tp_event_{}_to_{}.".format(date_start, date_end)
    plt.savefig(fig_name + ".pdf")
    plt.savefig(fig_name + ".png")

    plt.show()

