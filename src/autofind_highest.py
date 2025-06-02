import logging
import time

import src

def autofind_highest_report_id():
    logging.debug("Beginning autofind highest report number...")

    # check to see if we should run in the first place...
    should_run = src.SQL_check_autofind_should_run()

    if should_run is 0:
        logging.debug("DB value is 0, not running auto-find.")
        return

    # log that we're running autofind
    logging.info("Running autofind highest report number...")

    # get upper number from DB
    upper_number = src.SQL_get_UPPER_NUMBER()

    # set upper number to the iterator 
    number = upper_number
    consecutive_404s = 0

    while True:
        # request page 
        response_content, _ = src.get_report_page(number)

        if response_content == "404":
            # increase counter
            consecutive_404s += 1
            logging.debug(f"Had {consecutive_404s} 404s in a row")

            # break if we get more than 5 404s in a row
            if consecutive_404s >= 5:
                # log + update db
                logging.info(f"New highest report ID: {new_highest}")
                src.SQL_update_upper_number(new_highest)

                # break out
                logging.debug("Returning back to main function...")
                break

        else:
            logging.debug(f"Resetting consecutive_404s. Previous value: {consecutive_404s}")
            consecutive_404s = 0
            new_highest = number
            logging.info(f"Current highest number is now {new_highest}")

        number += 1
        logging.debug(f"Now trying {number}...")
        src.end_of_processing()
