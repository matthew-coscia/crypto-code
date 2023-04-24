from inspect import currentframe
from logging import exception
import ccxt
import secret_config
import networkx as nx
import matplotlib.pyplot as plt

#form github
money = 100.0
#initialize setup

kraken = ccxt.kraken({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_kraken,
        'secret': secret_config.API_SECRET_kraken
        })

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

def find_paths(kraken_info):
    final_list = []
    final_list_usdc_approved = []
    final_list_with_money = []
    graph = cGraph()
    paths = list(nx.all_simple_paths(graph, source='USDC', target='USD', cutoff=5))
    for i in paths:
        final_list.append(find_prices(i, kraken_info))
    for x in final_list:
        data = new_usdcNecessary(x, kraken_info)
        if (data[2]):
            continue
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


def usdcNecessary(price_list):
    global_price_list = price_list
    currency = ""
    try:
        temp_first_market = list(price_list.items())[0][0]
        temp_first_market = temp_first_market.replace('USDC', 'USD')
        first_ticker = kraken.fetch_ticker(temp_first_market)
        new_price_list = {temp_first_market: first_ticker['close']}
        del price_list[list(price_list.items())[0][0]]
        new_price_list.update(price_list)
        currency = 'USD'
    except:
        price_list = global_price_list
        print("Hit Exception")
        first_ticker = kraken.fetch_ticker('USDC/USD')
        new_price_list = {'USDC/USD': first_ticker['close']}
        new_price_list.update(price_list)
        currency = 'USD'
    return new_price_list, currency


def main_test():
    #93234 total paths with 5 cutoff
    kraken_info = kraken_test()
    paths = find_paths(kraken_info[0])
    print(float((len(paths) / 93234) * 100))
    print("Of Paths could be completed.")
    newList = sorted(paths, key=lambda d: float(d['total_money']), reverse=True)
    return newList, kraken_info[0]




def main():
    x = find_paths()
    progress_counter = 0
    progress_reporter = int(len(x) / 10)
    print(len(x))
    y = kraken_test()
    final_list = []
    condensed_string_for_orders = ""
    for path in x:
        if (progress_counter % progress_reporter == 0):
            print(str(int((progress_counter / len(x)) * 100)) + "% Done")
        prices = find_prices(path, y[0])
        price_list = prices[0]
        new_price_list = usdcNecessary(price_list)
        actual_currency = new_price_list[1]
        new_price_list = new_price_list[0]
        currency_list = prices[1]
        profit = calculate_profit(new_price_list, actual_currency)
        for i in list(new_price_list.keys()):
            condensed_string_for_orders = condensed_string_for_orders + "???" + i
        condensed_string_for_orders = condensed_string_for_orders.lstrip('???')
        temp_dict = {condensed_string_for_orders: profit}
        final_list.append(temp_dict)
        progress_counter = progress_counter + 1
    return new_price_list, currency_list, profit, final_list


