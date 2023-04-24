from inspect import currentframe
from logging import exception
import ccxt
import secret_config
import networkx as nx
import matplotlib.pyplot as plt
import urllib.parse
import hashlib
import hmac
import base64
import requests
import time


api_url = "https://api.kraken.com"
money = 50.0

USD_not_tradable = ['ACA', 'AGLD', 'ALICE', 'APT', 'ASTR', 'ATLAS', 'AUDIO',
                    'CFG', 'CSM', 'C98', 'GLMR', 'HDX', 'INTR', 'JASMY', 'KIN',
                    'MC', 'MV', 'NMR', 'NODL', 'NYM', 'ORCA', 'OXY', 'PARA', 'PERP',
                    'PSTAKE', 'RAY', 'REQ', 'ROOK', 'SAMO', 'SDN', 'STEP', 'TEER',
                    'WOO', 'YGG', 'XRT']

kraken = ccxt.kraken({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_kraken,
        'secret': secret_config.API_SECRET_kraken
        })

def keep_running():
    balance = kraken.fetch_balance()
    while float(balance['USD']['total']) > 50:
        x = main()
        print("Balance:")
        print(balance['USD']['total'])
        print("Total Made:")
        print(x[0][0]['total_money'])
        if float(x[0][0]['total_money']) > 60.0:
            orders = all_orders_orginizer(x[1])
        time.sleep(10)


def main():
    newer_list = []
    final_list = []
    #93234 total paths with 5 cutoff
    kraken_info = kraken_test()
    paths = find_paths(kraken_info[0])
    newList = sorted(paths, key=lambda d: float(d['total_money']), reverse=True)
    for i in newList:
        counter = 0
        for k in i:
            if float(i[k]) > 0.0001:
                counter = counter + 1
        if len(i) == counter:
            newer_list.append(i)
    for m in newer_list:
        bad_currency = False
        for n in USD_not_tradable:
            if n in str(m.keys()):
                bad_currency = True
        if bad_currency == False:
            final_list.append(m)
    purchase_path = final_list[0]
    purchasing_info = create_purchase_path(purchase_path)
    balance = kraken.fetch_balance()
    return final_list, purchasing_info

def all_orders_organizer(purchasing_info):
    print("Making orders")
    balance = kraken.fetch_balance()
    checker_bool = True
    if float(balance['USD']['total']) < money:
        return "Not enough funds"
    for i in purchasing_info:
        balance = kraken.fetch_balance()
        currency = i['current_currency']
        try:
            balance = balance[currency]['total']
        except:
            time.sleep(5)
            balance = kraken.fetch_balance()
            currency = i['current_currency']
            balance = balance[currency]['total']
        print(currency)
        print(balance)
        volume = get_volume(i, balance)
        print(volume)
        order_receipt = place_orders(i, volume)

def get_volume(purchasing_info_single, balance):
    volume = 0
    if purchasing_info_single['current_currency'] == 'USD':
        balance = money
    if purchasing_info_single['type'] == 'buy':
        price = kraken.fetch_ticker(purchasing_info_single['ticker_symbol'])['close']
        volume = balance / price
    if purchasing_info_single['type'] == 'sell':
        volume = balance
    return volume

def place_orders(purchasing_info, volume):
    resp = kraken_request('/0/private/AddOrder', {
        "nonce": str(int(1000*time.time())),
        "ordertype": "market",
        "type": purchasing_info['type'],
        "volume": volume,
        "pair": purchasing_info['symbol'],
        }, secret_config.API_KEY_kraken, secret_config.API_SECRET_kraken)
    print(resp.json())
    if ('Insufficient' in str(resp.json()['error'])):
        print("Replacing Order")
        x = place_orders(purchasing_info, volume * 0.995)

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-key'] = api_key
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def create_purchase_path(purchase_path):
    final_list = []
    currency = 'USD'
    for i in purchase_path:
        temp_currency = currency
        if i == "total_money":
            break
        market = i.split("/")
        if market[0] == temp_currency:
            temp_dict = {"symbol": i.replace("/", ""), "type": "sell", "current_currency": market[0], "new_currency": market[1], "ticker_symbol": i}
            currency = market[1]
        if market[1] == temp_currency:
            temp_dict = {"symbol": i.replace("/", ""), "type": "buy", "current_currency": market[1], "new_currency": market[0], "ticker_symbol": i}
            currency = market[0]
        final_list.append(temp_dict)
    return final_list


def kraken_test():
    kraken_ticker = [kraken.fetch_tickers(), 'kraken']
    final_dict = {}
    for i in list(kraken_ticker[0].keys()):
        if '/' in kraken_ticker[0][i]['symbol']:
            final_dict.update({kraken_ticker[0][i]['symbol']: kraken_ticker[0][i]['close']})
    return [final_dict, kraken_ticker]

def sort_by_base_currency(currency, list_of_markets):
    final_dict = {}
    for i in list(list_of_markets.keys()):
        try:
            if currency == i.split('/')[0] or currency == i.split('/')[1]:
                final_dict.update({i: list_of_markets[i]})
        except:
            continue
    return final_dict

def cGraph():
    x = find_all_currencies()
    markets = kraken_test()[0]
    G = nx.DiGraph()
    newCurrency = ''
    for i in x:
        stuff = sort_by_base_currency(i, markets)
        for s in list(stuff.keys()):
            if i == s.split('/')[0]:
                newCurrency = s.split('/')[1]
            if i == s.split('/')[1]:
                newCurrency = s.split('/')[0]
            if i != s.split('/')[0] and i != s.split('/')[1]:
                continue
            G.add_edges_from([(i, newCurrency)])
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=100)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='black')
    nx.draw_networkx_labels(G, pos)
    return G

def find_all_currencies():
    final_dict = []
    x = kraken_test()[0]
    for i in list(x.keys()):
        currencies = i.split('/')
        if currencies[0] in final_dict and currencies[1] in final_dict:
            continue
        if currencies[0] in final_dict and currencies[1] not in final_dict:
            final_dict.append(currencies[1])
        if currencies[0] not in final_dict and currencies[1] in final_dict:
            final_dict.append(currencies[0])
        if currencies[0] not in final_dict and currencies[1] not in final_dict:
            final_dict.append(currencies[0])
            final_dict.append(currencies[1])
    return final_dict

def find_paths(kraken_info):
    final_list = []
    final_list_usdc_approved = []
    final_list_with_money = []
    graph = cGraph()
    paths = list(nx.all_simple_paths(graph, source='USDC', target='USD', cutoff=5))
    for i in paths:
        final_list.append(find_prices(i, kraken_info))
    for x in final_list:
        data = try_this_for_markets(x, kraken_info)
        final_list_usdc_approved.append(data[0])
    for k in final_list_usdc_approved:
        money = calculate_profit(k, 'USD')
        k['total_money'] = money[0]
        if money[1]:
            continue
        final_list_with_money.append(k)
    return final_list_with_money

def find_prices(path, kraken_data):
    price_list = {}
    counter = 0
    # CHANGE THIS TO JUST TAKE IN A SINGLE PATH
    for i in path:
        if counter < 1:
            counter = counter + 1
            previous_currency = i
            continue
        try:
            market_string = previous_currency + "/" + i
            data = kraken_data[market_string]
            price_list.update({market_string: data})
            previous_currency = i
        except:
            try:
                market_string = i + "/" + previous_currency
                data = kraken_data[market_string]
                price_list.update({market_string: data})
                previous_currency = i
            except:
                print("FAILED")
                break
    return price_list


def calculate_profit(price_list, actual_currency):
    local_money = money
    exception_tracker = False
    #May have to change this too
    currency = actual_currency
    for i in list(price_list.keys()):
        try:
            exchange = i.split('/')
            if currency == exchange[0]:
                local_money = local_money * float(price_list[i])
                temp_currency = exchange[1]
            if currency == exchange[1]:
                local_money = local_money / float(price_list[i])
                temp_currency = exchange[0]
        except:
            exception_tracker = True
            break
        currency = temp_currency
    if currency != 'USD':
        exception_tracker = True
    return local_money, exception_tracker


def try_this_for_markets(list_of_markets_with_prices, kraken_info):
    global_price_list = list_of_markets_with_prices
    exception_tracker = False
    currency = ""
    price_list = global_price_list
    new_price_list = {'USDC/USD': kraken_info['USDC/USD']}
    new_price_list.update(price_list)
    currency = 'USD'
    exception_tracker = True
    return new_price_list, currency


def new_usdcNecessary(list_of_markets_with_prices, kraken_info):
    global_price_list = list_of_markets_with_prices
    exception_tracker = False
    currency = ""
    try:
        temp_first_market = list(list_of_markets_with_prices.items())[0][0]
        temp_first_market = temp_first_market.replace('USDC', 'USD')
        new_price_list = {temp_first_market: kraken_info[temp_first_market]}
        del list_of_markets_with_prices[list(list_of_markets_with_prices.items())[0][0]]
        new_price_list.update(list_of_markets_with_prices)
        currency = 'USD'
    except:
        try:
            temp_first_market = list(list_of_markets_with_prices.items())[0][0]
            temp_first_market = temp_first_market.replace('USDC', 'USD')
            temp_split = temp_first_market.split("/")
            temp_first_market = temp_split[1] + "/" + temp_split[0]
            new_price_list = {temp_first_market: kraken_info[temp_first_market]}
            del list_of_markets_with_prices[list(list_of_markets_with_prices.items())[0][0]]
            new_price_list.update(list_of_markets_with_prices)
            currency = 'USD'
        except:
            price_list = global_price_list
            new_price_list = {'USDC/USD': kraken_info['USDC/USD']}
            new_price_list.update(price_list)
            currency = 'USD'
            exception_tracker = True
    return new_price_list, currency, exception_tracker


