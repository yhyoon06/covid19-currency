import sys
import pandas as pd
import json
import os
import time


def main(pair_data_file):
    """
    This function converts json files to new line separated json files and
    saves the result in a file in directory "line_separated"
    Args:
        pair_data_file: the data file to convert
    """
    tic = time.perf_counter()

    no_type_name = pair_data_file[0:len(pair_data_file) - 5]
    pair_name = f"{no_type_name.split('_')[0]}:{no_type_name.split('_')[1]}"
    print(f"{pair_name} data conversion started")

    f = open(pair_data_file)

    directory = "line_separated"
    try:
        os.mkdir(directory)
    except Exception as e:
        pass
    filename = f"{directory}/{no_type_name}"
    of = open(filename, "a+")

    data = json.load(f)
    for i in data[no_type_name]:
        try:
            point = {
                    'p': pair_name,
                    't': i['t'],
                    'v': i['v'],
                    'o': i['o'],
                    'c': i['c'],
                    'h': i['h'],
                    'l': i['l'],
                    'n': i['n']
                    }
            json.dump(point, of)
            of.write("\n")
        except Exception as e:
            print(e)

    f.close()
    of.close()
    toc = time.perf_counter()
    print(f"Converted {pair_name} data to new line separated json in "
          f"{(toc -tic)/60} minutes")


if __name__ == "__main__":
    main(sys.argv[1])
