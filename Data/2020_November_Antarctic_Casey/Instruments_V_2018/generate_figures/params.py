from datetime import datetime

# the full data extent
# time_start = datetime(year=2021, month=2, day=15, hour=0, tzinfo=None)  # the beginning of the cruise
# time_end = datetime(year=2021, month=4, day=3, hour=0, tzinfo=None)  # long enough later that all stopped to work

# slightly reduced data extent for better looking plot
time_start = datetime(year=2020, month=10, day=12, hour=0, tzinfo=None)  # the beginning of the cruise
time_end = datetime(year=2020, month=11, day=11, hour=0, tzinfo=None)  # long enough later that all stopped to work

# None to use all available instruments, list of instruments like in ```list_instruments = ['RockBLOCK 18958', 'RockBLOCK 18715', 'RockBLOCK 17330']``` to use subset
list_instruments = ["RockBLOCK 17328 - Antarctica-AAD",
                    "RockBLOCK 18655 - Antarctica-AAD",
                   ]

