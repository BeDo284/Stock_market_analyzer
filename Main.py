import json
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

api_key1 = 'W59OQACAUZ0HS2N3'
api_key2 = 'TWGWL6U2XC4X2L6C'
today_date = datetime.now().strftime("%Y-%m-%d")
link_to_tickers = 'https://stockanalysis.com/stocks/'

response = None
valid_input = True
file_to_save = ''
start_date = None
end_date = None


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
    global start_date
    global end_date

    try:
        with open(file) as f:
            data = json.load(f)
        meta_data = pd.DataFrame(data['Meta Data'], index=['Meta Data'])
        if period == 'daily':
            stock_data = pd.DataFrame(data['Time Series (Daily)']).T
            stock_data.index = pd.to_datetime(stock_data.index)
            mask = (stock_data.index >= start_date) & (stock_data.index <= end_date)
            stock_data = stock_data[mask]
        elif period == 'intraday':
            stock_data = pd.DataFrame(data['Time Series (5min)']).T
        elif period == 'monthly':
            stock_data = pd.DataFrame(data['Monthly Time Series']).T
            stock_data.index = pd.to_datetime(stock_data.index)
            mask = (stock_data.index >= start_date) & (stock_data.index <= end_date)
            stock_data = stock_data[mask]
        elif period == 'weekly':
            stock_data = pd.DataFrame(data['Weekly Adjusted Time Series']).T
            stock_data.index = pd.to_datetime(stock_data.index)
            mask = (stock_data.index >= start_date) & (stock_data.index <= end_date)
            stock_data = stock_data[mask]
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
    stock_data_df['loss'] = stock_data_df['change'].apply(lambda x: abs(x) if x < 0 else 0)
    stock_data_df['Avg Gain'] = stock_data_df['gain'].rolling(window=window).mean()
    stock_data_df['Avg Loss'] = stock_data_df['loss'].rolling(window=window).mean()
    stock_data_df['RSI'] = 100 - (100 / (1 + stock_data_df['Avg Gain'] / stock_data_df['Avg Loss']))

    fig = make_subplots(rows=2, cols=1, subplot_titles=("RSI", "Close"))
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df['RSI'], mode='lines', name='RSI'), row=1, col=1)
    fig.add_shape(type="line",
                  x0=stock_data_df.index[0], y0=30, x1=stock_data_df.index[-1], y1=30,
                  line=dict(color="green", width=1.5, dash="dash"),
                  row=1, col=1)
    fig.add_shape(type="line",
                  x0=stock_data_df.index[0], y0=70, x1=stock_data_df.index[-1], y1=70,
                  line=dict(color="red", width=1.5, dash="dash"),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df['close'], mode='lines', name='Close'), row=2,
                  col=1)
    fig.update_layout(title_text="RSI and Close Data",
                      showlegend=True,
                      xaxis=dict(title='Date'))
    fig.show()


def calculate_macd():
    global fig
    ema_12 = stock_data_df['close'].ewm(span=12, min_periods=0, adjust=False).mean()
    ema_26 = stock_data_df['close'].ewm(span=26, min_periods=0, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, min_periods=0, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    stock_data_df['MACD'] = macd_line
    stock_data_df['Signal'] = signal_line
    stock_data_df['Histogram'] = macd_histogram

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.3)
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df['close'], mode='lines', name='Close Prices'), row=1,
                  col=1)
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=macd_line, mode='lines', name='MACD',
                             line=dict(color='purple')), row=2, col=1)
    fig.add_trace(go.Scatter(x=stock_data_df.index, y=signal_line, mode='lines', name='Signal Line',
                             line=dict(color='orange', dash='dot')), row=2, col=1)
    # Add the histogram with colors assigned to each bar individually
    colors = ['rgb(0,255,0)' if val >= 0 else 'rgb(255,0,0)' for val in stock_data_df['Histogram']]
    fig.add_trace(
        go.Bar(x=stock_data_df.index, y=stock_data_df['Histogram'], name='Histogram', marker=dict(color=colors)), row=2,
        col=1)

    # Customize the chart
    fig.update_xaxes(rangeslider=dict(visible=True))
    fig.update_layout(plot_bgcolor='#efefff', font_family='Monospace', font_color='#000000', font_size=20, width=1500,
                      height=1000)
    fig.update_layout(
        title=f"MACD chart for {ticker}"
    )
    # Show the chart
    fig.show()


def engulfing():
    global fig

    def is_engulfing(candle1, candle2):
        """
        Check if candle2 engulfs candle1
        """
        if candle2['open'] < candle1['close'] and candle2['close'] > candle1['open']:
            return True
        return False

    engulfing_patterns = []

    for s in range(1, len(stock_data_df)):
        prev_index = stock_data_df.index[s - 1]
        curr_index = stock_data_df.index[s]
        prev_candle = stock_data_df.loc[prev_index]
        curr_candle = stock_data_df.loc[curr_index]
        if is_engulfing(prev_candle, curr_candle):
            engulfing_patterns.append((prev_index, curr_index))

    print("Engulfing Patterns:")
    for pattern in engulfing_patterns:
        print("Engulfing pattern on {} at {}".format(pattern[0], pattern[1]))
    # Plotting using Plotly
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(x=stock_data_df.index,
                                 open=stock_data_df['open'],
                                 high=stock_data_df['high'],
                                 low=stock_data_df['low'],
                                 close=stock_data_df['close'],
                                 name='Candlestick'))
    # Add engulfing pattern areas
    for pattern in engulfing_patterns:
        fig.add_shape(type="rect",
                      x0=pattern[0], y0=min(stock_data_df['low']), x1=pattern[1], y1=max(stock_data_df['high']),
                      line=dict(color="Red", width=2),
                      fillcolor="Red", opacity=0.3,
                      layer="below")

    fig.update_layout(title='Stock Price with Engulfing Patterns',
                      xaxis_title='Date',
                      yaxis_title='Price')

    fig.show()


def get_valid_dates():
    global start_date
    global end_date

    valid_date = False

    while not valid_date:
        start_date_str = input('chose a start date(yyyy-mm-dd): ')
        end_date_str = input('chose a end date(yyyy-mm-dd): ')
        if start_date_str == "s":
            start_date = datetime.now() - timedelta(days=365)
        else:
            try:
                start_date = pd.to_datetime(start_date_str)
            except ValueError:
                print("Invalid date format. Please enter dates in YYYY-MM-DD format or 's' for 100 days ago.")
                continue

        if end_date_str == "t":
            end_date = datetime.now()
        else:
            try:
                end_date = pd.to_datetime(end_date_str)
            except ValueError:
                print("Invalid date format. Please enter dates in YYYY-MM-DD format or 't' for today.")
                continue

            # Convert start_date_str and end_date_str to datetime objects
        if start_date == "s" or end_date == "t":
            valid_date = True
        else:
            if start_date >= end_date:
                print("Start date must be before end date.")
            else:
                valid_date = True

    return start_date, end_date


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
        get_valid_dates()
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
                                subplot_titles=stock_data_df.columns,
                                vertical_spacing=0.05)

            for i, col in enumerate(stock_data_df.columns):
                fig.add_trace(go.Scatter(x=stock_data_df.index, y=stock_data_df[col], mode='lines', name=col),
                              row=i + 1, col=1)

            fig.update_xaxes(rangeslider=dict(visible=False))
            # Update layout
            fig.update_layout(
                title=f'{time_period.title()} stock data from {ticker}.',
                showlegend=True,
                height=800,
                width=1000,
            )
            fig.show()

            more_analytic = input('would you like to see more indepth analysis? y/n')
            print('what would you like to see?')
            print('1. The volatility of the stock \n'
                  '2. The Moving Averages for Stock Price (SMA)\n'
                  '3. The Relative Strength Index (RSI)\n'
                  '4. The Moving Average Convergence Divergence (MACD) \n'
                  '5. Engulfing pattern')

            while more_analytic != 'n':
                choice = int(input('Whats your choice?'))
                if choice == 1:
                    calculate_volatility()
                elif choice == 2:
                    number_datapoints = int(
                        input('Over how many datapoint would you like to calculate the moving average?'))
                    calculate_sma(number_datapoints)
                elif choice == 3:
                    calculate_rsi(14)
                elif choice == 4:
                    calculate_macd()
                elif choice == 5:
                    engulfing()
                else:
                    print(f'{choice} is not a function.')

                more_analytic = input('Another analysis? y/n:')

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
