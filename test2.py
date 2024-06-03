from pymongo.mongo_client import MongoClient
import sqlite3

mango = MongoClient('mongodb+srv://tunwit:tunwit3690@littlebirdd.tvaiyir.mongodb.net/?retryWrites=true&w=majority')
connection = sqlite3.connect('bot/data/bot_data.db')

database = mango["Main"]
collact = database['searchstatistic2']
cursor = connection.cursor()
i = 0
for data in collact.find():
    i+=1
    source = cursor.execute("INSERT INTO search_history (music,times) VALUES (?,?)",(data['music'].replace("$^", "."),data['times'],))
print(i)
connection.commit()
cursor.close()
