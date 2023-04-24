


def runThrough(dict_quote, dict_base, start, money, currency):
    final_dict = {}
    money2 = money
    finalString2 = finalString
    currency2 = currency
    if currency in dict_quote:
        for i in dict_quote[currency]:
            money = (money - (money * 0.006)) / float(i['price']) 
            finalString = finalString + '2' + i['product_id']
            currency = i['base_currency_id']
            test = runThrough(dict_quote, dict_base, i, money, currency, final_dict)
            final_dict.append(test)
    if currency2 in dict_base:
        for k in dict_base:
            money2 = (money2 - (money2 * 0.006)) * float(k['price']) 
            finalString2 = finalString2 + '2' + k['product_id']
            currency2 = k['quote_currency_id']
            test2 = runThrough(dict_quote, dict_base, k, money2, currency2, final_dict)
            final_dict.append(test2)



        if count >= 4:
            count = count + 1
            for xz in product:
                if 'USD' in xz['product_id'] and 'USDT' not in xz['product_id']:
                    if currency in xz['base_currency_id']:
                        money = (money - (money * 0.006)) * float(xz['price'])
                        currency = xz['quote_currency_id']
                        finalString = finalString + str(count) + xz['product_id']
                    if currency in xz['quote_currency_id']:
                        money = (money - (money * 0.006)) / float(xz['price'])
                        currency = xz['base_currency_id']
                        finalString = finalString + str(count) + xz['product_id']
                    final_dict.append({'id': finalString, 'money': money, 'current_currency': currency})
