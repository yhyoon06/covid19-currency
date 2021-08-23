import requests
import json
import pandas as pd
import time
import os


def grouped_daily(key, market, date, unadjusted="false"):
    """
    Get the daily open, high, low, and close (OHLC) for the entire forex or
    crypto markets. This response is saved in a txt file with the format of:
    {
    "status": "OK",
    "queryCount": 3,
    "resultsCount": 3,
    "adjusted": true,
    "results": [
        {
        "T": "C:CZKMXN",
        "v": 29035,
        "o": 0.98688,
        "c": 0.97531,
        "h": 0.9884522,
        "l": 0.97468,
        "t": 1599019200000
        },<...>
    ]
    }

    Args:
        key(string): polygon.io api key

        market(string): either "fx" or "crypto"

        date(string): date formatted in "yyyy-mm-dd"

        unadjusted(string): whether or not results adjusted for splits. See
        official api documentation for more details, but this project will use
        the default adjusted. "true" or "false".
    """

    # error handling
    assert (market == "fx") | (market == "crypto"), "Market must be \"fx\" or" \
                                                    " \"crypto\""

    url = f"https://api.polygon.io/v2/aggs/grouped/locale/global/market/" \
          f"{market}/{date}?unadjusted={unadjusted}&apiKey={key}"
    r = requests.get(url)
    expF = open(f"{market}_{date}", "a+")

    expF.write(json.dumps(r.json()))
    expF.close()


def aggregates(key, ticker, multiplier, timespan, from_, to,
               unadjusted="false",
               sort="asc", limit=5000, save=True):
    """
    Get aggregate bars for a currency pair over a given date range in custom
    time window sizes.

    This response is saved in the format of:
    {
    "ticker": "X:BTCUSD",
    "status": "OK",
    "queryCount": 2,
    "resultsCount": 2,
    "adjusted": true,
    "results": [
        {
        "v": 303067.6562332156,
        "vw": 9874.5529,
        "o": 9557.9,
        "c": 10094.75,
        "h": 10429.26,
        "l": 9490,
        "t": 1590984000000,
        "n": 1
        },<...>
    ],
    "request_id": "0cf72b6da685bcd386548ffe2895904a"
    }

    Args:
        key(string): polygon.io api key

        ticker(string): the desired currency pair. For forex pairs prepend the
        pair with "C:". For crypto pairs prepend "X:".

        multiplier(int): the amount of timespan

        timespan(string): either "minute","hour","day","day","week","month",
        "quarter", or "year"

        from_(string): beginning date formatted in "yyyy-mm-dd"

        to(string): ending date formatted in "yyyy-mm-dd"

        unadjusted(string): whether or not results adjusted for splits. See
        official api documentation for more details, but this project will
        use the default adjusted.

        sort(string): Sort results by timestamp. "asc" will return oldest
        results at top. "desc" will return newest results at top

        limit(int): Limits the number of base aggregates queried to create the
        aggregate results. Max 50000 and Default 5000. See official api
        documentation for more details.

        save(boolean): Return true if data should be saved in a file, else the
        json response will be returned.
    """

    # error handling
    assert (sort == "asc") | (sort == "desc"), "sort must be \"asc\" or " \
                                               "\"desc\""
    assert limit <= 50000, "limit must be <50000"
    # later check date valid

    assert (ticker[0:2] == "C:") | (ticker[0:2] == "X:"), "ticker must start" \
                                                          " with \"C:\" for" \
                                                          " forex or " \
                                                          "\"X:\" for" \
                                                          " crypto"

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/" \
          f"{multiplier}/{timespan}/{from_}/{to}?unadjusted={unadjusted}&" \
          f"sort={sort}&limit={limit}&apiKey={key}"
    result = requests.get(url)
    r = result.json()

    # Checks to make sure polygon.io api didn't have error
    try:
        assert r["status"] == "OK"
    except AssertionError:
        print(f"Error occurred from {from_} to {to} for {ticker}")
        exit(1)

    if save is True:
        expF = open(f"{ticker[2:]}_{from_}_{to}_{multiplier}_{timespan}",
                    "a+")
        expF.write(json.dumps(r))
        expF.close()
        pass
    else:
        return r


def multi_aggregates(key, ticker, multiplier, timespan, from_, to,
                     unadjusted="false"):
    """
    Essentially, this runs aggregate many times. Get aggregate bars for a
    cryptocurrency pair over a given date range in custom time window sizes.
    However, we do not have to deal with a limit like normal aggregate. Stores
    data in csv format in crypto_forex_data

    Result in form of: 
    {"{ticker[2:]}_{from_}_{to}": [<...>]}
    
    Args:
        key(string): polygon.io api key

        ticker(string): the desired currency pair. For forex pairs prepend the
        pair with "C:". For crypto pairs prepend "X:".

        multiplier(int): the amount of timespan

        timespan(string): either "minute","hour","day","day","week","month",
        "quarter", or "year"

        from_(string): beginning date formatted in "yyyy-mm-dd"

        to(string): ending date formatted in "yyyy-mm-dd"

        unadjusted(string): whether or not results adjusted for splits. See
        official api documentation for more details, but this project will
        use the default adjusted.

        sort(string): Sort results by timestamp. "asc" will return oldest
        results at top. "desc" will return newest results at top
    """
    
    name = f"{ticker[0]}_{ticker[2:]}_{from_}_{to}_{multiplier}_{timespan}"
    directory = "crypto_forex_data" 

    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

    expF = open(f"{directory}/{name}.json", "a+")

    incomplete_data = False
    empty = True
    expF.write("{" + '"' + name + '": [')

    # Note: Need to change freq if not minute timespan. 
    dateRange = pd.date_range(from_, to, freq="M")
    for i in range(1,len(dateRange)):
        dateB = dateRange[i - 1].strftime("%Y-%m-%d")
        dateE = dateRange[i].strftime("%Y-%m-%d")
        aggResult = aggregates(key, ticker, multiplier, timespan, dateB,
                               dateE, unadjusted=unadjusted, save=False,
                               limit=50000)
        if aggResult["resultsCount"] == 0:
            incomplete_data = True
        else:
            empty = False
            r = json.dumps(aggResult["results"])

            if i != len(dateRange) - 1:
                expF.write(r[1:len(r)-1] + ", ")
            else:
                expF.write(r[1:len(r)-1])

    expF.write("]}")
    expF.close()
    if empty is True:
        os.remove(f"{directory}/{name}.json")
        raise ValueError("polygon.io does not support that pair")
    elif incomplete_data is True:
        print(name + " finished, but data incomplete")
    else: 
        print(name + " finished")


def bigPull(key, multiplier, timespan, start, end):
    """
    This function pulls all of the data at a given timespan from our projects
    selected currency pairs over a given range of time. This data will be saved
    in a directory called

    Args:
        key(string): polygon.io API key
        multiplier(int): the size of timespan multiplier
        timespan(string): the size of time window
            options: "minute","hour","day","week","month",or "year"
        start(string): beginning date formatted in "yyyy-mm-dd"
        end(string): ending date formatted in "yyyy-mm-dd"

    """
    tik = time.perf_counter()

    crypto_list = [
            "X:BTCUSD",
            "X:ETHUSD",
            "X:USDTUSD",
            "X:BNBUSD",
            "X:ADAUSD",
            "X:XRPUSD",
            "X:LTCUSD",
            "X:LINKUSD",
            "X:USDCUSD",
            "X:BCHUSD",
            "X:XLMUSD",
            "X:DOGEUSD"]

    for i in crypto_list:
        try:
            multi_aggregates(key, f"{i}", multiplier, timespan, start, end)
            time.sleep(30)
        except:
            print(f"{i} failed")
    
    base = "USD"

    na_fx = [
        "CAD",
        "MXN"
    ]
    sa_fx = [
        "BRL",
        "ARS",
        "BOB",
        "CLP",
        "COP"
    ]
    ww_fx = [
        "EUR",
        "AUD",
        "NZD"
    ]
    eu_fx = [
        "GBP",
        "SEK",
        "CHF",
        "HUF",
        "RUB"
    ]
    as_fx = [
        "JPY",
        "CNY",
        "HKD",
        "KRW",
        "INR"
    ]
    af_fx = [
        "ZAR",
        "LYD",
        "TND",
        "MAD",
        "GHS"
    ]
    all_fx = na_fx + sa_fx + ww_fx + eu_fx + as_fx + af_fx

    for i in all_fx:
        try:
            multi_aggregates(key, f"C:{i}{base}", multiplier, timespan,
                             start, end)
            time.sleep(30)
            pass
        except:
            try:
                multi_aggregates(key, f"C:{base}{i}", multiplier, timespan,
                                 start, end)
                time.sleep(30)
            except Exception as e:
                print(e)

    tok = time.perf_counter()
    print(f"Downloaded the data in {(tok - tik)/60} minutes")
