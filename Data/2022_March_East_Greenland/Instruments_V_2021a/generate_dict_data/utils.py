from icecream import ic
import numpy as np

# a function to return an ordered list of keys for which in the right time interval, ordered by time
def sort_dict_keys_by_date(dict_in):
    list_key_datetime = []

    for crrt_key in dict_in:
        crrt_datetime = dict_in[crrt_key]['datetime']
        list_key_datetime.append((crrt_key, crrt_datetime))

    sorted_keys = sorted(list_key_datetime, key=lambda x: x[1])
    sorted_keys = [x for (x, y) in sorted_keys]

    return(sorted_keys)


# a function to return only the keys that correspond to a given kind of data (status / spectrum)

def get_index_of_first_list_elem_greater_starting_smaller(list_in, value):
    """If the list_in first elem is larger than value, return None; if list_in has no
    element larger than value, return None; else, return the index of the first elem larger
    than value."""
    if list_in[0] > value:
        return None

    for ind, crrt_element in enumerate(list_in):
        if crrt_element > value:
            return ind

    return None


def sliding_filter_nsigma(np_array_in, nsigma=5.0, side_half_width=2):
    """Perform a sliding filter, on points of indexes
    [idx-side_half_width; idx+side_half_width], to remove outliers. I.e.,
    the [idx] point gets removed if it is more than nsigma deviations away
    from the mean of the whole segment.

    np_array_in should have a shape (nbr_of_entries,)"""

    np_array = np.copy(np_array_in)
    array_len = np_array.shape[0]

    middle_point_index_start = side_half_width
    middle_point_index_end = array_len - side_half_width - 1

    for crrt_middle_index in range(middle_point_index_start, middle_point_index_end+1, 1):
        crrt_left_included = crrt_middle_index - side_half_width
        crrt_right_included = crrt_middle_index + side_half_width
        crrt_array_data = np.concatenate([ np_array_in[crrt_left_included:crrt_middle_index], np_array_in[crrt_middle_index+1:crrt_right_included+1] ])
        mean = np.mean(crrt_array_data)
        std = np.std(crrt_array_data)
        if np.abs(np_array[crrt_middle_index] - mean) > nsigma * std:
            print("found outlier")
            np_array[crrt_middle_index] = np.nan

    return np_array
