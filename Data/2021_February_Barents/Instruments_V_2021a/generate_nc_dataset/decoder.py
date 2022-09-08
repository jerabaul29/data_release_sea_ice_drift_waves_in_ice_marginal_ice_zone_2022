#!/usr/bin/python3
# before I used #!/bin/python3 , but some users were experiencing problems

import binascii
import struct
import datetime
import time
import os
from dataclasses import dataclass
import click
import math
import numpy as np

#--------------------------------------------------------------------------------
# make sure we are all UTC

os.environ["TZ"] = "UTC"
time.tzset()

#--------------------------------------------------------------------------------
# a few module constants

_BINARY_DECODER_TWOPO = 2.0 * math.pi

# properties of the GNSS packets
_BINARY_DECODER_GNSS_PACKET_LENGTH = 14

# properties of the wave spectra packets with 1024 FFT_LEN
_BINARY_DECODER_WAVES_PACKET_W_LENGTH = 65
_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MIN_BIN = 3
_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MAX_BIN = 31  # use correct conventions, at some point in the cpp. was as 30 with last point included
_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_SCALER = 65000
_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_SAMPLING_FREQ_HZ = 10.0
_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_NBR_SAMPLES_PER_SEGMENT = 2**10

# properties of the wave spectra packets with 2048 FFT_LEN
_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN = 9
_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MAX_BIN = 64
_BINARY_DECODER_WAVES_PACKET_X_LENGTH = 4 + 4 + 2*(_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MAX_BIN - _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN) + 2 + 1  # note: the last 2 is due to memory alignment
_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_SCALER = 65000
_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_SAMPLING_FREQ_HZ = 10.0
_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_NBR_SAMPLES_PER_SEGMENT = 2**11

#--------------------------------------------------------------------------------
# helper functions for unpacking binary data

def byte_to_char(crrt_byte):
    return(chr(crrt_byte))

def one_byte_to_int(crrt_byte):
    return(struct.unpack('B', bytes(crrt_byte))[0])

def four_bytes_to_long(crrt_four_bytes):
    res = struct.unpack('<I', bytes(crrt_four_bytes))
    return res[0]

def four_bytes_to_float(crrt_four_bytes):
    res = struct.unpack('<f', bytes(crrt_four_bytes))
    return res[0]

#--------------------------------------------------------------------------------
# custom data classes to store data packets

@dataclass
class GNSS_Packet:
    datetime_fix: datetime.datetime
    latitude: float
    longitude: float
    raw: str

@dataclass
class GNSS_Metadata:
    nbr_gnss_fixes: int

@dataclass
class Waves_Packet:
    datetime_fix: datetime.datetime
    list_frequencies: list
    list_acceleration_energies: list
    list_elevation_normalized_energies: list
    m0: float
    m2: float
    m4: float
    hs: float
    tp: float
    raw: str

@dataclass
class Waves_Metadata:
    None

#--------------------------------------------------------------------------------
# unpacking of GNSS packets

def unpack_gnss_packet(bin_msg, print_decoded=False):
    assert len(bin_msg) == _BINARY_DECODER_GNSS_PACKET_LENGTH, "GNSS packets with start and end byte have 14 bytes, got {} bytes".format(len(bin_msg))

    char_first_byte = byte_to_char(bin_msg[0])

    assert char_first_byte == 'F', "GNSS packets must start with a 'F', got {}".format(char_first_byte)

    posix_timestamp_fix = four_bytes_to_long(bin_msg[1:5])
    datetime_fix = datetime.datetime.fromtimestamp(posix_timestamp_fix)

    latitude_long = four_bytes_to_long(bin_msg[5:9])
    latitude = latitude_long / 1.0e7

    longitude_long = four_bytes_to_long(bin_msg[9:13])
    longitude = longitude_long / 1.0e7

    if print_decoded:
        print("-------------------- decoded GNSS message --------------------")
        print("fix at posix {}, i.e. {}".format(posix_timestamp_fix, datetime_fix))
        print("latitude {}, i.e. {}".format(latitude_long, latitude))
        print("longitude {}, i.e. {}".format(longitude_long, longitude))
        print("--------------------------------------------------------------")

    char_next_byte = byte_to_char(bin_msg[13])

    assert char_next_byte == 'E' or char_next_byte == 'F', "either end ('E') or fix ('F') expected at the end, got {}".format(char_next_byte)

    decoded_packet = GNSS_Packet(
        datetime_fix=datetime_fix,
        latitude=latitude,
        longitude=longitude,
        raw=binascii.hexlify(bin_msg)
    )

    return (decoded_packet, char_next_byte)

#--------------------------------------------------------------------------------
# unpacking of waves messages

# unpacking of wave spectra messages of type W, i.e. FFT_LEN 1024

def unpack_wave_packet_W(bin_msg, print_decoded=True):
    assert len(bin_msg) == _BINARY_DECODER_WAVES_PACKET_W_LENGTH, "wave spectra message should have length {}".format(_BINARY_DECODER_WAVES_PACKET_W_LENGTH)

    # extract the data
    posix_timestamp = four_bytes_to_long(bin_msg[0:4])
    max_value = four_bytes_to_float(bin_msg[4:8])
    nbr_bins = _BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MAX_BIN - _BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MIN_BIN
    nbr_bytes = 2 * nbr_bins

    spectra_energies = struct.unpack('<'+nbr_bins*'H', bytes(bin_msg[8:8+nbr_bytes]))
    char_next_byte = byte_to_char(bin_msg[_BINARY_DECODER_WAVES_PACKET_W_LENGTH-1])

    assert char_next_byte == 'E', "wave packets are transmitted one at a time, expect 'E' for end at the end"

    if print_decoded:
        print("posix timestamp: {}".format(posix_timestamp))
        print("max energy: {}".format(max_value))
        print("encoded energies:")
        for crrt_energy in spectra_energies:
            print(crrt_energy)

    # make sense of the data
    datetime_fix = datetime.datetime.fromtimestamp(posix_timestamp)
    list_energy_values = [1.0 * crrt_uint16 * max_value / 65000 for crrt_uint16 in spectra_energies]

    wave_frequencies = [crrt_bin * _BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_SAMPLING_FREQ_HZ / _BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_NBR_SAMPLES_PER_SEGMENT for crrt_bin in range(_BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MIN_BIN, _BINARY_DECODER_WAVES_PACKET_W_SPECTRUM_MAX_BIN)]

    list_elevation_energies = []
    for (crrt_frq, crrt_energy) in zip(wave_frequencies, list_energy_values):
        crrt_omega = 2.0 * math.pi * crrt_frq
        crrt_omega_4 = crrt_omega * crrt_omega * crrt_omega * crrt_omega
        list_elevation_energies.append(crrt_energy / crrt_omega_4 * np.sqrt(1024) * math.sqrt(2.0) * math.pi)

    def compute_spectral_moment(list_frequencies, list_elevation_energies, order):
        list_to_integrate = [
            math.pow(crrt_freq, order) * crrt_energy for (crrt_freq, crrt_energy) in zip(list_frequencies, list_elevation_energies)
        ]

        moment = np.trapz(list_to_integrate, list_frequencies)

        return moment

    m0 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 0)
    m2 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 2)
    m4 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 4)

    waves_packet = Waves_Packet(
        datetime_fix=datetime_fix,
        list_frequencies=wave_frequencies,
        list_acceleration_energies=list_energy_values,
        list_elevation_normalized_energies=list_elevation_energies,
        m0=m0,
        m2=m2,
        m4=m4,
        hs=4*math.sqrt(m0),
        tp=math.sqrt(m2/m0),
        raw=binascii.hexlify(bin_msg)
    )

    if print_decoded:
        print("---------- decoded WAVE message ------------------------------")
        print("acceleration spectrum at posix {}, i.e. {}".format(posix_timestamp, datetime_fix))
        for crrt_bin_ind, (crrt_frq, crrt_energy) in enumerate(zip(wave_frequencies, list_energy_values)):
            print("bin ind {:03d}: frq {:.5f} Hz, energy {:.4e}".format(crrt_bin_ind + _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN, crrt_frq, crrt_energy))

        print("m0")
        waves_packet.m0
        print("m2")
        waves_packet.m2
        print("m4")
        waves_packet.m4
        print("hs")
        waves_packet.hs
        print("sqrt(m2/m0)")
        waves_packet.tp
        print("--------------------------------------------------------------")

    return (waves_packet, char_next_byte)


# case for FFT_LEN 2048; this is mostly a copy of the case 1024, TODO: refactor
def unpack_wave_packet_X(bin_msg, print_decoded=True):
    assert len(bin_msg) == _BINARY_DECODER_WAVES_PACKET_X_LENGTH, "wave spectra message should have length {}, got {}".format(_BINARY_DECODER_WAVES_PACKET_X_LENGTH, len(bin_msg))

    # extract the data
    posix_timestamp = four_bytes_to_long(bin_msg[0:4])
    max_value = four_bytes_to_float(bin_msg[4:8])
    nbr_bins = _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MAX_BIN - _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN
    print("nbr_bins: {}".format(nbr_bins))
    nbr_bytes = 2 * nbr_bins

    spectra_energies = struct.unpack('<'+nbr_bins*'H', bytes(bin_msg[8:8+nbr_bytes]))
    char_next_byte = byte_to_char(bin_msg[_BINARY_DECODER_WAVES_PACKET_X_LENGTH-1])

    assert char_next_byte == 'E', "wave packets are transmitted one at a time, expect 'E' for end at the end"

    if print_decoded:
        print("posix timestamp: {}".format(posix_timestamp))
        print("max energy: {}".format(max_value))
        print("encoded energies:")
        for crrt_energy in spectra_energies:
            print(crrt_energy)

    # make sense of the data
    datetime_fix = datetime.datetime.fromtimestamp(posix_timestamp)
    list_energy_values = [1.0 * crrt_uint16 * max_value / 65000 for crrt_uint16 in spectra_energies]

    wave_frequencies = [crrt_bin * _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_SAMPLING_FREQ_HZ / _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_NBR_SAMPLES_PER_SEGMENT for crrt_bin in range(_BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN, _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MAX_BIN) ]

    list_elevation_energies = []
    for (crrt_frq, crrt_energy) in zip(wave_frequencies, list_energy_values):
        crrt_omega = 2.0 * math.pi * crrt_frq
        crrt_omega_4 = crrt_omega * crrt_omega * crrt_omega * crrt_omega
        list_elevation_energies.append(crrt_energy / crrt_omega_4 * np.sqrt(2048) * math.sqrt(2.0) * math.pi)

    def compute_spectral_moment(list_frequencies, list_elevation_energies, order):
        list_to_integrate = [
            math.pow(crrt_freq, order) * crrt_energy for (crrt_freq, crrt_energy) in zip(list_frequencies, list_elevation_energies)
        ]

        moment = np.trapz(list_to_integrate, list_frequencies)

        return moment

    m0 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 0)
    m2 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 2)
    m4 = compute_spectral_moment(wave_frequencies, list_elevation_energies, 4)

    waves_packet = Waves_Packet(
        datetime_fix=datetime_fix,
        list_frequencies=wave_frequencies,
        list_acceleration_energies=list_energy_values,
        list_elevation_normalized_energies=list_elevation_energies,
        m0=m0,
        m2=m2,
        m4=m4,
        hs=4*math.sqrt(m0),
        tp=math.sqrt(m2/m0),
        raw=binascii.hexlify(bin_msg)
    )

    if print_decoded:
        print("---------- decoded WAVE message ------------------------------")
        print("acceleration spectrum at posix {}, i.e. {}".format(posix_timestamp, datetime_fix))
        for crrt_bin_ind, (crrt_frq, crrt_energy) in enumerate(zip(wave_frequencies, list_energy_values)):
            print("bin ind {:03d}: frq {:.5f} Hz, energy {:.4e}".format(crrt_bin_ind + _BINARY_DECODER_WAVES_PACKET_X_SPECTRUM_MIN_BIN, crrt_frq, crrt_energy))

        print("m0")
        waves_packet.m0
        print("m2")
        waves_packet.m2
        print("m4")
        waves_packet.m4
        print("hs")
        waves_packet.hs
        print("sqrt(m2/m0)")
        waves_packet.tp
        print("--------------------------------------------------------------")

    return (waves_packet, char_next_byte)

#--------------------------------------------------------------------------------
# decode a whole message with all its packets

def decode_message(hex_string_msg, print_info=True):
    if print_info:
        print("decode message: {}".format(hex_string_msg))

    bin_msg = binascii.unhexlify(hex_string_msg)

    list_decoded_packets = []
    list_valid_message_kinds = ['G', 'W', 'X']

    message_kind = byte_to_char(bin_msg[0])

    assert message_kind in list_valid_message_kinds, "valid message kinds are {}, got {}".format(list_valid_message_kinds, message_kind)

    if message_kind == 'G':
        if print_info:
            print("this is a GNSS message")

        nbr_gnss_fixes = one_byte_to_int(bin_msg[1: 2])

        message_metadata = GNSS_Metadata(nbr_gnss_fixes=nbr_gnss_fixes)

        start_of_packet = 2

        while True:
            decoded_packet, char_next_byte = unpack_gnss_packet(
                bin_msg[start_of_packet: start_of_packet + _BINARY_DECODER_GNSS_PACKET_LENGTH],
                print_decoded=print_info
            )
            list_decoded_packets.append(decoded_packet)
            start_of_packet += _BINARY_DECODER_GNSS_PACKET_LENGTH - 1

            if char_next_byte == 'E':
                break

    elif message_kind == 'W':
        if print_info:
            print("this is a waves message with FFT_LEN 1024")

        message_metadata = Waves_Metadata()

        # no metadata for now, the package starts right out at next byte and is to the end
        start_of_packet = 1

        decoded_packet, char_next_byte = unpack_wave_packet_W(
            bin_msg[start_of_packet: start_of_packet+_BINARY_DECODER_WAVES_PACKET_W_LENGTH],
            print_decoded=print_info
        )

        list_decoded_packets.append(decoded_packet)

        assert char_next_byte == 'E', "a wave message should have a single packet ending by char 'E'"

    elif message_kind == 'X':  # mostly a copy of the W wave message; refactor?
        if print_info:
            print("this is a waves message with FFT_LEN 2048")

        message_metadata = Waves_Metadata()

        # no metadata for now, the package starts right out at next byte and is to the end
        start_of_packet = 1

        decoded_packet, char_next_byte = unpack_wave_packet_X(
            bin_msg[start_of_packet: start_of_packet+_BINARY_DECODER_WAVES_PACKET_X_LENGTH],
            print_decoded=print_info
        )

        list_decoded_packets.append(decoded_packet)

        assert char_next_byte == 'E', "a wave message should have a single packet ending by char 'E'"

    else:
        raise(RuntimeError("message kind {} unknown or not implemented".format(message_kind)))

    return message_kind, message_metadata, list_decoded_packets

#--------------------------------------------------------------------------------
# simple CLI

@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option('--example', '-e', is_flag=True, help="Example of use")
@click.option('--module', is_flag=True, help="Help: how to use as a module")
@click.option('--decode-hex', '-d', default=None, help="The hex message to decode")
@click.option('--diagnostic', '-g', is_flag=True, help="Run a diagnostic of the module by running a few tests")
@click.option('--verbose', '-v', is_flag=True, help="turn on verbosity")
def cli(example, module, decode_hex, diagnostic, verbose):
    """
    Simple CLI for decoding tracker messages.
    This can be added as a command by copying into $HOME/bin and making executable.
    (you may need to $ source ~/.profile to activate)
    """

    if example:
        print("download messages directly from Rock7: https://rockblock.rock7.com/ > Messages > Export > Payload")
        print("for example decoding a GNSS message with 3 packets obtained there:")
        print("    $ ./decoder.py --decode-hex 4704469cb62a6007160f2ef5581e1246c2b62a60d3150f2e1b5b1e1246e8b62a6009110f2e2e8a1e1245")
        print("    > GNSS 2021-02-15 17:59:56, lat: +77.2740615, lon: +030.3978741")
        print("    > GNSS 2021-02-15 18:00:34, lat: +77.2740563, lon: +030.3979291")
        print("    > GNSS 2021-02-15 18:01:12, lat: +77.2739337, lon: +030.3991342")

    if decode_hex:
        message_kind, message_metadata, list_decoded_packets = decode_message(decode_hex, print_info=verbose)

        if message_kind == 'G':
            print("received a GNSS packet; packet last GNSS fix number since booting: {}".format(message_metadata.nbr_gnss_fixes))
            for crrt_packet in list_decoded_packets:
                print("GNSS {}, lat: {:+011.7f}, lon: {:+012.7f}".format(
                    crrt_packet.datetime_fix,
                    crrt_packet.latitude,
                    crrt_packet.longitude
                ))

        elif message_kind == 'W':
            print("received a wave acceleration spectrum packet with length 1024")

            datetime_timestamp = list_decoded_packets[0].datetime_fix
            list_frequencies = list_decoded_packets[0].list_frequencies
            list_energies = list_decoded_packets[0].list_acceleration_energies

            print("timestamp of spectrum acquisition start (duration: 20 mins): {}".format(datetime_timestamp))

            for crrt_ind, (crrt_frq, crrt_energy) in enumerate(zip(list_frequencies, list_energies)):
                print("bin ind {:03d}: frq {:.5f} Hz, i.e. period {:05.2f} s: energy {:.4e}".format(crrt_ind, crrt_frq, 1.0/crrt_frq, crrt_energy))

            print("m0")
            print(list_decoded_packets[0].m0)
            print("m2")
            print(list_decoded_packets[0].m2)
            print("m4")
            print(list_decoded_packets[0].m4)
            print("hs")
            print(list_decoded_packets[0].hs)
            print("sqrt(m2/m0)")
            print(list_decoded_packets[0].tp)

        elif message_kind == 'X':
            print("received a wave acceleration spectrum packet with length 2048")

            datetime_timestamp = list_decoded_packets[0].datetime_fix
            list_frequencies = list_decoded_packets[0].list_frequencies
            list_energies = list_decoded_packets[0].list_acceleration_energies

            print("timestamp of spectrum acquisition start (duration: 20 mins): {}".format(datetime_timestamp))

            for crrt_ind, (crrt_frq, crrt_energy) in enumerate(zip(list_frequencies, list_energies)):
                print("bin ind {:03d}: frq {:.5f} Hz, i.e. period {:05.2f} s: energy {:.4e}".format(crrt_ind, crrt_frq, 1.0/crrt_frq, crrt_energy))

            print("m0")
            print(list_decoded_packets[0].m0)
            print("m2")
            print(list_decoded_packets[0].m2)
            print("m4")
            print(list_decoded_packets[0].m4)
            print("hs")
            print(list_decoded_packets[0].hs)
            print("sqrt(m2/m0)")
            print(list_decoded_packets[0].tp)

    if module:
        print("this can be used as a module after adding to PYTHONPATH")
        print("    $ python3")
        print("    >>> from decoder import decode_message")
        print("    >>> message_kind, list_decoded_packets = decode_message(4704469cb62a6007160f2ef5581e1246c2b62a60d3150f2e1b5b1e1246e8b62a6009110f2e2e8a1e1245, print_info=False)")
        print("    >>> print(message_kind)")
        print("    G")
        print("    >>> for package in list_decoded_packets:")
        print("    ...     print(package")
        print("    ...")
        print("    GNSS_Packet(datetime_fix=datetime.datetime(2021, 2, 15, 17, 59, 56), latitude=77.2740615, longitude=30.3978741)")
        print("    GNSS_Packet(datetime_fix=datetime.datetime(2021, 2, 15, 18, 0, 34), latitude=77.2740563, longitude=30.3979291)")
        print("    GNSS_Packet(datetime_fix=datetime.datetime(2021, 2, 15, 18, 1, 12), latitude=77.2739337, longitude=30.3991342)")

    if diagnostic:
        print("we will now run a few diagnostic tests to check that the module is working fine...")
        print()
        print("TODO: add asserting to make sure it is not only working, but correct")
        print()

        print("##################################################################################")
        print("testing the GNSS decoding")
        print("testing against message: 4704469cb62a6007160f2ef5581e1246c2b62a60d3150f2e1b5b1e1246e8b62a6009110f2e2e8a1e1245")
        kind, meta, list_gnss = decode_message("4704469cb62a6007160f2ef5581e1246c2b62a60d3150f2e1b5b1e1246e8b62a6009110f2e2e8a1e1245", print_info=verbose)
        print()

        print("##################################################################################")
        print("testing the wave decoding, with 1024 FFT points")
        print("testing against message: 5774c43460a0c67e379c1398136e1c024fe8fd9c5b465dda183a14871fda1ab91972397932d22f2730472c5e12e725d21ed70cac16a010b50ce41a1d1b130d070d45")
        kind, meta, list_wave_data = decode_message("5774c43460a0c67e379c1398136e1c024fe8fd9c5b465dda183a14871fda1ab91972397932d22f2730472c5e12e725d21ed70cac16a010b50ce41a1d1b130d070d45", print_info=verbose)
        print()

        print("##################################################################################")
        print("testing the wave decoding, with 2048 FFT points")
        print("testing against message: 584f5c36608921f737e8fd9685fcad598235766f5de740824a7451222b303497626e2b451eaf15f739bd351646542aed2781298e3efc22901c8524311e61271129452a942aff28943e572b621c1a22861f6218d311080a8e127018581579212d19920eb6192922a214162672144225361df227612afc1b000045")
        kind, meta, list_wave_data = decode_message("584f5c36608921f737e8fd9685fcad598235766f5de740824a7451222b303497626e2b451eaf15f739bd351646542aed2781298e3efc22901c8524311e61271129452a942aff28943e572b621c1a22861f6218d311080a8e127018581579212d19920eb6192922a214162672144225361df227612afc1b000045", print_info=verbose)


if __name__ == "__main__":
    cli()

