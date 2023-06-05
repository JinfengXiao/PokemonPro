import mysql.connector as mysql

#init MySQL connection
connection = mysql.connect(
	host = 'localhost',
	user = 'root',
	password = 'pokemasters',
	database = 'pokemasters')
cursor = connection.cursor(dictionary=True)

cursor.execute("USE pokemasters")
result = cursor.execute("SELECT * FROM types")
result_fetched = cursor.fetchall()
if len(result_fetched) > 0:
    for row in result_fetched:
        for key, value in row.items():
            print(key, value)
cursor.close()

