# filepath: [database.py](http://_vscodecontentref_/0)

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from datetime import datetime

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
        
        # Format date to YYYY-MM-DD for PostgreSQL
        formatted_date = topcut.date
        if topcut.date and isinstance(topcut.date, str):
            try:
                date_str = topcut.date.strip()  # ← strip spaces and line breaks
                for date_format in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        formatted_date = parsed_date.strftime('%Y-%m-%d')  # PostgreSQL ISO format
                        break
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Warning: Could not format date '{topcut.date}'. Using as is. Error: {e}")

        print("Final formatted date:", formatted_date)  # Add debug
        
        cursor.execute(
            sql.SQL("INSERT INTO tournaments (tour_name, tour_type, date, format, game) VALUES (%s, %s, %s, %s, %s) RETURNING id"),
            (topcut.tour_name, topcut.tour_type, formatted_date, topcut.format, topcut.game)
        )
        tournament_id = cursor.fetchone()[0]
        for index, player in enumerate(topcut.players):
            cursor.execute(
                sql.SQL("INSERT INTO players (tournament_id, player_index) VALUES (%s, %s) RETURNING id"),
                (tournament_id, index)
            )
            player_id = cursor.fetchone()[0]
            for pokemon in player.pokemon:
                if pokemon.name == "":
                    continue
                if pokemon.item == "":
                    pokemon.item = None
                if pokemon.teratype == "":
                    pokemon.teratype = None
                cursor.execute(
                    sql.SQL("INSERT INTO pokemon (player_id, name, item, teratype, gigantamax) VALUES (%s, %s, %s, %s, %s)"),
                    (player_id, pokemon.name, pokemon.item, pokemon.teratype, pokemon.gmax)
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
