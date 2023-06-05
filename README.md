# Pokemon Pro
This repo contains the source code for a web server about Pokemon. The homepage looks like this:

![interface](./data/images/interface.png)

On this webpage, you can search for a Pokemon, create new Pokemon, or play a Pokemon battle. The web server can be hosted on a local machine. We also provide the code for hosting a cloud server on [Heroku](https://www.heroku.com/).

This was part of my course project for `CS411: Database Systems` in Spring 2020 at the University of Illinois at Urbana-Champaign. My teammates include [Joshua Perks](https://github.com/joshuaPerakis), [David Fernandez-Wang](https://github.com/davidfwww), and [Zixuan Shao](https://github.com/PygMali0n). The code was originally developed in Joshua's private repo, and this is a public release with sensitive data removed. My major contribution to the project is the **full-stack development** of this web application including MySQL & MongoDB database construction, flask & HTML development, cloud deployment, and code documentation. My teammates played major roles in data file collection, webpage layout design, the Pokemon Battler module deployment, and report writing.

## Setting Up Local Server

### Python Environment

With [Conda](https://docs.conda.io/en/latest/), it is very easy to install all the required packages:

```bash
conda env create -f environment.yml
conda activate pokemasters
```

### MySQL Database

Install the [MySQL Community Server](https://dev.mysql.com/downloads/mysql/), and make sure your MySQL user "root" has the password "pokemasters" by following the instructions on [this webpage](https://www.techrepublic.com/article/how-to-set-change-and-recover-a-mysql-root-password/). Then, access the server with:

```bash
mysql --local-infile=1 -u root -ppokemasters
```

In the MySQL terminal, do the following:

```mysql
DROP DATABASE IF EXISTS pokemasters;
CREATE DATABASE pokemasters;
USE pokemasters;
SET GLOBAL local_infile = 'ON';
SOURCE ./data/pokemasters.sql;
```

### MongoDB

Install the [MongoDB Community Edition](https://www.mongodb.com/docs/manual/administration/install-community/) and the [`mongoimport` tool](https://www.mongodb.com/docs/database-tools/mongoimport/). Then, run this shell command under the project directory:

```bash
mongoimport ./data/descriptions.json -d pokemasters -c desc --drop
```

which imports the data in the JSON file into a collection named `desc` in a database `pokemasters` (and it drops the collection if it exists before importing the data). Then, use the `mongosh` shell command to open the MongoDB command line, and enter

```mongosh
db.desc.createIndex({description:"text"})
```

to build a text index. Use `Ctrl C` to go back to the shell and run `python ./debug/nosql.py`  to verify if both SQL DB and MongoDB are set up correctly.

### Starting Local Web Server

Use the command

```bash
python app_local.py
```

to start the local web server and follow the printed link to open the webpage in a browser. Now you are ready to have fun!

## Setting Up Cloud Server

We deployed a Heroko-based cloud server in 2020 and later retired it. To host a cloud server, follow these steps:

- Set up a MySQL DB and MongoDB online.
- Change the `app_cloud.config` values in `app_cloud.py` to access the web databases.
- Run `app_cloud.py` on a cloud server and access the webpage following the instructions from the cloud service provider.

Warning: Users can change the data in the backend DB.

## Sample Queries

You are welcome to play with these queries and whatever you come up with.

### SQL Queries:

```mysql
SELECT * FROM types;
INSERT INTO types (identifier, damage_class) VALUES ('mysterious', 'special');
SELECT * FROM types;
UPDATE types SET damage_class = "physical" WHERE identifier = 'mysterious';
SELECT * FROM types WHERE identifier = 'mysterious';
DELETE FROM types WHERE identifier = 'mysterious';
SELECT * FROM types;

-- Advanced queries
-- Join query: Count the number of pokemon with wings
SELECT COUNT(*) FROM pokemon JOIN pokemon_shape_prose ON shape_id = pokemon_shape_prose.id WHERE pokemon_shape_prose.name = "Wings";
-- GROUP BY query: For each type, output its name, and the number of types that it is strong against. Output in descending order of the number.
SELECT identifier AS type, COUNT(*) AS strong_against FROM types JOIN type_efficacy ON types.id = type_efficacy.damage_type_id WHERE damage_factor > 100 GROUP BY damage_type_id ORDER BY strong_against DESC;
```

### Natural Language Queries:

`I want pokemon with wings and is of the fire type`

`I want a pokemon with a flower on its back`

## More Information

For descriptions of MySQL database schema, data files, and the database construction process, check out `./data/data_documentation.md`.
