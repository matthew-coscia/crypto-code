from inspect import currentframe
import ccxt
import secret_config
import networkx as nx
import matplotlib.pyplot as plt

API_KEY = "zqiKZAp590y0Cly6"
API_SECRET = "UjkmK9DuKDdscs4bH4x9YGg6RIHbxKpl"
init_currency = 'USDC'
#form github
money = 100.0
#initialize setup
coinbase = ccxt.coinbase({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_coinbase,
        'secret': secret_config.API_SECRET_coinbase
        })
binanceus = ccxt.binanceus({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_binance,
        'secret': secret_config.API_SECRET_binance
        })
kraken = ccxt.kraken({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_kraken,
        'secret': secret_config.API_SECRET_kraken
        })
bitmart = ccxt.bitmart({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_bitmart,
        'secret': secret_config.API_SECRET_bitmart,
        'uid': '10368264'
        })
gemini = ccxt.gemini({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_gemini,
        'secret': secret_config.API_SECRET_gemini
        })
okcoin = ccxt.okcoin({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_okcoin,
        'secret': secret_config.API_SECRET_okcoin,
        'password': 'Grandma@0723'
        })
alpaca = ccxt.alpaca({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_alpaca,
        'secret': secret_config.API_SECRET_alpaca
        })
bittrex = ccxt.bittrex({
        'enableRateLimit': True,
        'apiKey': secret_config.API_KEY_bittrex,
        'secret': secret_config.API_SECRET_bittrex
        })


def place_orders():
    x = sort_list_of_arb()
    balances = get_balances()
    lowest_order = x['SOL/USDT']['lowest']
    highest_order = x['SOL/USDT']['highest']
    #if float(balances[lowest_order[1]]['USDT']) >= 75.0:


def get_balances():
    coinbase_balance = coinbase.fetch_balance()
    binanceus_balance = binanceus.fetch_balance()
    kraken_balance = kraken.fetch_balance()
    bitmart_balance = bitmart.fetch_balance()
    okcoin_balance = okcoin.fetch_balance()
    bittrex_balance = bittrex.fetch_balance()
    return {'coinbase': coinbase_balance, 'binanceus': binanceus_balance, 'kraken': kraken_balance, 'bitmart': bitmart_balance, 'okcoin': okcoin_balance, 'bittrex': bittrex_balance}


def sort_list_of_arb():
    temp_list = {}
    final_list = {}
    x = get_flat_arb()
    for i in list(x.items()):
        profit = i[1]['profit']
        temp_list.update({profit: i[0]})
    final_list_sorted = sorted(temp_list, reverse=True)
    for k in final_list_sorted:
        final_list.update({temp_list[k]: x[temp_list[k]]})
    return final_list


def get_flat_arb():
    final_dict = {}
    lowest_price = 10000000000000000000000.0
    lowest_market = ''
    highest_price = 0.0
    highest_market = ''
    markets = get_prices()
    temp_list = {}
    for i in list(markets.keys()):
        x = markets[i]
        for k in list(x.keys()):
            if float(x[k]) == 0.0:
                continue
            if float(x[k]) < lowest_price:
                lowest_price = float(x[k])
                lowest_market = k
            if float(x[k]) > highest_price:
                highest_price = float(x[k])
                highest_market = k
        total_made = (money / lowest_price) * highest_price
        temp_dict = {'lowest': [lowest_price, lowest_market], 'highest': [highest_price, highest_market], 'profit': total_made}
        final_dict.update({i: temp_dict})
        total_made = 0
        lowest_price = 10000000000000000000000.0
        highest_price = 0.0
    return final_dict

def get_prices():
    final_list = {}
    initialize_data = get_information()
    size = len(initialize_data) - 1
    init_list = initialize_data[size]
    list_of_exchanges = initialize_data[0:size]
    temp_list = {}
    for i in init_list:
        for k in list_of_exchanges:
            temp = k[0][i]
            temp = {k[1]: temp['close']}
            temp_list.update(temp)
        final_list.update({i : temp_list})
        temp_list = {}
        temp = 0
    return final_list



def get_information():
    temp_dict_one = []
    temp_dict_two = []
    temp_dict_three = []
    temp_dict_four = []
    temp_dict_five = []
    coinbase_ticker = [coinbase.fetch_tickers(), 'coinbase']
    binanceus_ticker = [binanceus.fetch_tickers(), 'binanceus']
    kraken_ticker = [kraken.fetch_tickers(), 'kraken']
    bitmart_ticker = [bitmart.fetch_tickers(), 'bitmart']
    #gemini_ticker = [gemini.fetch_tickers(), 'gemini']
    #alpaca_markets = [alpaca.fetch_tickers(), 'alpaca']
    okcoin_ticker = [okcoin.fetch_tickers(), 'okcoin']
    bittrex_ticker = [bittrex.fetch_tickers(), 'bittrex']
    for i in coinbase_ticker[0].keys():
        if i in binanceus_ticker[0].keys():
            temp_dict_one.append(i)
    for k in kraken_ticker[0].keys():
        if k in temp_dict_one:
            temp_dict_two.append(k)
    for z in bitmart_ticker[0].keys():
        if z in temp_dict_two:
            temp_dict_three.append(z)
    for kz in bittrex_ticker[0].keys():
        if kz in temp_dict_three:
            temp_dict_four.append(kz)
    return coinbase_ticker, binanceus_ticker, kraken_ticker, bitmart_ticker, bittrex_ticker, temp_dict_four

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

def find_paths():
    graph = cGraph()
    paths = list(nx.all_simple_paths(graph, source=init_currency, target='USD', cutoff=5))
    return paths

def find_prices(paths, kraken_data):
    counter = 0
    test = paths[0]
    print(test)
    for i in test:
        if counter < 1:
            counter = counter + 1
            previous_currency = i
            continue
        try:
            market_string = previous_currency + "/" + i
            data = kraken_data[market_string]
            print(data)
        except:
            market_string = i + "/" + previous_currency
            data = kraken_data[market_string]
            print(data)
        counter = counter + 1




def create_graph():
    currencyInit = 'USD'
    in_case = False
    x = kraken_test()[0]
    G = nx.DiGraph()
    y = sort_by_base_currency(currencyInit, x)
    for i in list(y.keys()):
        if currencyInit == i.split('/')[0]:
            currency = i.split('/')[1]
            in_case = True
        if currencyInit == i.split('/')[1] and in_case == False:
            currency = i.split('/')[0]
        G.add_edges_from([(currencyInit, currency)])
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=100)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='black')
    nx.draw_networkx_labels(G, pos)
    plt.show()
    return G





    



    #coinbase_ticker = [coinbase.fetch_ticker('BTC/USD'), 'coinbase']
    #binanceus_ticker = [binanceus.fetch_ticker('BTC/USD'), 'binanceus']
    #kraken_ticker = [kraken.fetch_ticker('BTC/USD'), 'kraken']
    #gemini_ticker = [gemini.fetch_ticker('BTC/USD'), 'gemini']
    #okcoin_ticker = [okcoin.fetch_ticker('BTC/USD'), 'okcoin']
    #ticker_dict = [coinbase_ticker, binanceus_ticker, kraken_ticker, gemini_ticker, okcoin_ticker]
    #test_dict = []
    #for i in ticker_dict:
    #    test_dict.append([i[0]['close'], i[1]])
    #return ticker_dict, test_dict
