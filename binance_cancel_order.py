#we pretend to gett all open orders, cancel them and revert database status if any
#first connecting to the api and to the db
import platform
import os, sys, time
import mysql.connector
import keyboard
import json
from pathlib import Path


from binance.client import Client
from datetime import datetime, timedelta
from utilities import updateAvg, definePerformance, getRefValues, updateDBTable_number, updateDBTable_string

from mysql_generic_script import (
    create_connection,
    execute_user_query,
    insert_into_table,
)


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

#getting all open orders
currentOpenOrders=[]
try:
    currentOpenOrders = client.get_open_orders()
    if len(currentOpenOrders) > 0:
        print('current number open orders: ', len(currentOpenOrders))
        #iterating over every order
        for an_order in currentOpenOrders:
            print('symbol: ', an_order['symbol'])
            print('orderId: ', an_order['orderId'])
            print('side: ', an_order['side'])
            #timestamp to readable time *********
            print('time: ', an_order['time'])
            print(' do you want to delete this order? (y or n only)')
            input1 = input()
            if 'y' in input1:
                print('deleting ordr number ', an_order['orderId'])
                #update table assets_transactions
                try:
                    aQuery = "UPDATE `assets_transactions` SET `status`='FILLED' WHERE `symbol`="+'"'+an_order['symbol']+'"'+" and `side`="+'"'+an_order['side']+'"'
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
                except Exception as e:#correction on 01.08
                    print(e)
                    print("error updating status to db")
                    sys.exit()
                #update table assets_transactions
                try:
                    aQuery = "UPDATE `ref_price` SET `status`='sold' WHERE `symbol`="+'"'+an_order['symbol']+'"'
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
                except Exception as e:#correction on 01.08
                    print(e)
                    print("error updating status in ref_price")
                    sys.exit()
                #canceling order
                try:
                    order = client.cancel_order(symbol=an_order['symbol'],orderId=an_order['orderId'])
                    print('sell order: ', order)
                except Exception as e:
                    print('error: ',e)
                    print('order not cancelled, please try later')
    else:
        print('no open order, I quit ')
        sys.exit()
except Exception as e:
    print('exception getting open orders: ', e)

