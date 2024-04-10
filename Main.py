import requests
import pprint as pp

key = 'W59OQACAUZ0HS2N3'
key_word = input()
url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={key_word}&apikey=W59OQACAUZ0HS2N3'
r = requests.get(url)
data = r.json()

pp.pprint(data)
