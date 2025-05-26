import logging
import random

def get_random_number(UPPER_NUMBER: int):
    logging.debug("Getting random number...")
    return random.randint(1, UPPER_NUMBER)
