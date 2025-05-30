import logging
import psycopg2 # type: ignore 
from psycopg2.extras import DictCursor # type: ignore

def SQL_get_row_counts(tables: list):
    logging.debug("Getting row counts...")
    row_counts = {}

    with psycopg2.connect() as psql:
        cursor = psql.cursor(cursor_factory=DictCursor)
        for table in tables:
            query = f"SELECT count(*) FROM {table};" # !! this is dangerous !! but it's not user input.
            cursor.execute(query)

            result = cursor.fetchone()
            row_counts[table] = result[0]
            logging.debug(f"Table: {table}, count: {result[0]}")

    return row_counts
    

def integrity_check():
    logging.info("Starting DB integrity check...")

    tables = ["details", "location", "logs", "method", "status", "updates"]
    row_counts = SQL_get_row_counts(tables)

    counts = []
    for table in tables:
        counts.append(row_counts[table])

    if len(set(counts)) == 1:
        logging.info("All tables have the same row count")
    else:
        msg = "Tables have differing row counts"
        logging.critical(msg)
        raise ValueError(msg)
