import platform
import os, sys, time
import mysql.connector
import keyboard
import json
from pathlib import Path


from binance.client import Client
from datetime import datetime, timedelta
from utilities import updateAvg, definePerformance, getRefValues

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
    #print('last_update_date: ', last_update_list[0])
    #testing if must be updated
    if (datetime.today()-last_update_list[0])>timedelta(days=1):
        #proceeding to update
        print("going to update******")
        updateAvg(DBconnection, cursor)
        definePerformance(DBconnection, cursor)
        ref_price_dict, ref_sd_dict, ref_perf_dict=getRefValues(DBconnection, cursor)
        print('commiting to db')
        DBconnection.commit()
        #sys.exit()
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
                #get time
                ref_symbol_price=ref_price_dict[symbol_price["symbol"]]#getting price of current symbol
                #print("ref_symbol_price: ", ref_symbol_price)
                ref_symbol_sd = ref_sd_dict[symbol_price["symbol"]]
                #print("ref_symbol_sd: ", ref_symbol_sd)
                ref_symbol_status = ref_status_dict[symbol_price["symbol"]]
                #print("ref_symbol_status: ", ref_symbol_status)
                recommendation="do nothing"
                #agregar más parentesis, seleccionar una moneda y fijarle el precio para probar
                print('evaluating ', aSymbol)
                if float(symbol_price["price"]) > (ref_symbol_price+(ref_symbol_perf*ref_symbol_sd)) and (ref_symbol_status=="bought") :
                    #query to know if there is an order
                    print("go to sell ", aSymbol)
                    sell_query=[]
                    buy_query=[]
                    try:
                        aQuery=''
                        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='NEW'")
                        cursor.execute(aQuery)
                        sell_query = cursor.fetchall()
                    except Exception as e:
                        print('exception because of no sell order')
                    try:
                        aQuery=''
                        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='NEW'")
                        cursor.execute(aQuery)
                        buy_query = cursor.fetchall()
                    except Exception as e:
                        print('no buy order')
                    
                    #print('no exception in sell query 1')

                    if len(sell_query)==0 and len(buy_query)==0:
                        print('no active purchase order, no active sell order')
                        cummulativeQuoteQty=[]
                        cummulativeQuantity=0
                        this_symbol_price=""
                        try:
                            aQuery = ("SELECT `cummulativeQuoteQty` FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='FILLED'")
                            cummulativeQuoteQty = cursor.fetchall(aQuery)
                        except Exception as e:
                            print('not sold order filled')
                        if len(cummulativeQuoteQty)==0:#if there is not value or record
                            print('no filled sold order for ',aSymbol)
                            cummulativeQuantity=20#assigning a value
                        else:  
                            cummulativeQuantity1=cummulativeQuoteQty[0]
                            cummulativeQuantity=cummulativeQuantity1[0]
                        #exchaging symbol price
                        current_str_symbol_price=symbol_price["price"]
                        print('current_str_symbol_price: ', current_str_symbol_price)
                        current_symbol_price=float(current_str_symbol_price)
                        #trying to get first 9 characters of price
                        try:
                            this_symbol_price = current_str_symbol_price[0:10]
                            print('this_symbol_price 0:10: ', this_symbol_price)
                        except:
                            this_symbol_price = current_str_symbol_price
                            print('this_symbol_price', this_symbol_price)
                        
                        coins_quantity_1=cummulativeQuantity/current_symbol_price
                        coins_quantity=round(coins_quantity_1,0)-1#to avoid insuficiente funds
                        print('selling '+str(coins_quantity)+ 'of '+aSymbol)
                        #price
                        #trying to get first 9 characters of price
                        current_str_symbol_price=symbol_price["price"]
                        print('current_str_symbol_price: ', current_str_symbol_price)
                        current_symbol_price=float(current_str_symbol_price)
                        #trying to get first 9 characters of price
                        # try:
                        #     this_symbol_price = current_str_symbol_price[0:10]
                        #     print('this_symbol_price 0:10: ', this_symbol_price)
                        # except:
                        #     this_symbol_price = current_str_symbol_price
                        #     print('this_symbol_price', this_symbol_price)
                        try:
                            order = client.order_limit_sell(symbol=aSymbol,quantity=coins_quantity,price=this_symbol_price)
                            print('sell order: ', order)
                        except Exception as e:
                            if 'APIError(code=-2010)' in str(e):
                                try:
                                    coins_quantity2=coins_quantity-1
                                    order = client.order_limit_sell(symbol=aSymbol,quantity=coins_quantity2,price=this_symbol_price)
                                    print('sell order 2: ', order)
                                except Exception as e:
                                    print(e)
                                    print('exception when selling ', aSymbol)
                                    #if insuficient funds, purchase with less******
                                    sys.exit()
                            else:
                                print(e)
                                print('exception when selling ', aSymbol)
                                #if insuficient funds, purchase with less******
                                sys.exit()
                        #update data base or creating the dataset
                        #query if there is a filled order, 
                        sell_filled_query=[]
                        try:
                            aQuery=''
                            aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='FILLED'")
                            cursor.execute(aQuery)
                            sell_filled_query = cursor.fetchall()
                        except:
                            print('not filled sell order')
                        if len(sell_filled_query)!=0:
                            print('updating selling order of ',aSymbol)
                            #updating
                            #update status
                            try:
                                aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+sell_filled_query['cummulativeQuoteQty']+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                                aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+sell_filled_query['status']+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                            except:
                                print(e)
                                print("error inserting to db")
                                sys.exit()
                        else:
                            print('inserting selling order of ',aSymbol)
                            #if we buy, then we can store to db
                            try:
                                values = (order['symbol'], order['side'], order['status'], order['orderId'], order['executedQty'], order['price'], order['cummulativeQuoteQty'])
                                aQuery = "INSERT INTO assets_transactions (symbol,side,status, orderId, executedQty, price, cummulativeQuoteQty) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                                cursor.execute(aQuery, values)
                                #commiting to db
                                DBconnection.commit()
                                recommendation="sell"
                                ref_symbol_status="sold"
                                #after succcesfull sold status must be changed to sold
                                #store to db
                                #query
                                aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                            except:
                                print(e)
                                print("error inserting to db")
                                sys.exit()
                    elif len(sell_query)!=0:
                        print('there is an open sell order, so I can not sell')
                        aQuery=""
                        aQuery = ("SELECT `orderId`  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='NEW'")
                        cursor.execute(aQuery)
                        result_tuple = cursor.fetchall()
                        orderId=result_tuple[0]
                        #get order from binance
                        print('result_tuple array: ', result_tuple[0])
                        print('orderId[4]: ', orderId[4])
                        currentOrder={}
                        currentOrder = client.get_order(symbol=aSymbol,orderId=orderId[4])
                        #update status
                        if  'filled' in currentOrder['status']:
                            aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+currentOrder['status']+'"'+" WHERE `side`='SELL' and `symbol`="+'"'+aSymbol+'"'
                            cursor.execute(aQuery)
                            #commiting to db
                            DBconnection.commit()
                            #update status
                            aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+currentOrder['cummulativeQuoteQty']+'"'+" WHERE `side`='SELL' and `symbol`="+'"'+aSymbol+'"'
                            cursor.execute(aQuery)
                            #commiting to db
                            DBconnection.commit()
                    #check if there is an open buy order
                    elif len(buy_query)!=0:
                        print('there is an open buy order, so I can not sell')
                        aQuery=""
                        aQuery = ("SELECT `orderId`  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='NEW'")
                        cursor.execute(aQuery)
                        orderId = cursor.fetchall()
                        #get order from binance
                        currentOrder={}
                        currentOrder = client.get_order(symbol=aSymbol,orderId=orderId[0])
                        #update status
                        if  'filled' in currentOrder['status']:
                            aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+currentOrder['status']+'"'+" WHERE `side`='BUY' and `symbol`="+'"'+aSymbol+'"'
                            cursor.execute(aQuery)
                            #commiting to db
                            DBconnection.commit()
                            #update status
                            aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+currentOrder['cummulativeQuoteQty']+'"'+" WHERE `side`='BUY' and `symbol`="+'"'+aSymbol+'"'
                            cursor.execute(aQuery)
                            #commiting to db
                            DBconnection.commit()
                    
                elif (float(symbol_price["price"]) < ref_symbol_price) and (ref_symbol_status=="sold" or ref_symbol_status==""):
                    print('going to buy ', aSymbol)
                    #query to know if there is an order
                    buy_query=[]
                    buy_query_filled=[]
                    try:
                        aQuery=''
                        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='NEW'")
                        cursor.execute(aQuery)
                        buy_query = cursor.fetchall()
                    except Exception as e:
                        print('no new buy order')
                    try:
                        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='FILLED'")
                        cursor.execute(aQuery)
                        buy_query_filled = cursor.fetchall()
                    except Exception as e:
                        print('no filled buy order')
                    if len(buy_query)==0:
                        print('no purchase order, then we go to buy')
                        #getting the last sold price
                        cummulativeQuoteQty=[]
                        cummulativeQuantity=0
                        try:
                            aQuery = ("SELECT `cummulativeQuoteQty` FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='FILLED'")
                            cursor.execute(aQuery)
                            cummulativeQuoteQty = cursor.fetchall()
                        except Exception as e:
                            print('error in select cummulativeQuoteQty ',e)

                        print('cummulativeQuoteQty: ', cummulativeQuoteQty)

                        if len(cummulativeQuoteQty)==0:
                            print('getting last sold price if any')
                            cummulativeQuantity=20    
                        else:
                            cummulativeQuantity1=cummulativeQuoteQty[0]
                            cummulativeQuantity=cummulativeQuantity1[0]
                        current_str_symbol_price=symbol_price["price"]
                        print('current_str_symbol_price: ', current_str_symbol_price)
                        current_symbol_price=float(current_str_symbol_price)
                        #trying to get first 9 characters of price
                        try:
                            this_symbol_price = current_str_symbol_price[0:10]
                            print('this_symbol_price 0:10: ', this_symbol_price)
                        except:
                            this_symbol_price = current_str_symbol_price
                            print('this_symbol_price', this_symbol_price)
                        print('cummulativeQuantity: ', cummulativeQuantity)
                        coins_quantity_1=cummulativeQuantity/current_symbol_price
                        coins_quantity=round(coins_quantity_1,0)
                        #print("this_symbol_price: ", "'"+this_symbol_price+"'")
                        print('buying '+str(coins_quantity)+ ' '+aSymbol)
                        buy_limit=None
                        try:
                            buy_limit = client.create_order(
                                symbol=aSymbol,
                                side='BUY',
                                type='LIMIT',
                                timeInForce='GTC',
                                quantity=coins_quantity,
                                price=this_symbol_price)
                            print('buy order ',buy_limit)
                        except Exception as e:
                            print(e)
                            print("error buying ", aSymbol)
                            if "APIError(code=-1021)" in str(e):
                                break
                            else:
                                sys.exit()
                        #if we buy, then we can store to db
                        try:
                            #if no new, no filled, then create at first time
                            if len(buy_query)==0 and len(buy_query_filled)==0:
                                try:
                                    #print('inserting value:' , buy_limit['symbol'],'BUY',buy_limit['status'],buy_limit['orderId'])
                                    values = (buy_limit['symbol'],'BUY',buy_limit['status'],buy_limit['orderId'],0,buy_limit['price'],0)
                                    aQuery = "INSERT INTO assets_transactions (symbol,side,status, orderId) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                                    #print('buy query: ', aQuery)
                                    cursor.execute(aQuery, values)
                                except Exception as e:
                                    print('exception inserting to db ', e)
                                    sys.exit()
                            else:
                                #update
                                try:
                                    #update status
                                    aQuery = "UPDATE `assets_transactions` SET `status`='NEW' WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                                    cursor.execute(aQuery)
                                    #commiting to db
                                    DBconnection.commit()
                                except Exception as e:
                                    print('exception updating to db ', e)
                                    sys.exit()
                            #commiting to db
                            DBconnection.commit()
                            #updating recommendation
                            recommendation="buy"
                            #after succcesfull bought status must be changed to bought
                            ref_symbol_status="bought"
                            #after succcesfull sold status must be changed to sold
                            #store to db
                            aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                            cursor.execute(aQuery)
                            #commiting to db
                            DBconnection.commit()
                        except Exception as e:
                            print(e)
                            print("error saving buy order of "+aSymbol+ ' to db')
                            sys.exit()
                    else:
                        #check status of buy order, getting current order
                        try:
                            print('buy query to update: ', buy_query)
                            buy_query_data=buy_query[0]#getting first of tuple
                            ordertoUpdate={}
                            print('order number: ', buy_query_data[4])
                            ordertoUpdate = client.get_order(symbol=aSymbol,orderId=buy_query_data[4])
                            print('currentOrder: ', ordertoUpdate)
                            if ordertoUpdate['status']=='FILLED':
                                aQuery = "UPDATE `assets_transactions` SET `status`='FILLED' WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                                cursor.execute(aQuery)
                                #commiting to db
                                DBconnection.commit()
                        except Exception as e:
                            print('error updating status: ', e)
                            sys.exit()
                        print('still buying '+aSymbol+' yet')
                        recommendation="buy order open"
                            #after succcesfull bought status must be changed to bought
                        ref_symbol_status="buy order open"
                        #after succcesfull sold status must be changed to sold
                        #store to db
                        aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                        cursor.execute(aQuery)
                        #commiting to db
                        DBconnection.commit()
                #getting current time
                #print("I recommend you to ",recommendation)
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



