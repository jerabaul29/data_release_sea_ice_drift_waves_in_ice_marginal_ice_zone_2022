import pytz
import datetime
import os
import time
from dataclasses import dataclass

@dataclass
class GNSS_Packet:
    datetime_fix: datetime.datetime
    latitude: float
    longitude: float
    raw: str

# make sure we use UTC in all our work
os.environ["TZ"] = "UTC"
time.tzset()


def decode_hex_rawstring(hex_str_in):
    print("--------------------")
    print("decode hex rawstring: {}".format(hex_str_in))
    str_plaintext = bytearray.fromhex(hex_str_in).decode()
    str_plaintext_splitted = str_plaintext.split(',')
    battery = float(str_plaintext_splitted[0])
    latitude = float(str_plaintext_splitted[2])
    longitude = float(str_plaintext_splitted[3])
    timestamp = datetime.datetime.strptime(str_plaintext_splitted[1], '%Y%m%d%H%M%S')
    pytz.utc.localize(timestamp)

    crrt_packet = GNSS_Packet(
        datetime_fix=timestamp,
        latitude=latitude,
        longitude=longitude,
        raw=hex_str_in
    )

    print("got: {}".format(crrt_packet))
    print("--------------------")

    return crrt_packet
