# filepath: [database.py](http://_vscodecontentref_/0)

import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse
import requests

# Load environment variables from .env file (without overriding hosting environment variables)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.is_file():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(find_dotenv())


def _is_neon_host(hostname: str) -> bool:
    host = (hostname or "").lower()
    return host == "neon.tech" or host.endswith(".neon.tech")


def _format_tournament_date(raw_date):
    """Format tournament date strings to YYYY-MM-DD when matching known formats."""
    formatted_date = raw_date
    if raw_date and isinstance(raw_date, str):
        try:
            date_str = raw_date.strip()  # ← strip spaces and line breaks
            for date_format in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    formatted_date = parsed_date.strftime('%Y-%m-%d')  # PostgreSQL ISO format
                    break
                except ValueError:
                    continue
        except Exception as e:
            print(f"Warning: Could not format date '{raw_date}'. Using as is. Error: {e}")
    return formatted_date


def _get_neon_http_config() -> tuple[str, str] | None:
    """Return (endpoint_url, connection_string) when configured for Neon Postgres."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        hostname = urlparse(db_url).hostname or ""
        if _is_neon_host(hostname):
            return f"https://{hostname}/sql", db_url
        return None

    db_host = os.getenv("DB_HOST") or ""
    if _is_neon_host(db_host):
        user = quote(os.getenv("DB_USER") or "", safe="")
        password = quote(os.getenv("DB_PASSWORD") or "", safe="")
        db_name = quote(os.getenv("DB_NAME") or "", safe="")
        sslmode = quote(os.getenv("DB_SSLMODE") or "require", safe="")
        conn_str = f"postgresql://{user}:{password}@{db_host}/{db_name}?sslmode={sslmode}"
        return f"https://{db_host}/sql", conn_str
    return None


def _submit_data_neon_http(topcut, endpoint_url: str, conn_str: str) -> str:
    """Submit tournament data atomically via Neon's SQL-over-HTTP endpoint (port 443)."""
    formatted_date = _format_tournament_date(topcut.date)
    print("Final formatted date:", formatted_date)

    players_payload = [
        {
            "player_index": index,
            "pokemon": [
                {
                    "name": pokemon.name,
                    "item": None if pokemon.item == "" else pokemon.item,
                    "teratype": None if pokemon.teratype == "" else pokemon.teratype,
                    "gmax": bool(pokemon.gmax),
                    "shadow": bool(pokemon.shadow),
                    "purified": bool(pokemon.purified),
                    "best_friend": bool(pokemon.best_friend),
                }
                for pokemon in player.pokemon
                if pokemon.name != ""
            ],
        }
        for index, player in enumerate(topcut.players)
    ]

    tour_type = topcut.tour_type.value if hasattr(topcut.tour_type, "value") else str(topcut.tour_type)
    game = topcut.game.value if hasattr(topcut.game, "value") else str(topcut.game)

    query = """
    WITH new_tournament AS (
        INSERT INTO tournaments (tour_name, tour_type, date, format, game)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    ),
    new_players AS (
        INSERT INTO players (tournament_id, player_index)
        SELECT nt.id, (p->>'player_index')::int
        FROM new_tournament nt,
             jsonb_array_elements($6::jsonb) AS p
        RETURNING id, player_index
    )
    INSERT INTO pokemon (player_id, name, item, teratype, gigantamax, shadow, purified, best_friend)
    SELECT np.id,
           mon->>'name',
           NULLIF(mon->>'item', ''),
           NULLIF(mon->>'teratype', ''),
           (mon->>'gmax')::boolean,
           (mon->>'shadow')::boolean,
           (mon->>'purified')::boolean,
           (mon->>'best_friend')::boolean
    FROM new_players np
    JOIN jsonb_array_elements($6::jsonb) AS p
      ON (p->>'player_index')::int = np.player_index
    CROSS JOIN LATERAL jsonb_array_elements(p->'pokemon') AS mon
    WHERE COALESCE(mon->>'name', '') <> ''
    """

    params = [
        topcut.tour_name,
        tour_type,
        formatted_date,
        topcut.format,
        game,
        json.dumps(players_payload),
    ]

    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    read_timeout = int(os.getenv("DB_HTTP_TIMEOUT", "15"))

    try:
        resp = requests.post(
            endpoint_url,
            json={"query": query, "params": params},
            headers={
                "Content-Type": "application/json",
                "Neon-Connection-String": conn_str,
            },
            timeout=(connect_timeout, read_timeout),
        )
    except requests.RequestException as error:
        print(f"Error connecting to Neon HTTP endpoint ({endpoint_url}): {error}")
        return "Error connecting to database."

    if resp.status_code == 200:
        print("Data submitted successfully via Neon HTTP.")
        return "Data submitted successfully."

    message = resp.text
    code = ""
    try:
        err_body = resp.json()
        if isinstance(err_body, dict):
            message = err_body.get("message") or message
            code = err_body.get("code") or ""
    except ValueError:
        pass

    print(f"Error submitting data via Neon HTTP (status {resp.status_code}, code={code}): {message}")
    return "Error submitting data."

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
    neon_cfg = _get_neon_http_config()
    if neon_cfg is not None:
        return _submit_data_neon_http(topcut, neon_cfg[0], neon_cfg[1])

    connection = connect_to_db()
    if connection is None:
        return "Error connecting to database."
    
    cursor = None
    try:
        cursor = connection.cursor()
        # Insert data into the database
        formatted_date = _format_tournament_date(topcut.date)
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
