from flask import Flask, render_template, request, redirect, jsonify
from src.bot import *
from src.config import *

app = Flask(__name__)
app.secret_key = b'somelongrandomstring'



# initialise the client
clients = Client(API_KEY, API_SECRET, tld='us')

@app.route('/')
def index():
    title = 'CoinView'
    account = clients.get_account()

    balances = account['balances']

    exchange_info = clients.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=balances, symbols=symbols)


@app.route('/buy', methods=['POST'])
def buy():
    print(request.form)

    order = clients.create_order(symbol=request.form['symbol'],
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=request.form['quantity'])


    return redirect('/')

@app.route('/bot', methods=['POST', 'GET'])
def bot():
    bot()
    return 'run'


@app.route('/sell')
def sell():
    return 'sell'


@app.route('/settings')
def settings():
    return 'settings'

@app.route('/history')
def history():
    candlesticks = clients.get_historical_klines("ALGOUSD", Client.KLINE_INTERVAL_1MINUTE, "21 Sep, 2021", "26 Sep, 2021")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = {
            "time": data[0] / 1000,
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)


