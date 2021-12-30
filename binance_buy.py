#30.12.2021 setting all sell order operations here.
import os, sys, time

#main sell operation

def buyOperation(aSymbol, cursor, symbol_price, client, ref_symbol_price, DBconnection):
    print('going to buy ', aSymbol)
    #query to know if there is an order
    buy_query=[]
    buy_query_filled=[]
    try:
        aQuery=''
        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='NEW'")
        cursor.execute(aQuery)
        buy_query = cursor.fetchall()
        print('buy_query from assets_transactions', buy_query)
    except Exception as e:
        print('no new buy order')
    try:
        aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='FILLED'")
        cursor.execute(aQuery)
        buy_query_filled = cursor.fetchall()
        print('buy_query from assets_transactions', buy_query_filled)
    except Exception as e:
        print('no filled buy order')
    #we proceed to get last amount of money sold, so we 
    if len(buy_query)==0:#no new buy order
        print('no purchase order, then we go to buy')
        #getting the last sold price
        cummulativeQuoteQty=[]
        cummulativeQuantity=0
        try:
            aQuery = ("SELECT `cummulativeQuoteQty` FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'")
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
        #checking cumulativeQuantity
        if cummulativeQuantity==0:
            cummulativeQuantity=20

        #increasing the trading price for a symbol******************
        #granting we can purchase more of one specific coin
        if "XRPUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "SHIBUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "STXUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "DOGEUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "VETUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "SANDUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "MBLUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "KLAYUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "HBARUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "BTTUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "CHZUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        elif "TRXUSDT" in aSymbol and cummulativeQuantity < 100:
            print('increasing '+aSymbol+' purchase amount to 100')
            cummulativeQuantity=100
        

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
            recommendation="buy"
            ref_symbol_status="bought"
            #OJO **************** I should update purchase here, and not later, only if purchase open
        except Exception as e:
            print(e)
            print("error buying ", aSymbol)
            return 
        #if we buy, then we can store to db
        try:
            #if no currently registered order, then we create the first record
            if len(buy_query)==0 and len(buy_query_filled)==0:
                try:
                    #print('inserting value:' , buy_limit['symbol'],'BUY',buy_limit['status'],buy_limit['orderId'])
                    values = (buy_limit['symbol'],'BUY',buy_limit['status'],buy_limit['orderId'],coins_quantity,buy_limit['price'],buy_limit['cummulativeQuoteQty'])
                    aQuery = "INSERT INTO assets_transactions (symbol,side,status, orderId,executedQty,price,cummulativeQuoteQty) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                    #print('buy query: ', aQuery)
                    cursor.execute(aQuery, values)
                except Exception as e:
                    print('exception inserting to db ', e)
                    sys.exit()
            else:
                #update
                try:
                    #update orderId
                    aQuery = "UPDATE `assets_transactions` SET `orderId`="+'"'+str(buy_limit['orderId'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
                    #update purchased quantity
                    #update orderId
                    aQuery = "UPDATE `assets_transactions` SET `executedQty`="+'"'+str(buy_limit['executedQty'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
                    #update 'cummulativeQuoteQty'
                    if buy_limit['cummulativeQuoteQty']==0:
                        cummulativeQuoteQty=coins_quantity*ref_symbol_price
                    aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+str(buy_limit['cummulativeQuoteQty'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
                    #if buy_limit status is filled, update to fill
                    if 'FILLED' in buy_limit['status']:
                        print('updating status of assets_transactions and  ref_price')
                        #update orderId
                        aQuery = "UPDATE `assets_transactions` SET `status`='FILLED' WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                        cursor.execute(aQuery)
                        DBconnection.commit()
                        #updating ref price with status bought 
                        #updating recommendation
                        recommendation="buy"
                        #after succcesfull bought status must be changed to bought
                        ref_symbol_status="bought"
                        #after succcesfull sold status must be changed to sold
                        #store to db
                        aQuery = "UPDATE `ref_price` SET `status`='bought' WHERE `symbol`="+'"'+aSymbol+'"'
                        cursor.execute(aQuery)
                        #commiting to db
                        DBconnection.commit()
                    else:
                            #update status
                        aQuery = "UPDATE `assets_transactions` SET `status`='NEW' WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'"
                        cursor.execute(aQuery)
                        #commiting to db
                        DBconnection.commit()
                        #updating recommendation
                        recommendation="buy order open"
                        #after succcesfull bought status must be changed to bought
                        ref_symbol_status="buy order open"
                        #after succcesfull sold status must be changed to sold
                        #store to db
                        aQuery = "UPDATE `ref_price` SET `status`="+'"'+ref_symbol_status+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'
                        cursor.execute(aQuery)
                        #commiting to db
                        DBconnection.commit()
                except Exception as e:
                    print('exception updating to db ', e)
                    sys.exit()
            #commiting to db
            DBconnection.commit()
            
        except Exception as e:
            print(e)
            print("error saving buy order of "+aSymbol+ ' to db')
            sys.exit()
    else:
        #then there is an open order, and we have to check order status

        try:
            #print('buy query to update: ', buy_query)
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
        aQuery = "UPDATE `ref_price` SET `status`='buy order open' WHERE `symbol`="+'"'+aSymbol+'"'
        cursor.execute(aQuery)
        #commiting to db
        DBconnection.commit()
