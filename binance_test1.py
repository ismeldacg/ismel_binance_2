import platform
import os, sys, time
import mysql.connector
import keyboard
import json
from pathlib import Path


from binance.client import Client
from datetime import datetime, timedelta
from utilities import updateAvg, definePerformance

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
   
   

client = Client(api_key, api_secret)

#creating connection to db
DBconnection = create_connection(
        dbcredentials["DBHOST"], 
        dbcredentials["DBUSER"], 
        dbcredentials["DBPASSWORD"], 
        dbcredentials["DBNAME"])
cursor = DBconnection.cursor()
if DBconnection == False:
    print("db server not available, leaving the system")
    sys.exit()
print('connexion created')
#obtaining symbols from db
results_query = ""
aQuery =""
aQuery = ("SELECT * FROM `assets_symbols`")
results_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
#iterate over dictionary to get names and symbols
symbol_list=[]
for an_asset in results_query:
    symbol_list.append(an_asset[2])

#print("symbol_list: ", symbol_list)
#obtaining reference price
ref_price = ""
aQuery =""
aQuery = ("SELECT * FROM `ref_price`")
ref_price_tuples=execute_user_query(connection=DBconnection, aQuery=aQuery)
ref_price_dict = {}
#print("ref_price_tuples: ", ref_price_tuples)
for a_tuple in ref_price_tuples:
    ref_price_dict[a_tuple[1]]=a_tuple[2]
#print("ref_price_dict: ", ref_price_dict)
ref_sd_dict = {}
for a_tuple in ref_price_tuples:
    ref_sd_dict[a_tuple[1]]=a_tuple[4]
#getting the performance value
ref_perf_dict = {}
#print("ref_price_tuples: ", ref_price_tuples)
for a_tuple in ref_price_tuples:
    ref_perf_dict[a_tuple[1]]=a_tuple[6]
#print("ref_perf_dict: ", ref_perf_dict)
#closing initial connection
#closing db connection
DBconnection.commit()
cursor.close()
DBconnection.close()

 #creating connection to db
DBconnection = None
cursor = None


while not(keyboard.is_pressed('s') and keyboard.is_pressed('t')):
    print('in automatic loop, please press and hold "s" and "t" simultaneously to stop')
    #connecting again
    #creating connection to db
    DBconnection = create_connection(dbcredentials["DBHOST"], 
        dbcredentials["DBUSER"], 
        dbcredentials["DBPASSWORD"], 
        dbcredentials["DBNAME"])
    cursor = DBconnection.cursor()
    #checking if updated to date
    #checking date to update
    results_query = ""
    aQuery =""
    aQuery = ("SELECT `updated` FROM `ref_price` limit 1")
    last_updated=execute_user_query(connection=DBconnection, aQuery=aQuery)
    last_update_list=last_updated[0]
    #current date 
    print('last_update_list: ', last_update_list[0])
    #testing if must be updated
    if (datetime.today()-last_update_list[0])>timedelta(days=1):
        #proceeding to update
        #print("going to update******")
        updateAvg(DBconnection, cursor)
        definePerformance(DBconnection, cursor)
    #getting symbols status
    #obtaining reference price
    ref_status = ""
    aQuery =""
    aQuery = ("SELECT * FROM `ref_price`")
    ref_status_tuples = None
    try:
        cursor.execute(aQuery)
        ref_status_tuples = cursor.fetchall()
    except Exception as e:
        # fatal error
        ref_status_tuples=None
        print(f"The error '{e}' occurred")
    #creating and filling out status dictionary
    ref_status_dict = {}
    for a_status in ref_status_tuples:
        try:
            ref_status_dict[a_status[1]]=a_status[5]
        except Exception as e:
            ref_status_dict[a_status[1]]=""
    #print("ref_status_dict: ",ref_status_dict)
    #OJO must set conditions to execute the loop
    for aSymbol in symbol_list:
        if not(keyboard.is_pressed('s') and keyboard.is_pressed('t')):
            try:
                symbol_price = client.get_symbol_ticker(symbol=aSymbol)
                #get performance
                ref_symbol_perf=ref_perf_dict[symbol_price["symbol"]]
                if ref_symbol_perf==0.0:
                    ref_symbol_perf=0.1
                #get time
                ref_symbol_price=ref_price_dict[symbol_price["symbol"]]#getting price of current symbol
                #print("ref_symbol_price: ", ref_symbol_price)
                ref_symbol_sd = ref_sd_dict[symbol_price["symbol"]]
                #print("ref_symbol_sd: ", ref_symbol_sd)
                ref_symbol_status = ref_status_dict[symbol_price["symbol"]]
                #print("ref_symbol_status: ", ref_symbol_status)
                recommendation="do nothing"
                # print("symbol_price[price]: ",symbol_price["price"] , 
                # "ref_symbol_price: ",ref_symbol_price, 
                # "ref_symbol_status: ",ref_symbol_status,
                # "ref_symbol_perf ", ref_symbol_perf)
                if float(symbol_price["price"]) > (ref_symbol_price+(ref_symbol_perf*ref_symbol_sd)) and (ref_symbol_status=="bought") :
                    recommendation="sell"
                    ref_symbol_status="sold"
                    #after succcesfull sold status must be changed to sold
                    #store to db
                    #query
                    aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                    cursor.execute(aQuery)
                elif (float(symbol_price["price"]) < ref_symbol_price) and (ref_symbol_status=="sold" or ref_symbol_status==""):
                    recommendation="buy"
                    #after succcesfull bought status must be changed to bought
                    ref_symbol_status="bought"
                    #after succcesfull sold status must be changed to sold
                    #store to db
                    aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                    cursor.execute(aQuery)
                #getting current time
                print("I recommend you to ",recommendation)
                now = datetime.now()
                #store to db
                values = ('',aSymbol,now,symbol_price["price"],recommendation)
                #query
                aQuery = "INSERT INTO assets_historical (id,symbol,datetime,price, recommendation) VALUES (%s, %s,%s,%s,%s)"
                cursor.execute(aQuery, values)
                #inserting delay
                print("delay time")
                time.sleep(10)
            except Exception as e:
                print("exception found here")
                DBconnection.commit()
                cursor.close()
                DBconnection.close()
                print(e)
        else:
            print("stopped by user")
            #closing db connection
            DBconnection.commit()
            cursor.close()
            DBconnection.close()
            print("finished!")
            sys.exit()
    #closing after every loop
    DBconnection.commit()
    cursor.close()
    DBconnection.close()
else:
    print("stopped by user")
    #closing db connection
    DBconnection.commit()
    cursor.close()
    DBconnection.close()
    print("finished!")
    sys.exit()



