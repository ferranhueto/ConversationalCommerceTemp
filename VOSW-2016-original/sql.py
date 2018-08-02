import sqlite3

with sqlite3.connect("Activities.db") as connection:
    c = connection.cursor()
    #c.execute('ALTER TABLE u43531899 ADD COLUMN action')
    #c.execute('INSERT INTO posts VALUES("Well","I\'m well.")')
