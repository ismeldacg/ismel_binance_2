import os, sys, time
import keyboard

from binance.client import Client
import datetime

# here we calculate and update to average and standard deviation of every currency in table,
#as well as we update the reference price
from datetime import datetime, timedelta
from mysql_generic_script import (
    create_connection,
    execute_user_query,
    insert_into_table,
)

def updateAvg(DBconnection, cursor):
    #first we get current date, and move 7 days back
    #ref_day = datetime.today() - timedelta(days=7)
    newnow = datetime.today().replace(microsecond=0)  #cambio para evitar los microsegundos en la hora
    ref_day = newnow - timedelta(days=1)
    print("ref day: ",ref_day)
    #obtaining symbols from db
    try:
        results_query = ""
        aQuery =""
        aQuery = ("SELECT * FROM `assets_symbols`")
        results_query=execute_user_query(connection=DBconnection, aQuery=aQuery)
    except Exception as e:
        print("error updating: ", e)
        sys.exit()
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
            #reading
            aQuery =""
            aQuery = ("SELECT AVG (price) FROM `assets_historical` WHERE `symbol`= "+'"'+aSymbol+'"'+" AND `datetime` > "+'"'+str(ref_day)+'"')
            average_price = 0
            cursor.execute(aQuery)
            average_price = cursor.fetchall()
            average_price_2 = average_price[0]
            #print(str(average_price_2)+' average of '+aSymbol)
            if average_price_2[0] is not None: 
                #print("average_price of "+aSymbol+" :",average_price_2[0])
                aQuery =""
                aQuery = ("SELECT FORMAT(STD(`price`),8) FROM `assets_historical` WHERE `symbol`= "+'"'+aSymbol+'"'+" AND `datetime` > "+'"'+str(ref_day)+'"')
                desviation_price = 0
                cursor.execute(aQuery)
                desviation_price = cursor.fetchall()
                desviation_price_2 = desviation_price[0]
                #print("desviation_price of "+aSymbol+" :",desviation_price_2[0])
                #writing
                #query update price
                aQuery = "UPDATE `ref_price` SET `price`= %s WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery,(average_price_2))
                #query update sd
                #query
                aQuery = "UPDATE `ref_price` SET `desviation`= %s WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery,(desviation_price_2))
                #update date
                update_date_time=newnow
                #query
                aQuery = "UPDATE `ref_price` SET `updated`= "+'"'+str(update_date_time)+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)#,(update_date_time))
            else:
                print("average_price of "+aSymbol+" non available")
        except Exception as e:
            # fatal error
            average_price=0
            desviation_price=0
            print(f"The error '{e}' occurred")


def definePerformance(DBconnection, cursor):
    # map the inputs to the function blocks
    options = {0 : 0.1,
            1 : 0.2,
            2 : 0.3,
            3 : 0.4,
            4 : 0.5,
            5 : 0.6,
            6 : 0.7,
            7 : 0.8,
            8: 0.9,
            9: 1.0,
            10:1.1,
            11:1.2,
            12:1.3,
            13:1.4,
            14:1.5,
            15:1.6,
            16:1.7,
            17:1.8,
            18:1.9,
            19:2.0,
    }
    newnow = datetime.today().replace(microsecond=0)  #cambio para evitar los microsegundos en la hora
    ref_day = newnow - timedelta(days=1)#must change to days=1
    #check date for update
    print("ref date for update: ", ref_day)
    try: 
        aQuery =""
        #obtener criterio de rendimiento
        aQuery = ("SELECT `symbol`,COUNT(*) FROM `assets_historical` WHERE  `datetime` > "+'"'+
        str(ref_day)+'"'+
        " and (`recommendation`='sell' or `recommendation`='buy' ) GROUP BY `symbol`")
        desviation_price = 0
        cursor.execute(aQuery)
        performance_tuples = cursor.fetchall()
    except Exception as e:
        print('erro calculating performance: ', e)
    performance_dict = {}
    print("performance_tuples updated: ", performance_tuples)
    try:
        for a_tuple in performance_tuples:
            if a_tuple[1]<20:
                #print(a_tuple[0], a_tuple[1], options[a_tuple[1]])
                performance_dict[a_tuple[0]]=options[a_tuple[1]]
                #query update price
                aQuery = "UPDATE `ref_price` SET `performance`=" +'"'+str(options[a_tuple[1]])+'"'+ "WHERE `symbol`="+'"'+str(a_tuple[0])+'"'
                cursor.execute(aQuery,( a_tuple[1]))
            else:
                performance_dict[a_tuple[0]]=2.0
                #query update price
            #query update price
                aQuery = "UPDATE `ref_price` SET `performance`=" +'"'+str(2.0)+'"'+ "WHERE `symbol`="+'"'+str(a_tuple[0])+'"'
                cursor.execute(aQuery,2.0)
    except Exception as e:
        print('error when updating: ', e)
    #print("performance_tuples: ", performance_dict)


def getRefValues(DBconnection, cursor):
    ref_price = ""
    aQuery =""
    try:
        aQuery = ("SELECT * FROM `ref_price`")
        ref_price_tuples=execute_user_query(connection=DBconnection, aQuery=aQuery)
    except Exception as e:
        print("exception getting ref price")
    ref_price_dict = {}
    print("ref_price_tuples: ", ref_price_tuples)
    for a_tuple in ref_price_tuples:
        ref_price_dict[a_tuple[1]]=a_tuple[2]
    print("ref_price_dict: ", ref_price_dict)
    ref_sd_dict = {}
    for a_tuple in ref_price_tuples:
        ref_sd_dict[a_tuple[1]]=a_tuple[4]
    #getting the performance value
    ref_perf_dict = {}
    print("ref_price_tuples: ", ref_price_tuples)
    for a_tuple in ref_price_tuples:
        ref_perf_dict[a_tuple[1]]=a_tuple[6]
    #retunring all vaues
    return ref_price_dict, ref_sd_dict, ref_perf_dict


#funtion to update string in table, the result is commited in the procedure
def updateDBTable_string(aTable, aColumn, aValue, aSymbol, DBconnection, cursor):
    try:
        aQuery = "UPDATE "+"`"+aTable+"`"+ "SET "+"`"+aColumn+"`"+ "= "+'"'+aValue+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
        cursor.execute(aQuery,(update_date_time))
        DBconnection.commit()
        return True
    except:
        return False

#funtion to update string in table, the result is commited in the procedure
def updateDBTable_number(aTable, aColumn, aValue, aSymbol, DBconnection, cursor):
    try:
        aQuery = "UPDATE "+"`"+aTable+"`"+ "SET "+"`"+aColumn+"`"+ "= %s WHERE `symbol`="+'"'+aSymbol+'"'
        cursor.execute(aQuery,aValue)
        DBconnection.commit()
        return True
    except:
        return False

#funtion to update tables after a filled sell or purchase
def order_Filled_Update(order, aSymbol, side,cursor, DBconnection, ref_symbol_status):
    try:    
        print("UPDATE `assets_transactions` SET `status`=")
        print("order['status']: ", order['status'])
        aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+order['status']+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`="+'"'+side+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
    except Exception as e:#correction on 01.08
        print(e)
        print("error inserting status to db")
        sys.exit()
    #updating 
    try:    
        print("UPDATE `assets_transactions` SET `orderId`=")
        print("order['orderId']: ", order['orderId'])
        aQuery = "UPDATE `assets_transactions` SET `orderId`="+'"'+str(order['orderId'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`="+'"'+side+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
    except Exception as e:#correction on 01.08
        print(e)
        print("error inserting orderId to db")
        sys.exit()
    #updating price
    try:    
        print("UPDATE `assets_transactions` SET `price`=")
        aQuery = "UPDATE `assets_transactions` SET `price`="+'"'+str(order['price'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`="+'"'+side+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
    except Exception as e:#correction on 01.08
        print(e)
        print("error inserting price to db")
        sys.exit()
    print('updating '+aSymbol+ 'in assets_transactions  with ' +order['executedQty'])
    try:    
        print("UPDATE `assets_transactions` SET `executedQty`=")
        aQuery = "UPDATE `assets_transactions` SET `executedQty`="+'"'+str(order['executedQty'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`="+'"'+side+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
    except Exception as e:#correction on 01.08
        print(e)
        print("error inserting price to db")
        sys.exit()
    print('updating '+aSymbol+ 'in ref_price  with ' +ref_symbol_status)
    try:
        #store to db
        #query
        aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
        return
    except Exception as e:
        print(e)
        print("error updating sell status in `ref_price` ")
        sys.exit()




    



