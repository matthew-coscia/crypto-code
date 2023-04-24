import requests, datetime, time, hmac, hashlib, json, base64


API_KEY = "zqiKZAp590y0Cly6"
API_SECRET = "UjkmK9DuKDdscs4bH4x9YGg6RIHbxKpl"
URL = "https://coinbase.com/api/v3/brokerage/products"

def find_product(product_name, full_list):
    dictStuff = []
    for i in full_list:
        if product_name in i['product_id']:
            dictStuff.append(i)
    return dictStuff


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



def initializeMap(full_list, start):
    money = 100.0
    # initialize string for mapping
    count = 1
    finalString = str(count) + start['product_id']
    currency = start['base_currency_id']
    money = (money - (money * 0.006)) / float(start['price'])
    continueMapVar = continueMapTest(full_list, money, currency, finalString, count)
    return continueMapVar


def continueMapTest(full_list, money, currency, finalString, count):
    product = find_product(currency, full_list)
    final_dict = []
    if 'USD' in currency and 'USDT' not in currency:
        final_dict.append({'id': finalString, 'money': money, 'current_currency': currency})
    if 'USD' not in currency or 'USDT' in currency:
        for i in product:
            tempString = finalString
            tempMoney = money
            tempCurrency = currency
            tempCount = count
            if currency in i['base_currency_id']:
                tempCount = tempCount + 1
                tempMoney = (tempMoney - (tempMoney * 0.006)) * float(i['price'])
                tempCurrency = i['quote_currency_id']
                tempString = tempString + str(tempCount) + i['product_id']
                temp_dir = {'id': tempString, 'money': tempMoney, 'current_currency': tempCurrency}
            if currency in i['quote_currency_id']:
                tempCount = tempCount + 1
                tempMoney = (tempMoney - (tempMoney * 0.006)) / float(i['price'])
                tempCurrency = i['base_currency_id']
                tempString = tempString + str(tempCount) + i['product_id']
                temp_dir = {'id': tempString, 'money': tempMoney, 'current_currency': tempCurrency}
            if 'USD' in currency and 'USDT' not in currency:
                final_dict.append(temp_dir)
            if 'USD' not in currency or 'USDT' in currency:
                final_dict.append(continueMapTest(full_list, tempMoney, tempCurrency, tempString, tempCount))
    return final_dict


