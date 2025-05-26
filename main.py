import src
import src.colourlog as colourlog

from dotenv import load_dotenv
import logging
import os
import time

load_dotenv()

# Set logging variables
DEFAULT_LOG_LEVEL = os.environ.get("LOG_LEVEL") or logging.DEBUG
logging.getLogger().setLevel(DEFAULT_LOG_LEVEL)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

colourlog.setup_logger()

TRUNCATE_DB_TABLES = False
UPPER_NUMBER = 7519490
SINGLE_NUMBER = 2
STRATEGY = "r"

def main():
    generator = None

    # process truncate variable
    src.truncate(TRUNCATE_DB_TABLES)

    # process strategy
    if STRATEGY in ("s", "sequential"):
        generator = src.sequential_strategy(UPPER_NUMBER)

    elif STRATEGY in ("r", "random"):
        generator = src.random_strategy(UPPER_NUMBER)

    elif STRATEGY in (1, "single"):
        if SINGLE_NUMBER:
            generator = src.single_strategy(SINGLE_NUMBER)
        else:
            msg = f"Value of SINGLE_NUMBER not allowed. Value: {SINGLE_NUMBER}"
            logging.critical(msg)
            raise ValueError(msg)

    else:
        msg = f"Unknown or none strategy given. Was given: {STRATEGY}"
        logging.critical(msg)
        raise ValueError(msg)
    
    # process
    for number in generator:
        data = {"number": number}

        print("THIS IS WHERE OTHER WORK THINGS NEED TO HAPPEN, LIKE GETTING THE PAGE")

        # Get the report page
        response_content = src.get_report_page(data["number"])

        # Escape if response was anything but 200
        if response_content in ("404", "403", "410"):
            msg = f"Response code was {response_content}. Entry recorded, nothing more to process. Moving on..."
            logging.warning(msg)
            print("=" * 50)
            time.sleep(1)
            continue

        # Process the page and insert into DB
        data = src.process_report_content(response_content, data)
        src.SQL_insert_into_db(data)

        print("=" * 50)
        time.sleep(1)

if __name__ == "__main__":
    main()
