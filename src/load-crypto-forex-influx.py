from influxdb import InfluxDBClient
import json
import time
import sys
import pandas as pd


def convertTime(t):
    return pd.to_datetime(t, unit='ms', utc=True)


def main(pair_data_file, host, username, password):
    tik = time.perf_counter()
    client = InfluxDBClient(host=host, username=username,
                            password=password, port=8086,
                            database="crypto_forex")

    # Must have 'crypto_forex' database 
    try:
        d = client.get_list_database()
        assert str(d) == "[{'name': '_internal'}, {'name': 'crypto_forex'}]"
        print("Successfully connected to DB")
    except AssertionError:
        print("InfluxDB not configured correctly. Databases listed below")
        print(client.get_list_database())
        quit()

    # Going point by point is too slow, so we need to upload in batches
    json_body = []
    count = 0

    f = open(pair_data_file)
    for line in f:
        try:
            tick = json.loads(line)
            json_body.append({
                "measurement": "crypto_forex",
                "tags": {
                    "pair": tick['p']
                },
                "time": convertTime(tick['t']),
                "fields": {
                    'p': tick['p'],
                    'v': float(tick['v']),
                    'o': float(tick['o']),
                    'c': float(tick['c']),
                    'h': float(tick['h']),
                    'l': float(tick['l']),
                    'n': float(tick['n'])
                }
            })
            count = count + 1
        except Exception as e:
            print(e)
            pass

        if count % 10000 == 0:
            try:
                client.write_points(points=json_body,
                                    time_precision='ms')
                count = 0
                json_body = []
            except Exception as e:
                print(e)
                pass

    client.write_points(json_body)
    tok = time.perf_counter()
    f.close()
    print(f"{pair_data_file} loaded in {(tok - tik)/60} minutes")
 

if __name__ == "__main__":
    host = ''
    username = ''
    password = ''
    main(sys.argv[1], host, username, password)

