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

TRUNCATE_DB_TABLES = True
UPPER_NUMBER = 7519490
USE_RANDOM = True  # Set to True to use random numbers
FOOBAR = 2014736

def scrape_fms(number: int):
    data = {"number": number}

    # Check if the number is already in the database
    if src.is_number_in_db(data["number"]):
        print(f"ID {data['number']} is already in the database. Trying again...")
        return  # Skip this number

    # Get the report page
    response_content = src.get_report_page(data["number"])

    # Escape if response was anything but 200
    if response_content in ("404", "403", "410"):
        msg = f"Response code was {response_content}. Entry recorded, nothing more to process. Moving on..."
        logging.warning(msg)
        time.sleep(1)
        return

    # Process the page and insert into DB
    data = src.process_report_content(response_content, data)
    src.SQL_insert_into_db(data)

    print("=" * 50)
    time.sleep(1)

def main():
    src.truncate(TRUNCATE_DB_TABLES)

    if FOOBAR:
        logging.info("Only processing 1 number")
        scrape_fms(FOOBAR)
        return

    if USE_RANDOM:
        logging.info("Using random number sequence")
        while True:
            number = src.get_random_number(UPPER_NUMBER)
            scrape_fms(number)
    else:
        logging.info("Using sequential number sequence")
        for number in range(1, UPPER_NUMBER + 1):
            scrape_fms(number)

if __name__ == "__main__":
    main()
