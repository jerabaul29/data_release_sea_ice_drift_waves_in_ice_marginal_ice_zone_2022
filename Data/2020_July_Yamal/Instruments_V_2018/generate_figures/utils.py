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
