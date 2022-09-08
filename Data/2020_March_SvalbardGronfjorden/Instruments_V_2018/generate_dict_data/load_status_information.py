"""Load iridium status information from a binary string."""

import pynmea2


def load_status_information(binary_payload, verbose=0, SIZE_MSG_BATTERY=4, SIZE_MSG_FILENAME=6):
    print("START LOAD STATUS INFORMATION")
    dict_binary_payload = {}

    if verbose > 3:
        for crrt_char in binary_payload:
            print(crrt_char)

    battery_level = binary_payload[0:SIZE_MSG_BATTERY]
    filename = binary_payload[SIZE_MSG_BATTERY: SIZE_MSG_BATTERY + SIZE_MSG_FILENAME]

    GPRMC_string = []

    for crrt_char in binary_payload[SIZE_MSG_BATTERY + SIZE_MSG_FILENAME:]:
        crrt_char = chr(crrt_char)
        if crrt_char == '\n' or crrt_char == '\r':
            break
        else:
            GPRMC_string.append(crrt_char)

    print(GPRMC_string)
    GPRMC_string = "".join(GPRMC_string)

    if verbose > 0:
        print("battery_level: {}".format(battery_level))
        print("filename: {}".format(filename))
        print("GPRMC string: {}".format(GPRMC_string))

    dict_binary_payload["battery_level_V"] = battery_level
    dict_binary_payload["filename"] = filename
    dict_binary_payload["GPRMC_binary_payload"] = pynmea2.parse(GPRMC_string)

    return(dict_binary_payload)


def expand_status_information(dict_binary_payload):

    battery_level = dict_binary_payload["battery_level_V"]
    filename = dict_binary_payload["filename"]
    GPRMC_binary_payload = dict_binary_payload["GPRMC_binary_payload"]

    return(battery_level, filename, GPRMC_binary_payload)
