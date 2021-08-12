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
    print('please, provide coin coin symbol')
    aSymbol = input()
    symbol_price = client.get_symbol_ticker(symbol=aSymbol)
    print(aSymbol, ' has the current price: ', symbol_price['price'])
    print('how many '+aSymbol+' do you want to sell?')
    aQuantity = input()
    print('proceeding to sell',aQuantity, ' ', aSymbol, 'do you agree? (y/n)')
    aDecision = input()
    if 'y' in aDecision:
        order = client.order_limit_sell(symbol=aSymbol,quantity=aQuantity,price=str(symbol_price['price']))
    else:
        print('nothing done')
    print('result: ', order)

except BinanceAPIException as e:
    # error handling goes here
    print(e)
except BinanceOrderException as e:
    # error handling goes here
    print(e)

