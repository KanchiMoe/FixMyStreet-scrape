import logging
import src
import time

def is_done(highest_number: int):
    return src.SQL_count_number_of_rows() == highest_number

def sequential_strategy(highest_number: int):
    logging.info("Using sequential number sequence")
    start = 1

    for number in range(start, highest_number + 1):
        # Check if number is already in db
        if src.is_number_in_db(number):
            logging.info("Skipping this number...")
            print("=" * 80)
            continue # skip number

        yield number # else return/yield
    return


def single_strategy(single_number: int):
    logging.info("Only processing 1 number")
    yield single_number

def random_strategy(highest_number: int):
    while not is_done(highest_number):
        number = src.get_random_number(highest_number)

        # check if number is in db
        if src.is_number_in_db(number):
            continue # skip number

        yield number
