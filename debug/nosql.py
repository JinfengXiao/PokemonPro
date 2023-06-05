import mysql.connector as mysql
from pymongo import MongoClient

# natural language query, taken from user input
# mongo_query = "I want pokemon with a flower on its back"
mongo_query = "I want pokemon with wings and is of the fire type"

# MySQL connection
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'pokemasters'
MYSQL_DB = 'pokemasters'
mysql_connection = mysql.connect(
	host = MYSQL_HOST,
	user = MYSQL_USER,
	password = MYSQL_PASSWORD,
	database = MYSQL_DB)
cursor = mysql_connection.cursor(dictionary=True)
cursor.execute("USE pokemasters")

# MongoDB connection
mongo_client = MongoClient()
mongo_db = mongo_client.pokemasters
mongo_collection = mongo_db.desc

# Execute MongoDB query
mongo_results = mongo_collection.find({"$text": {"$search":mongo_query}}, {"score": {"$meta": "textScore"}}).sort( [("score", {"$meta": "textScore"})]).limit(3)
print(mongo_results.count())
sql_results = []
for mongo_result in mongo_results:
    pokemon_id = mongo_result['_id']
    sql_query = "SELECT id, name FROM pokemon WHERE id = {}".format(pokemon_id)
    cursor.execute(sql_query)
    sql_result = cursor.fetchall()[0]
    sql_result["description"] = mongo_result["description"]
    sql_results.append(sql_result) # a list of dict
print(sql_results)

