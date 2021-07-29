import platform
import os, sys, time
import mysql.connector
import keyboard
import json
from pathlib import Path


from datetime import datetime, timedelta
from utilities import updateAvg, definePerformance, getRefValues
from mysql_generic_script import (
    create_connection,
    execute_user_query,
    insert_into_table,
)

#testing purchase order

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

# init
# if we are in linux, set a root, if not set another
if platform.system() == "Linux":
    with open("/etc/projects_keys/binance_api_keys/api_key.txt") as f:
        api_key = f.read().strip()
    with open("/etc/projects_keys/binance_api_keys/api_secret.txt") as f:
        api_secret = f.read().strip()
    with open("/etc/projects_keys/binance_api_keys/db_credentials.json") as credentials:
        dbcredentials = json.load(credentials)
else:
    with open(r"C:\Users\User\projects_keys\binance_api_keys\api_key.txt") as f:
        api_key = f.read().strip()
    with open(r"C:\Users\User\projects_keys\binance_api_keys\api_secret.txt") as f:
        api_secret = f.read().strip()
    with open(
        r"C:\Users\User\projects_keys\binance_api_keys\db_credentials.json"
    ) as credentials:
        dbcredentials = json.load(credentials)

#binance client
client = Client(api_key, api_secret)

#connection of db
DBconnection =None
try:
    DBconnection = mysql.connector.connect(
        host=dbcredentials["DBHOST"], 
        user=dbcredentials["DBUSER"], 
        passwd=dbcredentials["DBPASSWORD"], 
        database=dbcredentials["DBNAME"]
    )
    # print("Connection to MySQL DB successful")
except Exception as e:
    print(f"The error '{e}' occurred")
    DBconnection = False

if DBconnection == False:
    print("db server not available, leaving the system")
    sys.exit()
print('connexion created')
cursor = DBconnection.cursor()


try:
    while True:
        sell_query = ""
        aQuery =""
        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`='VETUSDT' and `side`='SELL' and `status`='NEW'")
        sell_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
        aQuery =""
        if len(sell_query)==0:
            print('no sell order')
            buy_query = ""
            aQuery =""
            aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`='VETUSDT' and `side`='BUY' and `status`='NEW'")
            buy_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
            aQuery =""
            if len(buy_query)==0:
                print('no purchase order, then we go to sell')
            else:
                print('buying yet')

        else:
            print('selling yet')
        time.sleep(10)
    # order = client.order_limit_sell(symbol='SHIBUSDT',quantity=1700000,price='0.00000617')
    # print("order: ", order)
    # orderId = order["orderId"]
    #print('Sell order placed at {}\n'.format(sellPrice))
    # while True:
    #     currentOrder = client.get_order(symbol=pair,orderId=orderId)
    #     if currentOrder['status']=='FILLED':
    #         print("Sold: {} at {}".format(quantity,sellPrice))
    #         break
    #         print(".")
    # # buy_limit = client.create_order(
    # #     symbol='SHIBUSDT',
    # #     side='BUY',
    # #     type='LIMIT',
    # #     timeInForce='GTC',
    # #     quantity=1700000,
    # #     price='0.00000615')
    # # print("buy_limit: ", buy_limit)
    # currentOrder = client.get_order(symbol='SHIBUSDT',orderId='156166591')

    # print('current order: ', currentOrder)

    # if currentOrder['status']=='FILLED':
    #     print("vendida")
    #     print(".")

except BinanceAPIException as e:
    # error handling goes here
    print(e)
except BinanceOrderException as e:
    # error handling goes here
    print(e)


    #buy_limit:  {'symbol': 'SHIBUSDT', 'orderId': 156166591, 'orderListId': -1, 'clientOrderId': 'sOC70URxat2NLgniHF55wd', 'transactTime': 1627537674447, 'price': '0.00000615', 'origQty': '1700000.00', 'executedQty': '0.00', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'fills': []}


   # order:  {'symbol': 'SHIBUSDT', 'orderId': 156175083, 'orderListId': -1, 'clientOrderId': 'O4VHkt2ix9H4Ijv4g4hnYj', 'transactTime': 1627539888395, 'price': '0.00000617', 'origQty': '1700000.00', 'executedQty': '1700000.00', 'cummulativeQuoteQty': '10.48900000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 
##'SELL', 'fills': [{'price': '0.00000617', 'qty': '1700000.00', 'commission': '0.01048900', 'commissionAsset': 'USDT', 'tradeId': 54944998}]}
