# data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022

The repository for the code and data corresponding to our data release paper for waves in ice measurements.

Unless explicitly mentioned otherwise, all the python code is python3, and the target system for running the scripts is linux (the code should work on any modern Ubuntu release with the proper packages installed).

There is quite a lot of code repetition between the deployments. We decided to not "fix" this because this way the code in each folder can be run directly, without the need to "install / add to path" for a package, and it is easier to tweak each individual script to the specificity of the corresponding deployment.

If you use any of these data, please cite our paper:

```
Rabault, J., Müller, M., Voermans, J. et al.
A dataset of direct observations of sea ice drift and waves in ice.
Sci Data 10, 251 (2023).
https://doi.org/10.1038/s41597-023-02160-9
```

- The published paper is open access at Nature Scientific Dataset: https://www.nature.com/articles/s41597-023-02160-9 .
- The manuscript is available on ResearchGate at: https://www.researchgate.net/publication/364652443_A_dataset_of_direct_observations_of_sea_ice_drift_and_waves_in_ice .
- The manuscript is also available on this repository at: https://github.com/jerabaul29/data_release_sea_ice_drift_waves_in_ice_marginal_ice_zone_2022/blob/master/article_preprint.pdf .
- The data are also hosted as a set of netCDF-CF files following the FAIR principles at: https://doi.org/10.21343/AZKY-0X44 .

In case of questions, please use the issue tracker of this repository to discuss.

We will periodically release extensions to this dataset. If you have some data you may want to release, consider contacting us to join our next data release paper, and / or index your open data at https://github.com/jerabaul29/meta_overview_sea_ice_available_data to help make it easy to find :) .

The name of this repository reflects the fact that: i) we focus on sea ice drift and waves in ice in the marginal ice zone, ii) the data release preparation work took place in 2022.

If you need more information about the instruments used for collecting data, see for the open source instruments the full open source hardware and firmware and post processing tools:

- OpenMetBuoy (OMB / v2021): https://github.com/jerabaul29/OpenMetBuoy-v2021a
- instrument v2018: https://github.com/jerabaul29/LoggerWavesInIce_InSituWithIridium

This repository only contains the data that were transmitted over iridium, for the deployments where the instruments were not recovered. For deployments where the raw data were recovered, typically several GB of data per instrument were generated, and this is too much data volume for storing on github. For these deployments, see the netCDF files at: https://adc.met.no/datasets/10.21343/azky-0x44 
