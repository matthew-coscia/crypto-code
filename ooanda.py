from unicodedata import decimal
import requests, datetime, time, hmac, hashlib, json, base64
import pandas as pd
import http.client
import numpy as np
import math
API_KEY = ""
link = "https://api-fxtrade.oanda.com"

def main():
    header = {
        "Authorization": "Bearer "
        }
    conn = http.client.HTTPSConnection('api-fxtrade.oanda.com')
    method = "GET"
    path = "/v3/accounts/001-001-8986741-001/instruments"
    print(path)
    conn.request(method, path, '', header)
    res = conn.getresponse()
    print(res)
    data = res.read()
    data = json.loads(data)
    return data

def find_orderBook(instrument):
    instrument = str(instrument)
    timestamp = str(int(time.time()))
    header = {
        "Authorization": "",
        "Accept-Datetime-Format": "UNIX"
        }
    conn = http.client.HTTPSConnection('api-fxtrade.oanda.com')
    method = "GET"
    path = "/v3/instruments/" + instrument + "/orderBook"
    conn.request(method, path, '', header)
    res = conn.getresponse()
    print(path)
    data = res.read()
    data = json.loads(data)
    return data