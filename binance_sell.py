#30.12.2021 setting all sell order operations here.
import os, sys, time

#main sell operation

def sellOperation(aSymbol, cursor, symbol_price, client, ref_symbol_price, DBconnection, recommendation):
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
        print('no purchase or sell order new 12.12.2021')
        #we have to check if there is a "buy order open" in ref_price table, then break
        try:
            aQuery = ("SELECT * FROM `ref_price` WHERE `symbol`="+'"'+aSymbol+'"'+" and `status`='buy order open'")
            cursor.execute(aQuery)
            current_status = cursor.fetchall()
            #if buy order open, then we must break and return
            if current_status:
                print("there is a buy order open, we must not sell anything? ",current_status)
                recommendation="do nothing"
                return recommendation
        except Exception as e:
            print('no buy order open')
        cummulativeQuoteQty=[]
        cummulativeQuantity=0
        this_symbol_price=""
        executedQuantity=[]
        last_buy_executed_Quantity=0
        try:
            aQuery = ("SELECT `cummulativeQuoteQty` FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='FILLED'")
            cursor.execute(aQuery)
            cummulativeQuoteQty = cursor.fetchall()
        except Exception as e:
            print('not sold order filled, update status and return')
            recommendation="do nothing"
            return recommendation
        if len(cummulativeQuoteQty)==0:#if there is not value or record
            print('no filled sold order for ',aSymbol)
            cummulativeQuantity=20#assigning a value
        else:  
            cummulativeQuantity1=cummulativeQuoteQty[0]
            cummulativeQuantity=cummulativeQuantity1[0]
        #getting executedQuantity
        try:
            aQuery = ("SELECT `executedQty` FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY'")
            cursor.execute(aQuery)
            executedQty = cursor.fetchall()
        except Exception as e:
            print('not excutedQty gotten')
            executedQty=[]
            sys.exit()
        if len(executedQty)==0:#if there is not value or record
            print('no executedQty for ',aSymbol)
            last_buy_executed_Quantity=0#assigning a value
        else:  
            last_buy_executed_Quantity1=executedQty[0]
            last_buy_executed_Quantity=last_buy_executed_Quantity1[0]
                   
        #increasing the trading price for a symbol******************
        #granting we can purchase more of one specific coin
        if "CELRUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "ONEUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "COTIUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "ALGOUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "COCOSUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "TRIBEUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "CTSIUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "XLMUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "FETUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "HARDUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "SHIBUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20
        elif "CTXCUSDT" in aSymbol and cummulativeQuantity < 20:
            print('increasing '+aSymbol+' sell amount to 20')
            cummulativeQuantity=20

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
            #coins_quantity must be less or equal to the last buy quantity
        coins_quantity_1=cummulativeQuantity/current_symbol_price
        coins_quantity=round(coins_quantity_1,0)#to avoid insuficiente funds
        #I should not sell more than what I purchased
        if  coins_quantity > last_buy_executed_Quantity  and last_buy_executed_Quantity !=0:
            coins_quantity=last_buy_executed_Quantity
            print('selling last purchase quantity, and not the calculated')
            print('selling '+str(coins_quantity)+ 'of '+aSymbol)
        #price
        #trying to get first 9 characters of price
        current_str_symbol_price=symbol_price["price"]
        print('current_str_symbol_price: ', current_str_symbol_price)
        current_symbol_price=float(current_str_symbol_price)
        order=None
        try:
            order = client.order_limit_sell(symbol=aSymbol,quantity=coins_quantity,price=this_symbol_price)
            print('sell order: ', order)
            #we have to include the update function here 02.12.2021
            if order['status']=='FILLED':
                print('order filled update')
                
            elif order['status']=='NEW':
                print('order new update')


        except Exception as e:
            if 'APIError(code=-2010)' in str(e):
                try:
                    coins_quantity2=coins_quantity-(coins_quantity*0.1)
                    order = client.order_limit_sell(symbol=aSymbol,quantity=coins_quantity2,price=this_symbol_price)
                    recommendation="sell"
                    ref_symbol_status="sold"
                    print('sell order 2: ', order)
                    ##OJO update order here  
                except Exception as e:
                    print(e)
                    print('exception when selling insuficient funds ', aSymbol)
                    #if insuficient funds, purchase with less******
                    recommendation="do nothing"
                    return recommendation
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
            ##should not be "and status="filled""???
            aQuery = ("SELECT * FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='FILLED'")
            cursor.execute(aQuery)
            sell_filled_query = cursor.fetchall()
            print('sell_filled_query: ', sell_filled_query)
        except:
            print('not filled sell order')
        if len(sell_filled_query)!=0:
            print('updating selling order of ',aSymbol)
            recommendation="sell"
            ref_symbol_status="sold"
            #updating
            #update status
            query_tuple=sell_filled_query[0]
            print('assets_transactions current query tuple in db: ', query_tuple)
            try:
                print('UPDATE `assets_transactions` SET `cummulativeQuoteQty` ')
                if order['cummulativeQuoteQty']==0:
                    cummulativeQuoteQty=coins_quantity*ref_symbol_price
                    print('order[cummulativeQuoteQty]: ', order['cummulativeQuoteQty'])
                    aQuery = "UPDATE `assets_transactions` SET `cummulativeQuoteQty`="+'"'+str(order['cummulativeQuoteQty'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'"
                    cursor.execute(aQuery)
                    #commiting to db
                    DBconnection.commit()
            except Exception as e:#correction on 01.08
                print(e)
                print("error inserting cummulativeQuoteQty to db")
                sys.exit()
            try:    
                print("UPDATE `assets_transactions` SET `status`=")
                print("order['status']: ", order['status'])
                aQuery = "UPDATE `assets_transactions` SET `status`="+'"'+order['status']+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'"
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
                aQuery = "UPDATE `assets_transactions` SET `orderId`="+'"'+str(order['orderId'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'"
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
                aQuery = "UPDATE `assets_transactions` SET `price`="+'"'+str(order['price'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'"
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
            except Exception as e:#correction on 01.08
                print(e)
                print("error inserting price to db")
                sys.exit()
            print('updating '+aSymbol+ 'in ref_price  with ' +ref_symbol_status)
            try:    
                print("UPDATE `assets_transactions` SET `executedQty`=")
                aQuery = "UPDATE `assets_transactions` SET `executedQty`="+'"'+str(order['executedQty'])+'"'+" WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL'"
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
                aQuery = "UPDATE `ref_price` SET `status`='sold' WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
            except Exception as e:
                print(e)
                print("error updating sell status in `ref_price` ")
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
            except Exception as e:
                print(e)
                print("error inserting sell order INTO assets_transactions")
                sys.exit()
            print('updating '+aSymbol+ 'in ref_price  with ' +ref_symbol_status)
            try:
                #store to db
                #query
                aQuery = "UPDATE `ref_price` SET `status`='sold' WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
            except Exception as e:
                print(e)
                print("error updating sell status in `ref_price` ")
                sys.exit()
            try:
                #updating ref price
                print('updating '+aSymbol+ 'in ref_price  again ' +ref_symbol_status)
                #store to db
                #query
                aQuery = "UPDATE `ref_price` SET `status`='sold' WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
            except Exception as e:
                print(e)
                print("error updating sell status in `ref_price` ")
                sys.exit()

    elif len(sell_query)!=0:
        print('there is an open sell order, so I can not sell')
        aQuery=""
        aQuery = ("SELECT *  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='SELL' and `status`='NEW'")
        cursor.execute(aQuery)
        result_query =''
        result_query = cursor.fetchall()
        result_tuple=''
        result_tuple=result_query[0]
        #get order from binance
        print('result_tuple array sell: ', result_tuple)
        print('result_tuple sell: ', result_tuple[4])
        currentOrder={}
        try:
            currentOrder = client.get_order(symbol=aSymbol,orderId=result_tuple[4])
            #12.12.2021
            print("sell currentOrder response: ", currentOrder)
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
                #31.12 we have to update the quantity of coins and return?
                #query
                aQuery = "UPDATE `ref_price` SET `status`='sold' WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
                #return recommendation????
            
        except Exception as e:
            print('error updating sell order: ', e)
            #else set status still selling
            #check if there is an open buy order
    elif len(buy_query)!=0:
        print('there is an open buy order, so I can not sell')
        aQuery=""
        aQuery = ("SELECT `orderId`  FROM `assets_transactions` WHERE `symbol`="+'"'+aSymbol+'"'+" and `side`='BUY' and `status`='NEW'")
        cursor.execute(aQuery)
        result_tuple = cursor.fetchall()
        #get order from binance
        currentOrder={}
        try:
            currentOrder = client.get_order(symbol=aSymbol,orderId=result_tuple[0])
            print("buy currentOrder response: ", currentOrder)
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
                #updateing ref_price
                #query
                aQuery = "UPDATE `ref_price` SET `status`='bought' WHERE `symbol`="+'"'+aSymbol+'"'
                cursor.execute(aQuery)
                #commiting to db
                DBconnection.commit()
        except Exception as e:
            print('error updating open buy order: ',e)
            time.sleep(60)
    return recommendation
                