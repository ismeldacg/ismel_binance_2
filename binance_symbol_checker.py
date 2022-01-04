import os, sys, time

from binance.client import Client



# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')


#client = Client('LTFhd56GMxSW6rqVXFAREBYywPGRZyBnFXMNaoBDQptPv9k6Z58ECngWchs53w06', 'IJgLxUQx6FTq9rnzzUt85amGOcMPgyT540MzbKjISHDT7BMmLMBhMBYSVUoCauUF')
client = Client('EkkHlk53cn7yrJ7pA6UksR3gEKMRhgb3mrO6GLSoYy7De43dvU1qD5SVL6l5Bbny', 'yFYH3jUXQt4PUbDHGnbLd0X54ifjhnBA7k3GZh8FheKvnRwE9zby85QWAJSwnqV8')

#client.API_URL = 'https://testnet.binance.vision/api'


# get balances for all assets & some account information
#print(client.get_account())
# get balance for a specific asset only (BTC)
#print('only btc *******')
#print(client.get_asset_balance(asset='BTC'))

# get latest price from Binance API - ok
xrp_price = client.get_symbol_ticker(symbol="TRXUSDT")
print('xrp price*******: ', xrp_price)