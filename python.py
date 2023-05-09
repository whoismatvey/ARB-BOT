import ccxt
import telebot 
import math

exchangesData = {
    "binance": {
        "apiKey": "WVet6aAxuGyUMnnW5rQzuRTDAYPSwYlX9vb5fzbAg4YBpGQxwBaDgfnYqyhl2ED3",
        "secret": "tXMHRe82YuvYsHsOo5yQ3Hvekq347NksYnmZp7rUSeAItMsaKeUMNxgTTsTPXAPD",
        "transactionFee": 0.001
    },
    "huobi": {
        "apiKey": "qv2d5ctgbn-dd30b726-2338179d-e54df",
        "secret": "ea5a8827-26a9b35c-1cf7d236-9eaea",
        "transactionFee": 0.002
    },
    "bitget": {
        "apiKey": "bg_b511dba576a76f473587bb6a60fd0539",
        "secret": "9f4924195ad5b2c985d0185f3409990fe58c4dcc173b65739297a1721cdbed3e",
        "transactionFee": 0.002
    },
    "kucoin": {
        "apiKey": "6450a6632f3ded00013aaec5",
        "secret": "9d46147c-fb0e-4674-bdb0-1edc8d4b8e3c",
        "transactionFee": 0.002
    },
    "cex": {
        "apiKey": "sLvcxk4w1PG0IpW0ZEBrTKVHlg",
        "secret": "rhX2RRCIm5joOzCZU2hCglWunH0",
        "transactionFee": 0.002
    },
}

min_spread = 3 #Минимальный спред 
min_profit = 0 #Минимальный профит  

bot = telebot.TeleBot("6214940636:AAEyeNUdlmqnXi_imG3uvTGw5O0gCHgbpCQ")
    

@bot.message_handler(commands=['start'])
def main(message):
    exchanges = [
        "binance",
        "huobi",
        "bitget",
        "kucoin",
        "cex"
    ]

    symbols = [
        "BTC/USDT"
    ]

    min_ask_exchange_id = ""
    min_ask_price = 99999999
    min_ask_volume = 0

    max_bid_exchange_id = ""
    max_bid_price = 0
    max_bid_volume = 0

    exchange_symbol = ""
    max_increase_percentage = 0.0

    for symbol in symbols:
        #Ищет биржи, на которых можно купить и продать заданную торговую пару, и вычисляет разницу между наивысшей ценой продажи (ask_price) и наименьшей ценой покупки (bid_price) 
        ask_exchange_id, ask_price, bid_exchange_id, bid_price, max_bid_volume, min_ask_volume, bid1, ask2, max1, min1 = get_biggest_spread_by_symbol(exchanges, symbol)
        #Эта формула определяет процентный разрыв между ценой продажи и ценой покупки,
        increase_percentage = (bid_price - ask_price) / ask_price * 100

        def covert (price, voluem): 
            return price * voluem

        #ОТПРАВИТЬ В ТГ
        bot.send_message(message.chat.id, "<b>[{0} - {1}] - [{2}]</b>\n\n<b>Price Spread: {3:.2}%</b>\n\n<b>Exchange: {0}</b>\nAsk Price: {4}$\
            \nBid Price: {5}$ \nBid Voluem: {6}$ \nAsk Voluem: {7}$\n\n<b>Exchange: {1}</b>\nAsk Price: {8}$\nBid Price: {9}$\
            \nBid Voluem: {10}$\nAsk Voluem: {11}$".format(ask_exchange_id, bid_exchange_id, symbol, increase_percentage, \
            round(ask_price, 3), round(bid1, 3),  round(covert(ask_price, max1),3), round(covert(ask_price, min_ask_volume),3), \
            round(ask2, 3), round(bid_price, 3), round(covert(ask2, max_bid_volume), 3), round(covert(ask2, min1), 3)), parse_mode='HTML')

        #Cравнивает значение increase_percentage с max_increase_percentage, которая содержит максимальное значение процентного 
        # изменения цены покупки относительно цены продажи для всех торговых пар. Если значение increase_percentage больше, 
        # чем max_increase_percentage, то текущая торговая пара имеет наивысший процентный разрыв между ценой покупки и ценой продажи
        if increase_percentage > max_increase_percentage:
            exchange_symbol = symbol
            max_increase_percentage = increase_percentage
            min_ask_exchange_id = ask_exchange_id
            min_ask_price = ask_price
            max_bid_exchange_id = bid_exchange_id
            max_bid_price = bid_price


        if increase_percentage >= min_spread:
            break


def get_biggest_spread_by_symbol(exchanges, symbol):
    ask_exchange_id = ""
    min_ask_price = 99999999
    min_ask_volume = 0

    bid_exchange_id = ""
    max_bid_price = 0
    max_bid_volume = 0
    max1 = 0
    min1 = 0

    for exchange_id in exchanges:
        exchange = eval("ccxt.{0}()".format(exchange_id))

        try:
            order_book = exchange.fetch_order_book(symbol)
            bid_price = order_book['bids'][0][0] if len(
                order_book['bids']) > 0 else None
            ask_price = order_book['asks'][0][0] if len(
                order_book['asks']) > 0 else None
            ask_volume = order_book['asks'][0][1] if len(
                order_book['asks']) > 0 else None
            bid_volume = order_book['bids'][0][1] if len(
                order_book['bids']) > 0 else None


            if ask_price < min_ask_price:
                ask_exchange_id = exchange_id
                min_ask_price = ask_price
                bid1 = bid_price
                min_ask_volume = ask_volume
                max1 = bid_volume
         
            if bid_price > max_bid_price:
                bid_exchange_id = exchange_id
                max_bid_price = bid_price
                ask2 = ask_price
                max_bid_volume = bid_volume
                min1 = ask_volume

            increase_percentage = (bid_price - ask_price) / ask_price * 100
            if increase_percentage >= 3:
                return ask_exchange_id, min_ask_price, bid_exchange_id, max_bid_price, max_bid_volume, min_ask_volume, bid1, ask2, max1, min1
        except:
            # pass
            print("")
            print("{0} - There is an error!".format(exchange_id))

    min_ask_price += 0.235
    max_bid_price -= 0.235

    return  ask_exchange_id, min_ask_price, bid_exchange_id, max_bid_price, max_bid_volume, min_ask_volume, bid1, ask2, max1, min1


def send_welcome(message):
    bot.send_message(message.chat.id, message)
    main(message)

bot.polling(non_stop=True)