# Readme load information

How to load information from the pre-processed dicts:

- position information

```python
[ins] In [1]: import pickle as pkl                                                                                                                                                                

[ins] In [2]: with open("./dict_data_each_logger_status.pkl", "rb") as fh: 
         ...:     dict_data_each_logger = pkl.load(fh) 
         ...:                                                                                                                                                                                     

[ins] In [3]: dict_data_each_logger.keys()                                                                                                                                                        
Out[3]: dict_keys(['RockBLOCK 18950', 'RockBLOCK 13314', 'RockBLOCK 18954', 'RockBLOCK 18958', 'RockBLOCK 18715', 'RockBLOCK 17330'])

[ins] In [4]: dict_data_each_logger["RockBLOCK 17330"].keys()                                                                                                                                     
Out[4]: dict_keys(['datetime', 'GPS', 'File', 'VBat'])

[ins] In [6]: dict_data_each_logger["RockBLOCK 17330"]["GPS"][0]                                                                                                                                                                                                                                                                                                                              
Out[6]: <RMC(timestamp=datetime.time(13, 4, 5), status='A', lat='8156.0628', lat_dir='N', lon='01020.0092', lon_dir='E', spd_over_grnd=0.4, true_course=243.76, datestamp=datetime.date(2020, 8, 27), mag_variation='', mag_var_dir='') data=['A']>

[ins] In [7]: dict_data_each_logger["RockBLOCK 17330"]["GPS"][0].longitude                                                                                                                                                                                                                                                                                                                    
Out[7]: 10.333486666666667

[ins] In [8]: dict_data_each_logger["RockBLOCK 17330"]["GPS"][0].latitude                                                                                                                                                                                                                                                                                                                     
Out[8]: 81.93438

[ins] In [9]: dict_data_each_logger["RockBLOCK 17330"]["GPS"][0].datetime                                                                                                                                                                                                                                                                                                                     
Out[9]: datetime.datetime(2020, 8, 27, 13, 4, 5)

[ins] In [11]: len(dict_data_each_logger["RockBLOCK 17330"]["GPS"])                                                                                                                                                                                                        
Out[11]: 166
```

For more information about how these data can be used, see: ```script\_show\_status.py```.

- wave characteristics information:

```python
[ins] In [1]: import pickle as pkl                                                                                                                                                                                                                                         

[ins] In [2]: with open("./dict_data_each_logger_wave.pkl", "br") as fh: 
         ...:     dict_data_each_logger = pkl.load(fh) 
         ...:                                                                                                                                                                                                                                                              

[ins] In [3]: dict_data_each_logger.keys()                                                                                                                                                                                                                                 
Out[3]: dict_keys(['RockBLOCK 18950', 'RockBLOCK 13314', 'RockBLOCK 18954', 'RockBLOCK 18958', 'RockBLOCK 18715', 'RockBLOCK 17330'])

[ins] In [4]: dict_data_each_logger["RockBLOCK 17330"].keys()                                                                                                                                                                                                              
Out[4]: dict_keys(['datetime', 'freq', 'a0_proc', 'R_proc', 'SWH', 'Hs', 'T_z0', 'T_z', 'Hs_proc', 'T_z_proc', 'T_c_proc', 'T_p_proc', 'aggregated_a0_proc', 'aggregated_R_proc'])

[ins] In [5]: dict_data_each_logger["RockBLOCK 17330"]["SWH"]                                                                                                                                                                                                              
Out[5]: 
[0.05481625348329544,
[...]
[ins] In [6]: dict_data_each_logger["RockBLOCK 17330"]["datetime"]                                                                                                                                                                                                         
Out[6]: 
[datetime.datetime(2020, 8, 27, 13, 11, 21),
 datetime.datetime(2020, 8, 27, 16, 36, 7),
[...]
[ins] In [10]: len(dict_data_each_logger["RockBLOCK 17330"]["datetime"])                                                                                                                                                                                                   
Out[10]: 201
[ins] In [15]: len(dict_data_each_logger["RockBLOCK 17330"]["SWH"])                                                                                                                                                                                                        
Out[15]: 201
[ins] In [16]: len(dict_data_each_logger["RockBLOCK 17330"]["freq"][0])                                                                                                                                                                                                    
Out[16]: 25
[ins] In [17]: dict_data_each_logger["RockBLOCK 17330"]["aggregated_a0_proc"].shape                                                                                                                                                                                        
Out[17]: (201, 25)
```

For more information, see ```script\_show\_Hs_Tp.py```.

