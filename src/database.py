import os
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql
from dotenv import find_dotenv, load_dotenv

# Load environment variables from .env file (without overriding hosting environment variables)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.is_file():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(find_dotenv())


def _format_tournament_date(raw_date):
    """Format tournament date strings to YYYY-MM-DD when matching known formats."""
    formatted_date = raw_date
    if raw_date and isinstance(raw_date, str):
        try:
            date_str = raw_date.strip()
            for date_format in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
        except Exception as e:
            print(f"Warning: Could not format date '{raw_date}'. Using as is. Error: {e}")
    return formatted_date


def _get_mysql_config() -> dict | None:
    """Return MySQL connection settings from DATABASE_URL or individual DB_* variables."""
    db_url = os.getenv("DATABASE_URL") or ""
    if db_url.startswith(("mysql://", "mysql+pymysql://")):
        parsed = urlparse(db_url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "database": unquote(parsed.path.lstrip("/")),
        }

    db_host = os.getenv("DB_HOST")
    if db_host:
        return {
            "host": db_host,
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER") or "",
            "password": os.getenv("DB_PASSWORD") or "",
            "database": os.getenv("DB_NAME") or "",
        }
    return None


def connect_to_db():
    """Establish and return a PyMySQL connection, or None if unconfigured/unreachable."""
    cfg = _get_mysql_config()
    if cfg is None:
        print("Database not configured; skipping connection.")
        return None

    try:
        connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
        connection = pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            charset="utf8mb4",
            connect_timeout=connect_timeout,
            autocommit=False,
            init_command="SET SESSION sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'",
        )
        print("Connection to MySQL database established successfully.")
        return connection
    except Exception as error:
        print(f"Error connecting to MySQL database: {error}")
        return None


def submit_data(topcut):
    """Submit tournament, player, and Pokémon records to MySQL."""
    connection = connect_to_db()
    if connection is None:
        return "Error connecting to database."

    cursor = None
    try:
        cursor = connection.cursor()
        formatted_date = _format_tournament_date(topcut.date)
        print("Final formatted date:", formatted_date)

        tour_type = topcut.tour_type.value if hasattr(topcut.tour_type, "value") else str(topcut.tour_type)
        game = topcut.game.value if hasattr(topcut.game, "value") else str(topcut.game)

        cursor.execute(
            "INSERT INTO tournaments (tour_name, tour_type, date, format, game) VALUES (%s, %s, %s, %s, %s)",
            (topcut.tour_name, tour_type, formatted_date, topcut.format, game),
        )
        tournament_id = cursor.lastrowid

        for index, player in enumerate(topcut.players):
            cursor.execute(
                "INSERT INTO players (tournament_id, player_index) VALUES (%s, %s)",
                (tournament_id, index),
            )
            player_id = cursor.lastrowid
            pokemon_rows = [
                (
                    player_id,
                    pokemon.name,
                    None if pokemon.item == "" else pokemon.item,
                    None if pokemon.teratype == "" else pokemon.teratype,
                    bool(pokemon.gmax),
                    bool(pokemon.shadow),
                    bool(pokemon.purified),
                    bool(pokemon.best_friend),
                )
                for pokemon in player.pokemon
                if pokemon.name != ""
            ]
            if pokemon_rows:
                cursor.executemany(
                    "INSERT INTO pokemon (player_id, name, item, teratype, gigantamax, shadow, purified, best_friend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    pokemon_rows,
                )

        connection.commit()
        print("Data submitted successfully via MySQL.")
        return "Data submitted successfully."
    except Exception as error:
        try:
            connection.rollback()
        except Exception:
            pass
        print(f"Error submitting data via MySQL: {error}")
        return "Error submitting data."
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
