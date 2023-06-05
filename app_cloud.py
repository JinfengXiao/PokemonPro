from flask import Flask, render_template, request, redirect, url_for
import mysql.connector as mysql
from pymongo import MongoClient
import sys

app = Flask(__name__)

#config
app.config['MYSQL_HOST'] = 'your_web_host'
app.config['MYSQL_USER'] = 'your_web_user'
app.config['MYSQL_PASSWORD'] = 'your_web_password'
app.config['MYSQL_DB'] = 'your_web_db'
app.config['MONGO_URL'] = 'your_web_url'

@app.route('/') #Description and maybe images about Pokemon and its logistics. Link create, find, and battle pages (Due now)
def home():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def get_result():

    #init MySQL connection. This cannot be simplified into a function
    connection = mysql.connect(
        host = app.config['MYSQL_HOST'],
        user = app.config['MYSQL_USER'],
        password = app.config['MYSQL_PASSWORD'],
        database = app.config['MYSQL_DB'])
    connection.reconnect(attempts=3, delay=3)
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("USE " + app.config['MYSQL_DB'])

    try:
        sql_query = request.form['sql_query']
        cursor.execute(sql_query)
        if 'SELECT' in sql_query:
            result = cursor.fetchall() # a list of dict
            return render_template('result.html', result=result)
        elif sql_query == '':
            return render_template('result.html', result=[])
        else:
            return render_template('feedback.html')
        cursor.close()
    except:
        is_mongo_query = True

    try:
        mongo_query = request.form['nlp_query']
    except:
        is_mongo_query = False
    try:
        # MongoDB connection
        mongo_client = MongoClient(app.config['MONGO_URL'])
    except AutoReconnect:
        pass
    if is_mongo_query:
        mongo_db = mongo_client.heroku_x57gtflc  # heroku_x57gtflc is the database name
        mongo_collection = mongo_db.descriptions  # "descriptions" is the collection name
        
        # Execute MongoDB query
        mongo_results = mongo_collection.find({"$text": {"$search":mongo_query}}, {"score": {"$meta": "textScore"}}).sort( [("score", {"$meta": "textScore"})]).limit(3)
        sql_results = []
        for mongo_result in mongo_results:
            pokemon_id = mongo_result['_id']
            sql_query = "SELECT id, name FROM pokemon WHERE id = {}".format(pokemon_id)
            cursor.execute(sql_query)
            sql_result = cursor.fetchall()[0]
            sql_result["description"] = mongo_result["description"]
            sql_results.append(sql_result) # a list of dict
        return render_template('result.html', result=sql_results)
    
    return render_template('result.html', result=[])


@app.route('/create.html', methods=['POST', 'GET']) #Give players the ability to create Pokemon so that they can test out how their Pokemon will do against theoretical ones (Due now)
def create():
    if request.method == "POST":

        #init MySQL connection. This cannot be simplified into a function
        connection = mysql.connect(
            host = app.config['MYSQL_HOST'],
            user = app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB'])
        connection.reconnect(attempts=3, delay=3)
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("USE " + app.config['MYSQL_DB'])

        name = request.form["pokemon_name"]
        type1 = request.form["type1"]
        type2 = request.form["type2"]
        weight = request.form["weight"]
        height = request.form["height"]
        color = request.form["color"]
        habitat = request.form["habitat"]
        capture_rt = request.form["capture"]
        type_dict = {
            "normal": 1,
            "fighting" : 2,
            "flying": 3,
            "poison" : 4,
            "ground" : 5,
            "rock" : 6,
            "bug" : 7,
            "ghost" : 8,
            "steel" : 9,
            "fire" : 10,
            "water" : 11,
            "grass" : 12,
            "electric" : 13,
            "physchic" : 14,
            "ice" : 15,
            "dragon": 16,
            "dark" : 17,
            "fairy" : 18,
            "unknown" : 1001,
            "shadow" : 1002
        }
        cursor.execute(
            """
            INSERT INTO pokemon (id, name, generation_id, color, height, weight, habitat, capture_rate, is_baby) 
            SELECT count(*)+1, '""" + name + """', 8, '""" + color + """', '""" + str(height) + """', 
            '""" + str(weight) + """', '""" + habitat + """', '""" + str(capture_rt) + """', 0 from pokemon
            """
        )
        cursor.execute(
            """
            INSERT INTO pokemon_types (pokemon_id, type_id, slot) SELECT count(*), '""" + str(type_dict[type1]) + """', 1 from pokemon
                    """
        )
        if type2 != "":
            cursor.execute("""
                        INSERT INTO pokemon_types (pokemon_id, type_id, slot) SELECT count(*), '""" + str(type_dict[type2]) + """', 1 from pokemon
                                """
                           )
        return redirect(url_for('home'))

    return render_template("create.html")


@app.route('/find.html') #Natural language processor that will return a pokemon based on users input (Due next stage)
def find():
    return render_template("find.html")

@app.route('/simple_search', methods=['POST','GET']) #search types for pokemon
def simple_search():
    if request.method == 'POST':

        #init MySQL connection. This cannot be simplified into a function
        connection = mysql.connect(
            host = app.config['MYSQL_HOST'],
            user = app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB'])
        connection.reconnect(attempts=3, delay=3)
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("USE " + app.config['MYSQL_DB'])

        name = request.form["name"]
        cursor.execute(
            """SELECT types.identifier as type, pokemon.height, pokemon.weight, pokemon.color, pokemon.capture_rate, pokemon.habitat
            FROM pokemon JOIN pokemon_types ON pokemon.id = pokemon_types.pokemon_id 
            JOIN types ON pokemon_types.type_id = types.id WHERE pokemon.name = '"""+name+"""';"""
        )
        result = cursor.fetchall()
        return render_template("simple_search.html", result = result)
    else:
        return render_template("find.html")

@app.route('/search_by_type', methods=['POST','GET'])#search pokemons by types
def search_by_type():
    if request.method == 'POST':

        #init MySQL connection. This cannot be simplified into a function
        connection = mysql.connect(
            host = app.config['MYSQL_HOST'],
            user = app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB'])
        connection.reconnect(attempts=3, delay=3)
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("USE " + app.config['MYSQL_DB'])

        type1 = request.form["type1"]
        type2 = request.form["type2"]
        cursor.execute(
            """SELECT q1.name from
            (SELECT pokemon.name FROM pokemon JOIN pokemon_types ON pokemon.id = pokemon_types.pokemon_id
            JOIN types ON pokemon_types.type_id = types.id WHERE types.identifier = '"""+type1+"""' ORDER BY pokemon.id) AS q1
            INNER JOIN (SELECT pokemon.name FROM pokemon
            JOIN pokemon_types ON pokemon.id = pokemon_types.pokemon_id
            JOIN types ON pokemon_types.type_id = types.id WHERE types.identifier = '"""+type2+"""' ORDER BY pokemon.id) AS q2 
            ON q1.name = q2.name;
            """
        )
        result_name = cursor.fetchall()
        return render_template("simple_search.html", result_name = result_name)
    else:
        return render_template("find.html")

@app.route('/type_efficacy', methods=['POST','GET'])#input a type, get info of stronger types and weaker types
def type_efficacy():
    if request.method == 'POST':

        #init MySQL connection. This cannot be simplified into a function
        connection = mysql.connect(
            host = app.config['MYSQL_HOST'],
            user = app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB'])
        connection.reconnect(attempts=3, delay=3)
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("USE " + app.config['MYSQL_DB'])

        types = request.form["type"]
        iterator = cursor.execute(
            """
            SELECT identifier, COUNT(*) AS num_stronger_type FROM types JOIN type_efficacy 
            ON types.id = type_efficacy.damage_type_id WHERE damage_factor > 100
            and identifier = '"""+types+"""'  GROUP BY damage_type_id;
            SELECT identifier, COUNT(*) AS num_weaker_type FROM types JOIN type_efficacy 
            ON types.id = type_efficacy.damage_type_id WHERE damage_factor < 100
            and identifier = '"""+types+"""'  GROUP BY damage_type_id;
            SELECT typesII.identifier FROM types JOIN type_efficacy ON types.id = type_efficacy.damage_type_id
            JOIN types AS typesII ON type_efficacy.target_type_id = typesII.id WHERE damage_factor > 100 
            and types.identifier = '"""+types+"""' ORDER BY typesII.id;
            SELECT typesII.identifier FROM types JOIN type_efficacy ON types.id = type_efficacy.damage_type_id
            JOIN types AS typesII ON type_efficacy.target_type_id = typesII.id WHERE damage_factor < 100 
            and types.identifier = '"""+types+"""' ORDER BY typesII.id;
            """, multi = True
        )
        type_strong = next(iterator).fetchall()
        type_weak = next(iterator).fetchall()
        stronger_types = next(iterator).fetchall()
        weaker_types = next(iterator).fetchall()
        return render_template("types_search.html", type_strong = type_strong, type_weak = type_weak, types = types
        , stronger_types = stronger_types, weaker_types = weaker_types)
    else:
        return render_template("find.html")


@app.route('/back_home', methods=['GET'])
def back_home():
    return render_template("home.html")

@app.route('/battle.html') #new
def battle_new():
    return render_template("battle.html")

if __name__ == '__main__':
    app.run()