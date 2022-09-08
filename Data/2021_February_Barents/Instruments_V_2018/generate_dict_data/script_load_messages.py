"""Generate data python dict from the rock7 csv hex message files."""

from datetime import datetime
from binascii import unhexlify

import csv
import pickle

import load_Iridium_wave_data
import load_status_information

verbose = 5

# %% path to the data
data_root_path = "../"
csv_folder = "data_from_rock7/"
dict_folder = "generate_dict_data/"

#  list_rock7_ids = ["200910",
#                    "200911",
#                    "200906"
#                    ]

list_rock7_ids = ["all"]

for crrt_rock7_id in list_rock7_ids:
    path_to_data = data_root_path + csv_folder + crrt_rock7_id + ".csv"
    path_to_dump = data_root_path + dict_folder + crrt_rock7_id + ".pkl"

    # summarize kinds of data: message_length -> data_kind
    dict_message_kinds = {138: 'status', 340: 'spectrum', 0: 'faulty'}

    # load the data
    dict_entries = {}

    with open(path_to_data, mode='r') as infile:
        input_dict = csv.DictReader(infile)

        for index, row in enumerate(input_dict):
            dict_entries[index] = row

    for crrt_entry in dict_entries:
        if verbose > 0:
            print(crrt_entry)
            print(dict_entries[crrt_entry])

        crrt_data = dict_entries[crrt_entry]

        # check which kind of message depending on its length
        crrt_length_bytes = int(crrt_data['Length (Bytes)'])
        if verbose > 0:
            print(crrt_length_bytes)

        if crrt_length_bytes in dict_message_kinds:
            data_kind = dict_message_kinds[crrt_length_bytes]
        else:
            data_kind = 'faulty'

        crrt_data['data_kind'] = data_kind

        if verbose > 0:
            print(data_kind)

        # extract the datetime timestamp
        crrt_date_string = crrt_data["Date Time (UTC)"]
        if verbose > 0:
            print(crrt_date_string)

        crrt_datetime = datetime.strptime(crrt_date_string, '%d/%b/%Y %H:%M:%S')
        crrt_data['datetime'] = crrt_datetime

        if verbose > 0:
            print(crrt_datetime)

        # convert the payload to bytes
        crrt_hex_payload = crrt_data['Payload']
        if verbose > 0:
            print(crrt_hex_payload)

        crrt_bin_payload = unhexlify(crrt_hex_payload)
        crrt_data['binary_payload'] = crrt_bin_payload

        if verbose > 0:
            print(crrt_bin_payload)

        # extract the information from the binary messages
        if data_kind == 'status':
            dict_data = load_status_information.load_status_information(crrt_bin_payload)
        elif data_kind == 'spectrum':
            dict_data = load_Iridium_wave_data.load_data(crrt_bin_payload)
        else:
            dict_data = None

        crrt_data["parsed_data"] = dict_data

        if verbose > 0:
            print(dict_data)

    if verbose > 0:
        print(dict_entries)

    with open(path_to_dump, 'wb') as fh:
        pickle.dump(dict_entries, fh)
