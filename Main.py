import json
import os
from datetime import datetime

import pandas as pd
import requests

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
        print("File exists!")
        valid_input = False
    else:
        print("File does not exist.")
        if period == 'daily':
            url_daily = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key2}'
            print(url_daily)
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
            except Exception as e:
                print(f'An error occurred: {e}')
        if 'Error Message' in data:
            print("Wrong stock market ticker. Choose a new one!")
            # os.remove(file_to_save)  # Delete the file
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
        meta_data = pd.DataFrame(data['Meta Data'], index=['Meta Data']).T
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
    except Exception as e:
        print(f'An error occurred: {e}')
    return meta_data, stock_data


print("Welcome to StockAnalyzer v1.0! Analyze stock data effortlessly. \
Choose a company and time period to get started.")

print(f"If you don't know the right ticker for a company. Check this website:\
{link_to_tickers}.")

ticker = input('Choose a ticker (company):').upper()

interval = '5'
print('The available time period options are daily, intraday, monthly or weekly.')

time_period = input().lower()
new_file = create_file(time_period, ticker)

if check_api_error_message():
    meta_data_df, stock_data_df = create_dataframes(time_period, new_file)
    print(stock_data_df)
else:
    print('nok')
