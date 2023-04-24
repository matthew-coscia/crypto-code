from unicodedata import decimal
import requests, datetime, time, hmac, hashlib, json, base64
import pandas as pd
import http.client
import numpy as np
import math

combinations_for_paths = 4
checking_limits = 1
currency_needed_big = 100.0
database_sorted = []
API_KEY = "zqiKZAp590y0Cly6"
API_SECRET = "UjkmK9DuKDdscs4bH4x9YGg6RIHbxKpl"
URL = "https://coinbase.com/api/v3/brokerage/products"

API_KEY_FOR_WALLET = 'C1OL9YT8ybtqYzSg'
API_SECRET_FOR_WALLET = 'MumvKyk19ffFd1pHbplgbpsfloVVCwbC'


def round_up(n, decimals):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def put_together():
    rounding = 10
    counter = 0
    test_count = 0
    account_list_init = list_accounts()
    initial_balance = float(find_account(account_list_init, 'USD')['value'])
    #initialize money
    money_count = currency_needed_big
    currency = "USD"
    #find the buy order
    print("Finding Combinations....")
    buy_order_x = main()
    for_reference = buy_order_x[0]
    buy_order = buy_order_x[1]
    print(for_reference[0]['money'])
    print("Starting Transactions....")
    counter_loop = len(buy_order)
    while counter < counter_loop:
        i = buy_order[counter]
        print(money_count)
        if money_count == 0.0:
            account_list = list_accounts()
            account = find_account(account_list, i['currency'])
            if float(account['value']) > 0.000000001:
                print("Skipping...")
                counter = counter + 1
                continue
        account_list = list_accounts()
        account = find_account(account_list, i['currency'])
        money_count = float(account['value'])
        if currency == 'USD':
            money_count = 100.0
        order_confirm = send_orders(i['product_id'], i['type'], str(money_count))
        print(i)
        print(order_confirm)
        if order_confirm['success'] != True:
            money_count = round(money_count, rounding)
            rounding = rounding - 1
            continue
        if order_confirm['success']:
            rounding = 10
            currency = i['currency']
            account_list = list_accounts()
            account = find_account(account_list, currency)
            if type(account) == str:
                print("could not find account")
                time.sleep(3)
                continue
            counter = counter + 1
            print("Starting Next Transaction....")
            time.sleep(3)
        money_count = float(account['value'])
        if order_confirm['success'] == False:
            print("transaction failure, restarting current transaction...")
            time.sleep(3)
            break
    accounts_listed_late = list_accounts()
    usd_account_value = float(find_account(accounts_listed_late, 'USD')['value'])
    print(for_reference[0]['money'])
    print(usd_account_value - initial_balance)
    return for_reference

def sort_for_limits(list):
    final_list = []
    for x in list:
        if x['limit_only'] == True:
            final_list.append(x['product_id'])
    return final_list

def sortLimits(newList, full_list):
    final_list = []
    count = 0
    for i in newList:
        count = 0
        for k in full_list:
            if k in i['id']:
                count = 1
        if count == 0:
            final_list.append(i)
    return final_list


def main():
    keeper = 0
    while keeper == 0:
        filtered_sales = []
        #gather data
        x = find_shit()
        full_list = x[1]
        #sort data
        full_list = sort_for_limits(full_list)
        y = sort_da_list(x[2])
        #sort by balance increase
        newList = sorted(y, key=lambda d: float(d['money']), reverse=True)
        print(len(newList))
        newList = testCurrency(newList)
        print(len(newList))
        newList = sortLimits(newList, full_list)
        print(len(newList))
        try:
            holder = newList[0]
            keeper = 1;
        except:
            return [None, None]
    best_opt = get_orders(newList[0])
    results_confirmed = confirm_results(best_opt)
    final_sales = generate_buy_sale(results_confirmed)
    return [newList, final_sales, full_list]

def get_orders_history():
    link_for_get = 'https://api.coinbase.com/api/v3/brokerage/orders/historical/batch?limit=100'
    unix_get = str(int(time.time()))
    path = "/api/v3/brokerage/orders/historical/batch"
    sign2_get = unix_get + "GET" + path.split("?")[0] + ''
    sign_get = hmac.new(API_SECRET.encode('utf-8'), sign2_get.encode('utf-8'), digestmod=hashlib.sha256).digest()
    head = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": sign_get.hex(),
        "CB-ACCESS-TIMESTAMP": unix_get,
        }
    x_get = requests.get(link_for_get, headers=head)
    return x_get.json()

def send_orders(product_id, side, cash):
        info = get_market_values(product_id)
        order_id = np.random.randint(2**31)
        if info['limit_only'] == False:
            conn = http.client.HTTPSConnection('api.coinbase.com')
            method = "POST"
            path = "/api/v3/brokerage/orders"
            if 'BUY' in side:
                payload = "{\"client_order_id\":" + "\"" + str(order_id) + "\"" + ",\"product_id\":" + "\"" + product_id + "\"" + ",\"side\":" + "\"" + side + "\"" + ",\"order_configuration\": {\"market_market_ioc\": {\"quote_size\":" + "\"" + cash + "\"" + "}}}"
            if "SELL" in side:
                payload = "{\"client_order_id\":" + "\"" + str(order_id) + "\"" + ",\"product_id\":" + "\"" + product_id + "\"" + ",\"side\":" + "\"" + side + "\"" + ",\"order_configuration\": {\"market_market_ioc\": {\"base_size\":" + "\"" + cash + "\"" + "}}}"
            timestamp = str(int(time.time()))
            message = timestamp + method + path.split('?')[0] + str(payload)
            signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
            headers = {
                'CB-ACCESS-KEY': API_KEY,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-SIGN': signature,
                'accept': 'application/json'
                }
            conn.request(method, path, str(payload), headers)
            res = conn.getresponse()
            data = res.read()
            print(data)
            data = json.loads(data)
        if info['limit_only'] == True:
            conn = http.client.HTTPSConnection('api.coinbase.com')
            method = "POST"
            path = "/api/v3/brokerage/orders"
            if 'BUY' in side:
                payload = make_json(product_id, side, order_id, info['price'], cash)
            if "SELL" in side:
                payload = make_json(product_id, side, order_id, info['price'], cash)
            print(payload)
            timestamp = str(int(time.time()))
            message = timestamp + method + path.split('?')[0] + str(payload)
            signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
            headers = {
                'CB-ACCESS-KEY': API_KEY,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-SIGN': signature,
                'accept': 'application/json'
                }
            conn.request(method, path, str(payload), headers)
            res = conn.getresponse()
            data = res.read()
            data = json.loads(data)
        return data

def make_json(product_id, side, order_id, price, cash):
    if "BUY" in side:
        payload = json.dumps({
            "client_order_id": str(order_id),
            "product_id": str(product_id),
            "side": str(side),
            "order_configuration": {
                "limit_limit_gtc": {
                    "limit_price": price,
                    "post_only": False,
                    "base_size": cash
                    }
                }
            })
    if "SELL" in side:
        payload = json.dumps({
            "client_order_id": str(order_id),
            "product_id": str(product_id),
            "side": str(side),
            "order_configuration": {
                "limit_limit_gtc": {
                    "limit_price": price,
                    "post_only": False,
                    "base_size": cash
                    }
                }
            })
    return payload

def find_account(data, currency):
    holder = 0
    for i in data:
        test = str(i['currency'])
        if currency == test:
            holder = 1
            return i
    if holder == 0:
        return "can't find currency"

def list_accounts():
    final_dict = []
    url_list = "https://api.coinbase.com/api/v3/brokerage/accounts"
    conn = http.client.HTTPSConnection('api.coinbase.com')
    method = "GET"
    path = "/api/v3/brokerage/accounts"
    timestamp = str(int(time.time()))
    message = timestamp + method + path.split('?')[0]
    signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    headers = {
        'CB-ACCESS-KEY': API_KEY,
        'CB-ACCESS-TIMESTAMP': timestamp,
        'CB-ACCESS-SIGN': signature,
        'accept': 'application/json'
        }
    conn.request(method, path + "?limit=200", '', headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    data = data['accounts']
    for i in data:
        final_dict.append(i['available_balance'])
    return final_dict

def generate_buy_sale(list_of_confirms):
    currency_type = 'USD'
    currency_needed = currency_needed_big
    count = 0
    for i in list_of_confirms:
        if currency_type == i['base']:
            currency_needed = (currency_needed - (currency_needed * 0.006)) * float(i['price'])
            currency_type = i['quote']
            list_of_confirms[count] = {'product_id': i['product_id'], 'price': i['price'], 'base': i['base'], 'quote': i['quote'], 'bankroll': currency_needed, 'currency': currency_type, 'type': 'SELL'}
            count = count + 1
            continue
        if currency_type == i['quote']:
            currency_needed = (currency_needed - (currency_needed * 0.006)) / float(i['price'])
            currency_type = i['base']
            list_of_confirms[count] = {'product_id': i['product_id'], 'price': i['price'], 'base': i['base'], 'quote': i['quote'], 'bankroll': currency_needed, 'currency': currency_type, 'type': 'BUY'}
            count = count + 1
            continue
    return list_of_confirms

def confirm_results(list_pairs):
    helper_list = []
    for i in list_pairs:
        marketTemp = get_market_values(i)
        helper_list.append({'product_id': marketTemp['product_id'], 'price': marketTemp['price'], 'base': marketTemp['base_currency_id'], 'quote': marketTemp['quote_currency_id']})
    return helper_list


def get_market_values(pair):
    url_for_product = 'https://api.coinbase.com/api/v3/brokerage/products/' + pair
    unix_market = str(int(time.time()))
    sign2_market = unix_market + "GET" + "/api/v3/brokerage/products/" + pair + ''
    sign_market = hmac.new(API_SECRET.encode('utf-8'), sign2_market.encode('utf-8'), digestmod=hashlib.sha256).digest()
    head = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": sign_market.hex(),
        "CB-ACCESS-TIMESTAMP": unix_market,
        }
    x_market = requests.get(url_for_product, headers=head)
    y_market = json.loads(x_market.text)
    return y_market

def get_orders(best_order):
    final_list = []
    identity = best_order['id']
    list_products_sale = identity.split('?&')
    for item in list_products_sale:
        if item != '':
            final_list.append(item)
    return final_list

def find_product(product_name, full_list):
    dictStuff = []
    for i in full_list:
        if product_name in i['product_id']:
            dictStuff.append(i)
    return dictStuff


def sort_da_list(df):
    if len(df) > 3 and len(df) != 1:
        for items in df:
            sort_da_list(items)
    if len(df) == 1:
        temp = df[0]
        if len(temp) != 0 and type(temp) is dict:
            if float(temp['money']) > currency_needed_big:
                database_sorted.append(temp)
        if len(temp) != 0 and type(temp) is list:
            for items3 in temp:
                sort_da_list(items3)
    if len(df) == 3 and type(df) is dict:
        if float(df['money']) > currency_needed_big:
            database_sorted.append(temp)
    if len(df) == 3 and type(df) is list:
        for items2 in df:
            sort_da_list(items2)
    return database_sorted


def examine(product_id):
    new_full_list = []
    unix = str(int(time.time()))
    sign2 = unix + "GET" + "/api/v3/brokerage/products" + ''
    sign = hmac.new(API_SECRET.encode('utf-8'), sign2.encode('utf-8'), digestmod=hashlib.sha256).digest()
    head = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": sign.hex(),
        "CB-ACCESS-TIMESTAMP": unix,
        }
    x = requests.get(URL, headers=head)
    y = json.loads(x.text)
    z = y['products']
    for data in z:
        if data['price'] != '':
            new_full_list.append(data)
    test = find_product(product_id, new_full_list)
    return test


def find_shit():
    new_full_list = []
    test_list = []
    ultimate_answer = []
    checkIfExists = False
    dict_quote = {}
    dict_base = {}
    unix = str(int(time.time()))
    sign2 = unix + "GET" + "/api/v3/brokerage/products" + ''
    sign = hmac.new(API_SECRET.encode('utf-8'), sign2.encode('utf-8'), digestmod=hashlib.sha256).digest()
    head = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": sign.hex(),
        "CB-ACCESS-TIMESTAMP": unix,
        }
    x = requests.get(URL, headers=head)
    y = json.loads(x.text)
    z = y['products']
    for i in z:
        if i['quote_currency_id'] in dict_quote:
            if i['price'] == '':
                continue
            else:
                dict_quote[i['quote_currency_id']].append(i)
        else:
            if i['price'] == '':
                continue
            else:
                dict_quote[i['quote_currency_id']] = [i]
    for data in z:
        if data['price'] != '':
            new_full_list.append(data)
    for test in dict_quote['USD']:
        initMapVar = initializeMap(new_full_list, test)
        ultimate_answer.append(initMapVar)
    return [dict_quote, new_full_list, ultimate_answer]

def testCurrency(list_lol):
    final_dict = []
    for i in list_lol:
        if 'EUR' in i['id'] or 'GBP' in i['id']:
            continue
        if 'EUR' not in i['id'] and 'GBP' not in i['id']:
            final_dict.append(i)
    return final_dict


def initializeMap(full_list, start):
    money = currency_needed_big
    # initialize string for mapping
    count = 1
    finalString = '?&' + start['product_id']
    currency = start['base_currency_id']
    money = (money - (money * 0.006)) / float(start['price'])
    limit_only = start['limit_only']
    continueMapVar = continueMapTest(full_list, money, currency, finalString, count)
    return continueMapVar


def continueMapTest(full_list, money, currency, finalString, count):
    carry_on_var = 0
    product = find_product(currency, full_list)
    final_dict = []
    if 'USD' in currency and 'USDT' not in currency:
        final_dict.append({'id': finalString, 'money': money, 'current_currency': currency})
    if 'USD' not in currency or 'USDT' in currency:
        if count >= combinations_for_paths:
            for xz in product:
                if currency == xz['base_currency_id'] and 'USD' == xz['quote_currency_id']:
                    count = count + 1
                    money = (money - (money * 0.006)) * float(xz['price'])
                    currency = xz['quote_currency_id']
                    finalString = finalString + '?&' + xz['product_id']
                    final_dict.append({'id': finalString, 'money': money, 'current_currency': currency})
                    continue
                if currency == xz['quote_currency_id'] and 'USD' == xz['base_currency_id']:
                    count = count + 1
                    money = (money - (money * 0.006)) / float(xz['price'])
                    currency = xz['base_currency_id']
                    finalString = finalString + '?&' + xz['product_id']
                    final_dict.append({'id': finalString, 'money': money, 'current_currency': currency})
                    continue
        if count < combinations_for_paths or carry_on_var > 0:
            for i in product:
                tempString = finalString
                tempMoney = money
                tempCurrency = currency
                tempCount = count
                if currency == i['base_currency_id']:
                    tempCount = tempCount + 1
                    tempMoney = (tempMoney - (tempMoney * 0.006)) * float(i['price'])
                    tempCurrency = i['quote_currency_id']
                    tempString = tempString + '?&' + i['product_id']
                    temp_dir = {'id': tempString, 'money': tempMoney, 'current_currency': tempCurrency}
                    if 'USD' in currency and 'USDT' not in currency:
                        final_dict.append(temp_dir)
                    if 'USD' not in currency or 'USDT' in currency:
                        final_dict.append(continueMapTest(full_list, tempMoney, tempCurrency, tempString, tempCount))
                if currency == i['quote_currency_id']:
                    tempCount = tempCount + 1
                    tempMoney = (tempMoney - (tempMoney * 0.006)) / float(i['price'])
                    tempCurrency = i['base_currency_id']
                    tempString = tempString + '?&' + i['product_id']
                    temp_dir = {'id': tempString, 'money': tempMoney, 'current_currency': tempCurrency}
                    if 'USD' in currency and 'USDT' not in currency:
                        final_dict.append(temp_dir)
                    if 'USD' not in currency or 'USDT' in currency:
                        final_dict.append(continueMapTest(full_list, tempMoney, tempCurrency, tempString, tempCount))
    return final_dict


