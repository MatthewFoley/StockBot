import alpaca_trade_api as tradeapi
import time
import datetime
import yfinance as yf
import pandas as  pd
import numpy as np
import bs4 as BeautifulSoup
import requests

#Alpaca API Keys
key = 'Insert Alpaca Trading API Key'
sec = 'Insert Alpaca Trading Secret Key'

#Endpoint URL
url = 'https://paper-api.alpaca.markets'

#Connects to trading account via the Alpaca API
api = tradeapi.REST(key, sec, url, api_version='v2')
account = api.get_account()

#Create array of stocks to invest in for the day
stock_array = ['GME', 'F', 'APHA', 'GNW', 'ATHX', 'MRO', 'MNKD', 'SOLO', 'GPRO', 'BB']

################################### Stock Tracker #############################################################
class PaperTrader:

    def trackAndTrade(ticker):
        stock = yf.Ticker(ticker)

        #Fetchs date the desired days ago
        date_today = datetime.date.today()
        date_7_days_ago = date_today - datetime.timedelta(days=7)

        #200 day moving average
        history_200_days = stock.history(start=date_today - datetime.timedelta(days=200), end=date_today, interval='1d')
        close_200_day = history_200_days['Close']
        sma_200 = pd.DataFrame.rolling(close_200_day, window=200, min_periods=2).mean()
        current_sma_200 = round(sma_200[-1], 6)

        #7 day low
        stock_7days = stock.history(start=date_7_days_ago, end=date_today, interval='1d')
        low_7_day = stock_7days['Low']
        low_7_day.sort_values
        lowest_7_day = float(low_7_day[0])

        #7 day high
        high_7_day = stock_7days['High']
        high_7_day.sort_values
        highest_7_day = float(high_7_day[-1])

        #Retrieve the closing value of the day
        close_daily = stock_7days['Close']
        close_day = float(close_daily[-1])

        #Scrapes and formats the current price, day Low & day high from Yahoo Finance
        url = f'https://finance.yahoo.com/quote/{ticker}'
        headers = {'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0'}
        r = requests.get(url, headers=headers)
        web_content = BeautifulSoup.BeautifulSoup(r.text, 'html.parser')
        price = web_content.find('div', {'class' : 'D(ib) Mend(20px)'}).find_all('span')[0].text
        range = web_content.find('td', {'data-test' : 'DAYS_RANGE-value'}).text
        range_split = str(range).split('-', 1)
        daily_low = float(range_split[0])
        daily_high = float(range_split[1])
        stock_current_price = float(price)

    ###################### Variables ##################################################
        #Note not all values are used in the current trading plan, but have been
        #calculated in anticipation of future trading plans.

        #stock_current_price - The live market price of the selected stock
        #daily_low - The low price of the stock for current day
        #daily_high - The high price of the stock for the current day
        #close_day - The closing price of the previous day
        #highest_7_day - The rolling 7 days high
        #lowest_7_day - The rolling 7 day low
        #current_sma_200 - The Simple Moving Average over the last 200 days

    ######################Buy & Sell Orders############################################

        #The Trading Plan - Please note this is NOT financial advice. 
            #Buy if the previous day closed below the 7 day low and the current market price is above the 200 day Moving average.
            #Sell if the previous days close is 7 day rolling high.

        #Calculates how much to buy based available capital
        balance = float(account.cash)
        order_quantity = np.floor((balance/10) / stock_current_price)

        #Searches portfolio for positions in selected stock
        portfolio = api.list_positions()
        portfolio_positions = [o for o in portfolio if o.symbol == ticker]

        #Searches the order list for open orders on the selected stock
        orders = api.list_orders(status='open')
        stock_orders = [o for o in orders if o.symbol == ticker]

        #Places Buy order following the trading plan
        if close_day < lowest_7_day:
            if stock_current_price > current_sma_200:
                if not portfolio_positions:
                    if not stock_orders:
                        api.submit_order(symbol=ticker,qty=order_quantity, side='buy', type='market', time_in_force='day')
                        print("Buy order for " + str(order_quantity) + " shares of " + ticker)
            
        #Places Sell order follwoing the trading plan
        if close_day > highest_7_day:
            if portfolio_positions:
                api.submit_order(symbol=ticker,qty=order_quantity, side='sell', type='market', time_in_force='gtc')
                print("Sell order for  " + str(order_quantity) + " shares of " + ticker)
            
    #############################Execution###########################################################

    while True:
        for symbol in stock_array:
            trackAndTrade(symbol)
        time.sleep(5)