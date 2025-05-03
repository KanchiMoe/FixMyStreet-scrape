import logging
import psycopg2 # type: ignore 
from psycopg2.extras import DictCursor # type: ignore
import time

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
            VALUES (%s, %s, %s)
            """,
            (number, lat, lon, council)
        )

def SQL_insert_into_db(data):
    
    insert_status(data["number"], data["status"], data["timestamp"], data["editable"])
    insert_details(data["number"], data["category"], data["title"], data["description"])
    insert_location(data["number"], data["lat"], data["lon"], data["council"])
    return None

# council




# def SQL_insert_into_db(number, status, category, timestamp, council, title):
#     with psycopg2.connect() as psql:
#         cursor = psql.cursor(cursor_factory=DictCursor)

#         cursor.execute(
#             """
#             INSERT INTO fms (id, status, category, reported_timestamp, council, title)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             """,
#             (number, status, category, timestamp, council, title)
#             )  
#         psql.commit()


# #cursor.execute("INSERT INTO fms (id, status, category, reported_timestamp, council, title) VALUES (%s, %s, %s, %s, %s, %s)", (number, status, category, timestamp, council, title))
        