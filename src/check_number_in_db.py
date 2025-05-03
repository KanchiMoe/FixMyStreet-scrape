import logging
import psycopg2 # type: ignore 
from psycopg2.extras import DictCursor # type: ignore

def is_number_in_db(number):
    logging.debug(f"Checking to see if {number} is in the DB or not")
    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT 1 FROM status WHERE id = %s LIMIT 1;", (number,))
        result = cursor.fetchone()

        logging.debug(f"Result: {result}")
        if result:
            logging.info("IS IN database")
            return True
        else:
            logging.info("NOT in database")
            return False