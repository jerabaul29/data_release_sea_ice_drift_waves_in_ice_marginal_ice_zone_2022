To use this code, run:

- ```script_put_csv_to_time_base.py```: analyze the raw data logged by the probes system, and put it into a common time base, dumping as pkl files.
- ```script_create_boat_position_data.py```: look at the boat GPS data to find times when the boat was immobile, and dump the time segments when was immobile as a pkl file.
- ```explore_time_delta_boat_imu.py```: check that there is no time shift between the boat GPS data and the UG records, i.e. that both are in UTC; also find the promising segments of data both in the ice and in the open water.
- ```script_dump_valid_segments.py```: dump the valid segments of data

Dead ends:

- ```script_select_valid_data_entries.py```: look at the data entries and select the valid ones. This is too much manual work, discard, and use the immobile positions instead.

Ongoing:


TODOs:
- data in the open water: look at, find, and use for validation
- data in the ice when immobile: look at, find, and use as product of this system
