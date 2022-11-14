These are the data from the instruments v2021-a / OpenMetBuoy. The data are of two kinds: GPS and wave spectra. Content of the folder:

- the scripts in the ```generate_dict_data``` folder parse all the binary transmissions and put these into a dictionary
- the scripts in the ```generate_nc_dataset``` folder perform a bit of quality check on the dict data, turn the python dict into a standardised netCDF file, and offer a bit of plotting utilities for the corresponding data.
