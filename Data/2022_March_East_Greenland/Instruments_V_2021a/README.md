These are the data from the instruments v2021.a. These instruments are prototypes of the follow up design to the v2018. These are based on the Sparkfun Artemis Global Tracker, and the BNO08x IMU. The BNO08x proved to be not as good as good an IMU as we had hoped, and also quite troublesome to communicate with, so in the future we will not use the BNO08x any longer. The data are of two kinds: GPS and wave spectra. Content of the folder:

- the scripts in the ```generate_dict_data``` folder parse all the binary transmissions and put these into a dictionary
- the scripts in the ```generate_nc_dataset``` folder perform a bit of quality check on the dict data, turn the python dict into a standardised netCDF file, and offer a bit of plotting utilities for the corresponding data.
