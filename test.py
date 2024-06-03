import sqlite3

connection = sqlite3.connect('bot/data/bot_data.db')
cursor = connection.execute("SELECT * from search_history ")

for row in cursor:
    print(row)