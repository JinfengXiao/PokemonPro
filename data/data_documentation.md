# Data Documentation

This file documents the raw data, MySQL database schema, and the database construction process.

## Data Files

- `pokemasters.sql`: The complete SQL database for this project. It contains a database `pokemasters` with the following schema:
  - pokemon(<u>id</u>, name, generation_id, evolves_from_species_id, evolution_chain_id, color, height, weight, shape_id, habitat, capture_rate, is_baby)
  - pokemon_shape_prose(<u>id</u>, name, awesome_name, description)
  - pokemon_species_names(<u>id</u>, pokemon_species_id, local_language, name, genus)
  - pokemon_types(<u>id</u>, pokemon_id, type_id, slot)
  - type_efficacy(<u>id</u>, damage_type_id, target_type_id, damage_factor)
  - types(<u>id</u>, identifier, generation_id, damage_class)
- In the above relations, `pokemon`, `pokemon_shape_prose`, `pokemon_species_names` and `types` are **entity sets**, while `pokemon_types` and `type_efficacy` are **relationship sets**. *When drawing ER diagrams, you may ignore the id attribute of relationship sets.*
- Foreign keys:
  - pokemon_species_names.pokemon_species_id → pokemon.id
  - pokemon_types.pokemon_id → pokemon.id
  - pokemon_types.type_id → types.id
  - type_efficacy.damage_type_id → types.id
  - type_efficacy.target_type_id → types.id
- `toy_db.sql `: A toy SQL database for front-end development. It contains a database `pokemasters` with only one table pokemon_species(<u>id</u>, identifier, generation_id, evolves_from_species_id, evolution_chain_id, color_id, shape_id, habitat_id, gender_rate, capture_rate, base_happiness, is_baby, hatch_counter, has_gender_differences, growth_rate_id, forms_switchable).
- `csv/`: The directory of raw csv data downloaded from https://github.com/veekun/pokedex/tree/master/pokedex/data/csv. The raw data file `pokemon.csv` is renamed into `pokemon_height_weight.csv`.

## Steps for MySQL DB Construction

This section documents the steps going from the raw data to the final dababase (DB).

First, start MySQL by navigating to the project directory and typing:

```bash
mysql --local-infile=1 -u root -ppokemasters
```

Then in MySQL, do:

```mysql
CREATE DATABASE pokemasters;
USE pokemasters;
SET GLOBAL local_infile = 'ON';

CREATE TABLE move_damage_classes(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255)
);
LOAD DATA LOCAL INFILE './data/csv/move_damage_classes.csv'
INTO TABLE move_damage_classes
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier);

CREATE TABLE pokemon_colors(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_colors.csv'
INTO TABLE pokemon_colors
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier);

CREATE TABLE pokemon_habitats(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_habitats.csv'
INTO TABLE pokemon_habitats
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier);

CREATE TABLE languages(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255)
);
LOAD DATA LOCAL INFILE './data/csv/languages.csv'
INTO TABLE languages
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, @dummy, @dummy, identifier, @dummy, @dummy);

CREATE TABLE pokemon_shape_prose(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pokemon_shape_id INT,
  local_language_id INT,
  name VARCHAR(255),
  awesome_name VARCHAR(255),
  description VARCHAR(255)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_shape_prose.csv'
INTO TABLE pokemon_shape_prose
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(pokemon_shape_id, local_language_id, name, awesome_name, description);
DELETE FROM pokemon_shape_prose WHERE local_language_id <> 9;
ALTER TABLE pokemon_shape_prose DROP local_language_id,
                                DROP PRIMARY KEY,
                                DROP id,
                                CHANGE pokemon_shape_id id INT,
                                ADD PRIMARY KEY (id);

CREATE TABLE types_tmp(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255),
  generation_id INT,
  damage_class_id INT,
  FOREIGN KEY (damage_class_id) REFERENCES move_damage_classes(id)
);
LOAD DATA LOCAL INFILE './data/csv/types.csv'
INTO TABLE types_tmp
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier, generation_id, @damage_class_id)
SET damage_class_id = IF(@damage_class_id = '', NULL, @damage_class_id);

-- Remove redundancy
CREATE TABLE types AS
(SELECT types_tmp.id AS id, types_tmp.identifier AS identifier, generation_id, move_damage_classes.identifier AS damage_class FROM
 (types_tmp LEFT JOIN move_damage_classes
   ON types_tmp.damage_class_id = move_damage_classes.id)
);
ALTER TABLE types ADD PRIMARY KEY (id);
DROP TABLE types_tmp, move_damage_classes;

CREATE TABLE type_efficacy(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  damage_type_id INT,
  target_type_id INT,
  damage_factor INT,
  FOREIGN KEY (damage_type_id) REFERENCES types(id),
  FOREIGN KEY (target_type_id) REFERENCES types(id)
);
LOAD DATA LOCAL INFILE './data/csv/type_efficacy.csv'
INTO TABLE type_efficacy
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(damage_type_id, target_type_id, damage_factor);

CREATE TABLE pokemon_species(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255),
  generation_id INT,
  evolves_from_species_id INT,
  evolution_chain_id INT,
  color_id INT,
  shape_id INT,
  habitat_id INT,
  capture_rate INT,
  is_baby INT,
  FOREIGN KEY (color_id) REFERENCES pokemon_colors(id),
  FOREIGN KEY (shape_id) REFERENCES pokemon_shape_prose(id),
  FOREIGN KEY (habitat_id) REFERENCES pokemon_habitats(id)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_species.csv'
INTO TABLE pokemon_species
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier, generation_id, @evolves_from_species_id, @evolution_chain_id, @color_id, @shape_id, @habitat_id, @dummy, @capture_rate, @dummy, @is_baby, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy)
SET evolves_from_species_id = IF(@evolves_from_species_id = '', NULL, @evolves_from_species_id),
    evolution_chain_id = IF(@evolution_chain_id = '', NULL, @evolution_chain_id),
    color_id = IF(@color_id = '', NULL, @color_id),
    shape_id = IF(@shape_id = '', NULL, @shape_id),
    habitat_id = IF(@habitat_id = '', NULL, @habitat_id),
    capture_rate = IF(@capture_rate = '', NULL, @capture_rate),
    is_baby = IF(@is_baby = '', NULL, @is_baby);

CREATE TABLE pokemon_height_weight(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  identifier VARCHAR(255),
  species_id INT, -- This WILL have duplicates from mega pokemon
  height INT,
  weight INT,
  FOREIGN KEY (species_id) REFERENCES pokemon_species(id)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_height_weight.csv'
INTO TABLE pokemon_height_weight
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, identifier, species_id, height, weight, @dummy, @dummy, @dummy);

-- Now, combine multiple redundant tables into one big table "pokemon"
CREATE TABLE pokemon AS
(SELECT pokemon_species.id AS id, pokemon_species.identifier AS name, generation_id, evolves_from_species_id, evolution_chain_id, pokemon_colors.identifier AS color, height, weight, shape_id, pokemon_habitats.identifier AS habitat, capture_rate, is_baby FROM
 (pokemon_species LEFT JOIN pokemon_height_weight
   ON pokemon_species.id = pokemon_height_weight.species_id 
      AND pokemon_species.identifier = pokemon_height_weight.identifier
 LEFT JOIN pokemon_colors
   ON pokemon_species.color_id = pokemon_colors.id
 LEFT JOIN pokemon_habitats
   ON pokemon_species.habitat_id = pokemon_habitats.id)
);
ALTER TABLE pokemon ADD PRIMARY KEY (id);
-- Drop redundant tables
DROP TABLE pokemon_height_weight, pokemon_species, pokemon_colors, pokemon_habitats;

-- Continue to create tables
CREATE TABLE pokemon_species_names_tmp(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pokemon_species_id INT,
  local_language_id INT,
  name VARCHAR(255),
  genus VARCHAR(255),
  FOREIGN KEY (pokemon_species_id) REFERENCES pokemon(id),
  FOREIGN KEY (local_language_id) REFERENCES languages(id)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_species_names.csv'
INTO TABLE pokemon_species_names_tmp
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(pokemon_species_id, local_language_id, name, genus);

-- Again, remove redundancy
CREATE TABLE pokemon_species_names AS
(SELECT pokemon_species_names_tmp.id AS id, pokemon_species_id, languages.identifier AS local_language, name, genus FROM
 (pokemon_species_names_tmp LEFT JOIN languages
   ON pokemon_species_names_tmp.local_language_id = languages.id)
);
ALTER TABLE pokemon_species_names ADD PRIMARY KEY (id);
-- Drop redundant tables
DROP TABLE pokemon_species_names_tmp, languages;

-- Continue to create tables
CREATE TABLE pokemon_types(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pokemon_id INT,
  type_id INT,
  slot INT,
  FOREIGN KEY (pokemon_id) REFERENCES pokemon(id),
  FOREIGN KEY (type_id) REFERENCES types(id)
);
LOAD DATA LOCAL INFILE './data/csv/pokemon_types.csv'
INTO TABLE pokemon_types
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(pokemon_id, type_id, slot); -- 272 warnings due to pokemon_id overflow are expected
```

After the above code is executed, the database now has the schema of `pokemasters.sql` described ealier in this document.

Finally, the results are saved to a `.sql` file.

```bash
mysqldump -u root -ppokemasters pokemasters > ./data/pokemasters.sql
```
