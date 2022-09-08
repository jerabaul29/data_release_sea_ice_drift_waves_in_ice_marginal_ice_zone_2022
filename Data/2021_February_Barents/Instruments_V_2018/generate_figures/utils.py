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

