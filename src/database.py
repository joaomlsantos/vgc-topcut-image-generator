# filepath: [database.py](http://_vscodecontentref_/0)

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def connect_to_db():
    try:
        # Get connection parameters from environment variables
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Connection to database established successfully.")
        return connection
    except Exception as error:
        print(f"Error connecting to database: {error}")
        return None
    

def submit_data(topcut):
    connection = connect_to_db()
    if connection is None:
        return "Error connecting to database."
    
    try:
        cursor = connection.cursor()
        # Insert data into the database
        cursor.execute(
            sql.SQL("INSERT INTO tournaments (tour_name, tour_type, date, format) VALUES (%s, %s, %s, %s) RETURNING id"),
            (topcut.tour_name, topcut.tour_type, topcut.date, topcut.format)
        )
        tournament_id = cursor.fetchone()[0]
        for index, player in enumerate(topcut.players):
            cursor.execute(
                sql.SQL("INSERT INTO players (tournament_id, player_index) VALUES (%s, %s) RETURNING id"),
                (tournament_id, index)
            )
            player_id = cursor.fetchone()[0]
            for pokemon in player.pokemon:
                cursor.execute(
                    sql.SQL("INSERT INTO pokemon (player_id, name, item, teratype) VALUES (%s, %s, %s, %s)"),
                    (player_id, pokemon.name, pokemon.item, pokemon.teratype)
                )
        connection.commit()
        print("Data submitted successfully.")
        return "Data submitted successfully."
    except Exception as error:
        print(f"Error submitting data: {error}")
        return "Error submitting data."
    finally:
        cursor.close()
        connection.close()
