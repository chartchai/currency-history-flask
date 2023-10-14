import requests
import json
import redis
from flask import Flask, request

app = Flask(__name__)
REDIS_URL = "redis://red-cklgniou1l6c73bk7g60:6379"
# REDIS_URL = 'redis://default:wFUMe5zGsP6X8NaECkSadQVs2zQCtrjL@redis-10285.c292.ap-southeast-1-1.ec2.cloud.redislabs.com:10285'

@app.route('/')
def hello_world():
    based = request.args.get('base')
    symbol = request.args.get('symbols')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ret = get_currency_history(based, symbol, start_date, end_date)
    return ret


def get_currency_history(based, symbol, start_date, end_date):
    key = {
        'based': based,
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date
    }
    cache = get_cache(key)
    if cache is not None:
        return cache
    api_key = '6bf3e73945-a4eac4a4e7-s2g7gx'
    url = "https://api.fastforex.io/time-series?" \
          "from={}&to={}&start={}&end={}" \
          "&api_key={}".format(based, symbol, start_date, end_date, api_key)

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)

    res = json.loads(response.text)

    rates = res['results']
    rate_list = rates[symbol]
    return_rate = {}
    for date, rate in rate_list.items():
        return_rate[date] = {symbol: rate}
    ret = {"rates": return_rate}
    set_cache(key, ret)
    return ret


def get_cache(key):
    r = redis.from_url(REDIS_URL)

    try:
        cache = r.get(str(key)).decode('utf-8')
        cache = cache.replace("'", "\"")
        print('cache: ', cache)

        cache_dic = json.loads(cache)
        return cache_dic
    except AttributeError:
        return None


def set_cache(key, result):
    r = redis.from_url(REDIS_URL)
    r.set(str(key), str(result))
    return result


if __name__ == '__main__':
    output = get_currency_history('THB', 'USD', '2023-01-01', '2023-01-08')
    print(output)
