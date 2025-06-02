import logging
import psycopg2 # type: ignore 
from psycopg2.extras import DictCursor # type: ignore
import time
from datetime import datetime, timezone

def truncate(bool):
    if bool:
        logging.warning("TRUNCATING TB TABLES in 3 seconds...")
        time.sleep(3)
        with psycopg2.connect() as psql:
            cursor = psql.cursor(cursor_factory=DictCursor)
            cursor.execute(
                """
                TRUNCATE TABLE "public"."details";
                TRUNCATE TABLE "public"."status";
                TRUNCATE TABLE "public"."location";
                TRUNCATE TABLE "public"."method";
                TRUNCATE TABLE "public"."updates";
                TRUNCATE TABLE "public"."logs";
                """,
                ()
            )
            psql.commit()
        logging.info("DB TABLES TRUNCATED")
        logging.debug("Waiting for 3 seconds before continuing...")
        time.sleep(3)
        return None

    else:
        return None

def insert_status(number: int, status: str, timestamp, editable):
    logging.debug("Writing status to DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO status (id, status, reported_timestamp, editable)
            VALUES (%s, %s, %s, %s)
            """,
            (number, status, timestamp, editable)
        )
        psql.commit()
    return None

def insert_details(number: int, category: str, title: str, description: str):
    logging.debug("Writing details to DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO details (id, category, title, description)
            VALUES (%s, %s, %s, %s)
            """,
            (number, category, title, description)
        )
        psql.commit()
    return None

def insert_location(number: int, lat: int, lon: int, council: str):
    logging.debug("Writing location to DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO location (id, latitude, longitude, council)
            VALUES (%s, %s, %s, %s)
            """,
            (number, lat, lon, council)
        )

def insert_methods(number: int, method: str):
    logging.debug("Writing method to DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO method (id, method)
            VALUES (%s, %s)
            """,
            (number, method)
        )

def insert_updates(number: int, no_of_updates, latest_update):
    logging.debug("Writing updates to DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO updates (id, no_of_updates, latest_timestamp)
            VALUES (%s, %s, %s)
            """,
            (number, no_of_updates, latest_update)
        )

def insert_log(number: int):
    logging.debug("Writing log to DB...")

    # get timestamp
    timestamp = datetime.now(timezone.utc)

    # write to db
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            INSERT INTO logs (id, timestamp)
            VALUES (%s, %s)
            """,
            (number, timestamp)
        )

def SQL_insert_into_db(data):
    
    insert_status(data["number"], data["status"], data["timestamp"], data["editable"])
    insert_details(data["number"], data["category"], data["title"], data["description"])
    insert_location(data["number"], data["lat"], data["lon"], data["council"])
    insert_methods(data["number"], data["method"])
    insert_updates(data["number"], data["updates"], data["latest_update"])
    insert_log(data["number"])

    return None

def SQL_count_number_of_rows():
    logging.debug("Counting the number of rows in the DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            SELECT count(*) FROM status
            """,
            ()
        )
        result = cursor.fetchone()
        return result[0]

def SQL_get_UPPER_NUMBER():
    logging.debug("Getting UPPER_NUMBER from DB...")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            SELECT value FROM meta
            WHERE key = 'UPPER_NUMBER';
            """,
            ()
        )
        result = cursor.fetchone()
        
        logging.info(f"Got {result[0]} as UPPER_NUMBER from DB...")
        return int(result[0])

def SQL_update_upper_number(new_upper_number: int):
    logging.debug(f"Updating UPPER_NUMBER in DB to {new_upper_number}... ")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute(
            """
            UPDATE meta
            SET value = '%s'
            WHERE key = 'UPPER_NUMBER';
            """,
            (new_upper_number, )
        )
