import os, sys, time
import mysql.connector
import keyboard

from binance.client import Client
import datetime

from mysql_generic_script import (
    create_connection,
    execute_user_query,
    insert_into_table,
)

# here we calculate and update to average and standard deviation of every currency in table,
#as well as we update the reference price
from datetime import datetime, timedelta
    

#conencting to the database

#creating connection to db
DBconnection = create_connection("localhost", "luisramos", "Lr12610418", "binance_api")
cursor = DBconnection.cursor()
if DBconnection == False:
    print("db server not available, leaving the system")
    sys.exit()
print('connexion created')
#checking date to update
results_query = ""
aQuery =""
aQuery = ("SELECT `updated` FROM `ref_price` limit 1")
last_updated=execute_user_query(connection=DBconnection, aQuery=aQuery)
last_update_list=last_updated[0]

#current date 
print('last_update_list: ', last_update_list[0])
#testing if must be updated
if (last_update_list[0]-datetime.today())<timedelta(days=1):
    print("no one day difference to update yet")
    sys.exit()
print('proceeding to update ')
#first we get current date, and move 7 days back
ref_day = datetime.today() - timedelta(days=7)
print("ref day: ",ref_day)
#obtaining symbols from db
results_query = ""
aQuery =""
aQuery = ("SELECT * FROM `assets_symbols`")
results_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
#closing initial connection
#closing db connection
DBconnection.commit()
cursor.close()
DBconnection.close()
#iterate over dictionary to get names and symbols
symbol_list=[]
for an_asset in results_query:
    symbol_list.append(an_asset[2])
#list of symbols
#print('symbol_list: ', symbol_list)
#iterate over symbols and make query per symbol
for aSymbol in symbol_list:
    #creating connection to db
    try:
        DBconnection = create_connection("localhost", "luisramos", "Lr12610418", "binance_api")
        cursor = DBconnection.cursor()
        #reading
        aQuery =""
        aQuery = ("SELECT AVG (price) FROM `assets_historical` WHERE `symbol`= "+'"'+aSymbol+'"'+" AND `datetime` > "+'"'+str(ref_day)+'"')
        average_price = 0
        cursor.execute(aQuery)
        average_price = cursor.fetchall()
        average_price_2 = average_price[0]
        if average_price_2[0] is not None: 
            print("average_price of "+aSymbol+" :",average_price_2[0])
            aQuery =""
            aQuery = ("SELECT FORMAT(STD(`price`),8) FROM `assets_historical` WHERE `symbol`= "+'"'+aSymbol+'"'+" AND `datetime` > "+'"'+str(ref_day)+'"')
            desviation_price = 0
            cursor.execute(aQuery)
            desviation_price = cursor.fetchall()
            desviation_price_2 = desviation_price[0]
            print("desviation_price of "+aSymbol+" :",desviation_price_2[0])
            #writing
            #query update price
            aQuery = "UPDATE `ref_price` SET `price`= %s WHERE `symbol`="+'"'+aSymbol+'"'
            cursor.execute(aQuery,(average_price_2))
            #query update sd
            #query
            aQuery = "UPDATE `ref_price` SET `desviation`= %s WHERE `symbol`="+'"'+aSymbol+'"'
            cursor.execute(aQuery,(desviation_price_2))
            #update date
            #query
            aQuery = "UPDATE `ref_price` SET `updated`= %s WHERE `symbol`="+'"'+aSymbol+'"'
            cursor.execute(aQuery,(datetime.today()))
        else:
            print("average_price of "+aSymbol+" non available")
        #closing db connection
        DBconnection.commit()
        cursor.close()
        DBconnection.close()

    except Error as e:
        # fatal error
        average_price=0
        desviation_price=0
        print(f"The error '{e}' occurred")

    



