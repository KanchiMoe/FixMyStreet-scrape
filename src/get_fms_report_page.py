import logging
import requests

import src

def get_report_page(random_number):
    data = {}
    FMS_REPORT_URL = f"https://www.fixmystreet.com/report/{random_number}"
    logging.debug(f"Constructed URL: {FMS_REPORT_URL}")

    logging.info(f"Requesting URL: {FMS_REPORT_URL}")
    response = requests.get(FMS_REPORT_URL)
    logging.info(f"Response status: {response.status_code}")

    data["number"] = random_number

    if response.status_code == 200:
        return response.content, ""

    elif response.status_code == 404:
        logging.warning("Response was 404")
        return "404", "Not Found"
    
    elif response.status_code == 403:
        logging.warning("Response was 403")
        return "403", "Forbidden"

    elif response.status_code == 410:
        logging.warning("Response was 410")     
        return "410", "Gone"

    else:
        msg = f"Got unexpected response code: {response.status_code}"
        logging.critical(msg)
        raise ValueError
