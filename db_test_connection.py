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


DBconnection =None
try:
    DBconnection = mysql.connector.connect(
        host='46.101.173.164',#dbcredentials["DBHOST"], 
        user='ismelql',#dbcredentials["DBUSER"], 
        passwd='olgaMRG49*',#dbcredentials["DBPASSWORD"], 
        port = 8888,
        database='binance_api'#dbcredentials["DBNAME"]
    )
    # print("Connection to MySQL DB successful")
except Exception as e:
    print(f"The error '{e}' occurred")
    DBconnection = False

if DBconnection == False:
    print("db server not available, leaving the system")
    sys.exit()
print('connexion created')
