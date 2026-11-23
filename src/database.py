# filepath: [database.py](http://_vscodecontentref_/0)

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file (without overriding hosting environment variables)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.is_file():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(find_dotenv())

def connect_to_db():
    try:
        connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            connect_kwargs = {}
            if "neon.tech" in db_url and "sslmode" not in db_url:
                connect_kwargs["sslmode"] = "require"
            if "connect_timeout" not in db_url:
                connect_kwargs["connect_timeout"] = connect_timeout
            connection = psycopg2.connect(db_url, **connect_kwargs)
        else:
            db_host = os.getenv("DB_HOST")
            if not db_host:
                print("Database not configured; skipping connection.")
                return None
            connect_kwargs = {
                "dbname": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "host": db_host,
                "port": os.getenv("DB_PORT", 5432),
                "connect_timeout": connect_timeout,
            }
            sslmode = os.getenv("DB_SSLMODE")
            if not sslmode and "neon.tech" in db_host:
                sslmode = "require"
            if sslmode:
                connect_kwargs["sslmode"] = sslmode
            connection = psycopg2.connect(**connect_kwargs)

        print("Connection to database established successfully.")
        return connection
    except Exception as error:
        print(f"Error connecting to database: {error}")
        return None
    

def submit_data(topcut):
    connection = connect_to_db()
    if connection is None:
        return "Error connecting to database."
    
    cursor = None
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
                    sql.SQL("INSERT INTO pokemon (player_id, name, item, teratype, gigantamax, shadow, purified, best_friend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                    (player_id, pokemon.name, pokemon.item, pokemon.teratype, pokemon.gmax, pokemon.shadow, pokemon.purified, pokemon.best_friend)
                )
        connection.commit()
        print("Data submitted successfully.")
        return "Data submitted successfully."
    except Exception as error:
        print(f"Error submitting data: {error}")
        return "Error submitting data."
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
