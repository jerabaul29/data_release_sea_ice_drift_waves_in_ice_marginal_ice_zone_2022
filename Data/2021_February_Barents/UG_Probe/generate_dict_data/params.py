import datetime

import os
import time

os.environ["TZ"] = "UTC"
time.tzset()


# start of time after de-icing in the open water
# when going in the open water at the start of the cruise, there was a lot of icing, and the signal was quickly lost. The, we de-iced and things got better

# start of time when boat in the ice
# from now on, need to look at signal when the boat is still, otherwise we get annoyed by ice moving in and out of the probe
datetime_start_ice = datetime.datetime(2021, 2, 16, 16, 0, 0)

# end of time when boat in the ice
# from now on, no more need to look at the signal when the boat is still
datetime_end_ice = datetime.datetime(2021, 2, 25, 14, 0, 0)

# start of icing in the open water
# after going in the open water, the sensor re-iced quite quickly