import json
import os
from datetime import datetime
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

api_key1 = 'W59OQACAUZ0HS2N3'
api_key2 = 'TWGWL6U2XC4X2L6C'
today_date = datetime.now().strftime("%Y-%m-%d")
link_to_tickers = 'https://stockanalysis.com/stocks/'

response = None
valid_input = True
file_to_save = ''


def create_file(period, tick):
    global response
    global valid_input
    global file_to_save
    global ticker

    relative_path = 'data/%s/%s_stock_market_data-%s-%s.json' % (period, period, tick, today_date)
    # Get the base directory of the current Python script
    base_directory = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path by joining the base directory and the relative path
    file_to_save = os.path.join(base_directory, relative_path)

    if os.path.exists(file_to_save):
        valid_input = False
    else:
        if period == 'daily':
            url_daily = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key2}'
            response = requests.get(url_daily)
        elif period == 'intraday':
            url_intra_day = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval}min&apikey={api_key2}'
            response = requests.get(url_intra_day)
        elif period == 'monthly':
            url_monthly = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&apikey={api_key2}'
            response = requests.get(url_monthly)
        elif period == 'weekly':
            url_weekly = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={ticker}&apikey={api_key2}'
            response = requests.get(url_weekly)
        else:
            valid_input = False

    if valid_input:
        json_data = response.json()
        directory = os.path.dirname(file_to_save)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_to_save, 'w', newline='') as file:
            json.dump(json_data, file, indent=4)

    return file_to_save


def check_api_error_message():
    global file_to_save
    try:
        with open(file_to_save, 'r') as f:
            try:
                data = json.load(f)
            except Exception as exception:
                print(f'An error occurred: {exception}')
        if 'Error Message' in data:
            print("Wrong stock market ticker. Choose a new one!")
            os.remove(file_to_save)  # Delete the file
            return False
        else:
            return True
    except FileNotFoundError:
        print("File not found:", file_to_save)
    except json.JSONDecodeError:
        print("Invalid JSON format in file:", file_to_save)


def create_dataframes(period, file):
    meta_data = None
    stock_data = None
    global valid_input

    try:
        with open(file) as f:
            data = json.load(f)
        meta_data = pd.DataFrame(data['Meta Data'], index=['Meta Data'])
        if period == 'daily':
            stock_data = pd.DataFrame(data['Time Series (Daily)']).T
        elif period == 'intraday':
            stock_data = pd.DataFrame(data['Time Series (5min)']).T
        elif period == 'monthly':
            stock_data = pd.DataFrame(data['Monthly Time Series']).T
        elif period == 'weekly':
            stock_data = pd.DataFrame(data['Weekly Adjusted Time Series']).T
        else:
            valid_input = False
    except Exception as exception:
        print(f'An error occurred: {exception}')

    stock_data = stock_data.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    })
    stock_data = stock_data.astype(float)
    stock_data = stock_data.sort_index(ascending=True)
    return meta_data, stock_data


def calculate_volatility():
    global fig
    stock_data_df['returns'] = ((stock_data_df['close'] /
                                 stock_data_df['close'].shift(1)) - 1) * 100
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=stock_data_df['returns'], name='Daily Returns'))
    fig.update_layout(title=f'Histogram of {time_period} Returns (Percentage) of {ticker} Stock',
                      xaxis_title='Daily Returns (%)',
                      yaxis_title='Frequency')
    fig.show()


def calculate_sma(window):
    global fig
    stock_data_df['sma'] = stock_data_df['close'].rolling(window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df['sma'], mode='lines', name='SMA50'))
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df['close'], mode='lines', name='close'))
    fig.update_layout(title=f'Simple Moving Average over 50 datapoints of the {ticker} closing stock data',
                      xaxis_title='date',
                      yaxis_title='SMA')
    fig.show()


def calculate_rsi(window):
    global fig
    stock_data_df['change'] = stock_data_df['close'].diff()
    stock_data_df['gain'] = stock_data_df['change'].apply(lambda x: x if x > 0 else 0)
    stock_data_df['Loss'] = stock_data_df['Price Change'].apply(lambda x: abs(x) if x < 0 else 0)

    stock_data_df['Avg Gain'] = stock_data_df['Gain'].rolling(window=window).mean()
    stock_data_df['Avg Loss'] = stock_data_df['Loss'].rolling(window=window).mean()

    stock_data_df['RSI'] = 100 - (100 / (1 + stock_data_df['Avg Gain'] / stock_data_df['Avg Loss']))

    #print rsi and show on graph



print("Welcome to StockAnalyzer v1.0! Analyze stock data effortlessly. \
Choose a company and time period to get started.")

print(f"If you don't know the right ticker for a company. Check this website:\
{link_to_tickers}.")

ticker = input('Choose a ticker (company):').upper()

interval = '5'
print('The available time period options are daily, intraday, monthly or weekly.')

time_period = input().lower()
new_file = create_file(time_period, ticker)

while True:
    try:
        if check_api_error_message():
            meta_data_df, stock_data_df = create_dataframes(time_period, new_file)
            if time_period == 'intraday':
                print(f'You chose the ticker {meta_data_df['2. Symbol'].iloc[0]}.\n'
                      f'The data was last updated on {meta_data_df['3. Last Refreshed'].iloc[0]} on the {meta_data_df['6. Time Zone'].iloc[0]} standard time.')
            elif time_period == 'weekly' or time_period == 'monthly':
                print(f'You chose the ticker {meta_data_df['2. Symbol'].iloc[0]}.\n'
                      f'The data was last updated on {meta_data_df['3. Last Refreshed'].iloc[0]} on the {meta_data_df['4. Time Zone'].iloc[0]} standard time.')
            else:
                print(f'You chose the ticker {meta_data_df['2. Symbol'].iloc[0]}.\n'
                      f'The data was last updated on {meta_data_df['3. Last Refreshed'].iloc[0]} on the {meta_data_df['5. Time Zone'].iloc[0]} standard time.')

            fig = make_subplots(rows=len(stock_data_df.columns), cols=1, shared_xaxes=True,
                                subplot_titles=stock_data_df.columns, vertical_spacing=0.05)

            for i, col in enumerate(stock_data_df.columns):
                fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df[col], mode='lines', name=col),
                              row=i + 1, col=1)
            # Update layout
            fig.update_layout(
                title=f'{time_period.title()} stock data from {ticker}.',
                showlegend=True,
                height=800,
                width=1000, )
            fig.show()

            more_analytic = input('would you like to see more indepth analysis? y/n')
            print('what would you like to see?')
            print('1. The volatility of the stock \n'
                  '2. The Moving Averages for Stock Price (SMA)\n'
                  '3. ')

            while more_analytic != 'n':
                choice = int(input('Whats your choice?'))
                if choice == 1:
                    calculate_volatility()
                elif choice == 2:
                    number_datapoints = int(
                        input('over how many datapoint would you like to calculate the moving average?'))
                    calculate_sma(number_datapoints)
                elif choice == 3:
                    calculate_rsi(14)
                more_analytic = input('More analysis? y/n:')

            ticker = input('Give next ticker: ').upper()
            if ticker == 'q' or ticker == 'Q':
                break
            time_period = input('Choose new time period:').lower()
            new_file = create_file(time_period, ticker)
        else:
            ticker = input('New ticker: ').upper()
            time_period = input('Choose new time period:').lower()
            new_file = create_file(time_period, ticker)
    except Exception as e:
        print(f'An error occurred: {e}')
