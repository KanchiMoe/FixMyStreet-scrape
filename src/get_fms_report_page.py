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
        return response.content

    elif response.status_code == 404:
        logging.warning("Response was 404")
        src.SQL_insert_into_db({
            "number": random_number,
            "status": "N/a - 404",
            "editable": False,
            "timestamp": None,
            "category": "N/a - 404",
            "title": "N/a - HTTP 404, Not Found",
            "description": "N/a - HTTP 404, Not Found",
            "lat": 0.0,
            "lon": 0.0
            }
        )
        return "404"
    
    elif response.status_code == 403:
        logging.warning("Response was 403")
        src.SQL_insert_into_db({
            "number": random_number,
            "status": "N/a - 404",
            "editable": False,
            "timestamp": None,
            "category": "N/a - 403",
            "title": "N/a - HTTP 403, Forbidden",
            "description": "N/a - HTTP 403, Forbidden",
            "lat": 0.0,
            "lon": 0.0
            }
        )
        return "403"


    elif response.status_code == 410:
        logging.warning("Response was 410")     
        src.SQL_insert_into_db({
            "number": random_number,
            "status": "N/a - 410",
            "editable": False,
            "timestamp": None,
            "category": "N/a",
            "title": "N/a - HTTP 410, Gone",
            "description": "N/a - HTTP 404, Not Found",
            "lat": 0.0,
            "lon": 0.0
            }
        )
        return "410"

    else:
        msg = f"Got unexpected response code: {response.status_code}"
        logging.critical(msg)
        raise ValueError
