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
SINGLE_NUMBER = 2
STRATEGY = "r"

def main():
    # Do a DB integrity check before continuing
    src.integrity_check()

    # get upper number from DB
    upper_number = src.SQL_get_UPPER_NUMBER()

    generator = None

    # process truncate variable
    src.truncate(TRUNCATE_DB_TABLES)

    # process strategy
    if STRATEGY in ("s", "sequential"):
        generator = src.sequential_strategy(upper_number)

    elif STRATEGY in ("r", "random"):
        generator = src.random_strategy(upper_number)

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

        # Get the report page
        response_content, reason = src.get_report_page(data["number"])

        # Escape if response was anything but 200
        if response_content in ("404", "403", "410"):
            src.SQL_insert_into_db({
                "number": number,
                "status": f"N/a - {response_content}",
                "editable": False,
                "timestamp": None,
                "category": f"N/a - {response_content}",
                "title": f"N/a - HTTP {response_content}, {reason}",
                "description": f"N/a - HTTP {response_content}, {reason}",
                "lat": 0.0,
                "lon": 0.0,
                "council": "N/a",
                "method": f"N/a - {response_content}",
                "updates": 0,
                "latest_update": None
                }
            )
            msg = f"Response code was {response_content}. Entry recorded, nothing more to process. Moving on..."
            logging.warning(msg)
            src.end_of_processing()
            continue

        # Process the page and insert into DB
        data = src.process_report_content(response_content, data)
        src.SQL_insert_into_db(data)

        src.end_of_processing()

if __name__ == "__main__":
    main()
