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
from binance_sell2 import sellOperation
from binance_buy import buyOperation


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
#obtaining symbols from db
results_query = ""
aQuery =""
aQuery = ("SELECT * FROM `assets_symbols`")
results_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
#iterate over dictionary to get names and symbols
symbol_list=[]
for an_asset in results_query:
    symbol_list.append(an_asset[2])


ref_price_dict, ref_sd_dict, ref_perf_dict=getRefValues(DBconnection, cursor)
DBconnection.commit()
cursor.close()
DBconnection.close()

 #creating connection to db
DBconnection = None
cursor = None


while not(keyboard.is_pressed('q')):
    print('in automatic loop, please press "q" to stop')
    #connecting again
    #creating connection to db
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
    cursor = DBconnection.cursor()
    #checking if updated to date
    #checking date to update
    results_query = ""
    aQuery =""
    aQuery = ("SELECT `updated` FROM `ref_price` limit 1")
    last_updated=execute_user_query(connection=DBconnection, aQuery=aQuery)
    last_update_list=last_updated[0]
    #current date 
    print('last_update_date: ', last_update_list[0])
    print('datetime.today() for update: ', datetime.today())
    print('update operation: ', datetime.today()-last_update_list[0])
    #testing if must be updated
    #changed timedelta to hours on 11.12.2020
    if (datetime.today()-last_update_list[0])>timedelta(hours=1):
        #proceeding to update
        print("going to update******")
        updateAvg(DBconnection, cursor)
        definePerformance(DBconnection, cursor)
        ref_price_dict = {}
        ref_sd_dict = {}
        ref_perf_dict = {}
        ref_price_dict, ref_sd_dict, ref_perf_dict=getRefValues(DBconnection, cursor)
        print('commiting to db')
        DBconnection.commit()
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
        if not(keyboard.is_pressed('q')):
            try:
                symbol_price = client.get_symbol_ticker(symbol=aSymbol)
                #get performance
                ref_symbol_perf=ref_perf_dict[symbol_price["symbol"]]
                if ref_symbol_perf==0.0:
                    ref_symbol_perf=0.1
                #get values of a coin
                ref_symbol_price=ref_price_dict[symbol_price["symbol"]]#getting price of current symbol
                ref_symbol_sd = ref_sd_dict[symbol_price["symbol"]]
                ref_symbol_status = ref_status_dict[symbol_price["symbol"]]


                if aSymbol=="XRPUSDT":
                    print("ref_symbol_status, status en db: ", ref_symbol_status)
                    print("performance calculado: ", ref_symbol_perf)
                    print("precio real de la moneda: ", symbol_price)
                    print("ref_symbol_price, price in db: ", ref_symbol_price)
                    print("ref_symbol_sd claculated: ", ref_symbol_sd)



                recommendation="do nothing"
                #agregar más parentesis, seleccionar una moneda y fijarle el precio para probar
                print('evaluating ', aSymbol)
                if float(symbol_price["price"]) > (ref_symbol_price+(ref_symbol_perf*ref_symbol_sd)) and (ref_symbol_status=="bought") :
                #condition fulfilled to sell 30.12.2021
                #begins sell operation
                    recommendation = sellOperation(aSymbol, cursor, symbol_price, client, ref_symbol_price, DBconnection, recommendation)
                #finishes sell operation here 30.12.2021

                elif (float(symbol_price["price"]) < ref_symbol_price-(ref_symbol_perf*ref_symbol_sd)) and (ref_symbol_status=="sold" or ref_symbol_status==""):
                    recommendation = buyOperation(aSymbol, cursor, symbol_price, client, ref_symbol_price, DBconnection, recommendation)
                #elif buy order open 
                elif (ref_symbol_status=="buy order open") :
                    print('recommended to buy, but buy order open, we must check the status')
                    recommendation="do nothing"
                    print('there is an open buy order, so I have to check buy status')
                    aQuery=""
                    aQuery = ("SELECT *  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'")
                    cursor.execute(aQuery)
                    result_tuple = cursor.fetchall()
                    if len(result_tuple)>0:
                        orderId=result_tuple[0]
                        #get order from binance
                        print('result_tuple array: ', result_tuple[0])
                        print('orderId[4]: ', orderId[4])
                        currentOrder={}
                        try:
                            currentOrder = client.get_order(symbol=aSymbol,orderId=orderId[4])
                            #update status
                            if  'FILLED' in currentOrder['status']:
                                aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+currentOrder['status']+'"'+" WHERE `side`='BUY' and `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                    #commiting to db
                                DBconnection.commit()
                                #update status
                                aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+currentOrder['cummulativeQuoteQty']+'"'+" WHERE `side`='BUY' and `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                                recommendation="do nothing"
                                ref_symbol_status="bought"
                                #store recommendation to db
                                aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                                
                        except Exception as e:
                            print('error updating buy order: ', e)

                #elif sell order open 
                elif  (ref_symbol_status=="sell order open") :
                    print(' sell order open, we must check the status')
                    recommendation="do nothing"
                    print('there is an open sell order, so I have to check sell status')
                    aQuery=""
                    aQuery = ("SELECT *  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'") 
                    #removed status = new to test and `status` ='new'. 
                    cursor.execute(aQuery)
                    result_tuple = cursor.fetchall()
                    if len(result_tuple)>0:
                        orderId=result_tuple[0]
                        #get order from binance
                        print('result_tuple array: ', result_tuple[0])
                        print('orderId[4]: ', orderId[4])
                        currentOrder={}
                        try:
                            currentOrder = client.get_order(symbol=aSymbol,orderId=orderId[4])
                            #update status
                            if  'FILLED' in currentOrder['status']:
                                aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+currentOrder['status']+'"'+" WHERE `side`='SELL' and `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                    #commiting to db
                                DBconnection.commit()
                                #update status
                                aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+currentOrder['cummulativeQuoteQty']+'"'+" WHERE `side`='SELL' and `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                                recommendation="do nothing"
                                ref_symbol_status="sold"
                                #store recommendation to db
                                aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                                
                        except Exception as e:
                            print('error updating buy order: ', e)
                #getting current time
                print("I recommend you to ",recommendation)
                now = datetime.now()
                #store to db
                values = (aSymbol,now,symbol_price["price"],recommendation)
                #query
                aQuery = "INSERT INTO assets_historical (symbol,datetime,price, recommendation) VALUES (%s,%s,%s,%s)"
                cursor.execute(aQuery, values)
                #commiting to db
                DBconnection.commit()
                #inserting delay
                #print("delay time")
                time.sleep(10)
                #elif  (ref_symbol_status=="sell order open") : nuevo status que procesar
            except Exception as e:
                print("exception found here: ", e)
                time.sleep(60)
                #delay, after this returns to for loop, but db connection is still open,
                #if repeated, we must read the error, and decide. 29.07
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



