import requests
import pprint as pp

api_key = 'W59OQACAUZ0HS2N3'
key_word = 'nvidia'
symbol = 'NVDA'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}'
r = requests.get(url)
data = r.json()
pp.pprint(data)
