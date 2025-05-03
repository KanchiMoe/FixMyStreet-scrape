import src
import src.colourlog as colourlog

import os
import logging
import random
from dotenv import load_dotenv
import psycopg2 # type: ignore 
from psycopg2.extras import DictCursor # type: ignore


from datetime import datetime, timezone
import time

DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL") or logging.DEBUG
logging.getLogger().setLevel(DEFAULT_LOG_LEVEL)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

colourlog.setup_logger()

# def get_random_number():
#     logging.debug("Getting random number")
#     UPPER_NUMBER = 9999
#     random_number = random.randint(1, UPPER_NUMBER)
    
#     logging.info(f"Random numbear {random_number}")
#     return random_number


TRUNCATE_DB_TABLES = True
UPPER_NUMBER = 1 + 7519070





###########################
def main():
    data = {}

    src.truncate(TRUNCATE_DB_TABLES)

    for i in range(1, UPPER_NUMBER):
        
        data["number"] = i

        # Check if the number is already in the database
        in_db = src.is_number_in_db(data["number"])
        
        # If the number is in the database, restart by continuing the loop
        if in_db is True:
            print(f"ID {data["number"]} is already in the database. Trying again...")
            continue  # Start the loop over, getting a new random number
        
        # Otherwise, get the report page
        response_content = src.get_report_page(data["number"])
        
        # If the response content is "404", skip to the next iteration
        if response_content in ("404", "410"):
            msg = f"Response code was {response_content}. Entry recorded, nothing more to process. Moving on..."
            logging.warning(msg)
            time.sleep(1)
            continue # Start the loop over

        # Process the page, extract the required data
        data = src.process_report_content(response_content, data)

        # Write into the database
        src.SQL_insert_into_db(data)

        print("=" * 50)

        time.sleep(1)
        


if __name__ == "__main__":
    main()
