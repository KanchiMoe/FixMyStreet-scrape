from bs4 import BeautifulSoup
from datetime import datetime, timezone
import logging
import re

def get_status(side_report, data):
    logging.debug("Getting status...")
    banner = side_report.find(class_="banner")

    if banner:
        classes = banner.get("class", [])
        if "banner--unknown" in classes:
            logging.info("Report status is UNKNOWN")
            data["status"] = "Unknown"
        elif "banner--fixed" in classes:
            logging.info("Report status is FIXED")
            data["status"] = "Fixed"
        elif "banner--closed" in classes:
            logging.info("Report status is CLOSED")
            data["status"] = "Closed"
        elif "banner--progress" in classes:
            logging.info("Report status is INVESTIGATING")
            data["status"] = "Investigating"
        else:
            msg = f"Unexpected banner status class: {classes}"
            logging.critical(msg)
            raise ValueError(msg)
    else:
        msg = "No status banner found on the page"
        logging.warning(msg)
        data["status"] = "Unknown"

    return data

def get_editable(side_report, data):
    logging.debug("Checking if report is editable...")

    update_form = side_report.find("div", id="update_form")
    data["editable"] = update_form is not None

    logging.info(f"Editable: {data['editable']}")
    return data

def get_timestamp(meta_tag, data):
    logging.debug("Getting timestamp...")

    text = meta_tag.get_text(strip=True)

    # Extract only the timestamp
    match = re.search(r"at (\d{1,2}:\d{2},\s\w{3}\s+\d{1,2}\s+\w+\s+\d{4})", text)
    if not match:
        raise ValueError(f"Could not parse timestamp from meta info text: {text}")
    
    time_str = match.group(1)
    logging.debug(f"Reported timestamp (raw): {time_str}")

    # Convert to datetime object
    parsed_time = datetime.strptime(time_str, "%H:%M, %a %d %B %Y")
    logging.info(f"Parsed timestamp: {parsed_time}")

    data["timestamp"] = parsed_time
    return data

def get_category(meta_tag, data):
    logging.debug("Getting category...")

    text = meta_tag.get_text(strip=True)
    
    match = re.search(r"Reported in the (.*?) category", text)
    if not match:
        # Some reports may not have categories. Warn, set as none and move on.
        logging.warning(f"Category not found in meta info: {text}")
        data["category"] = "N/a"
        return data
        
    category = match.group(1)
    logging.info(f"Category: {category}")

    data["category"] = category
    return data

def get_council_sentto(council_tag, data):
    logging.debug("Getting the council the report was sent to...")

    text = council_tag.get_text()
    text = " ".join(text.split())  # Normalize all whitespace

    if "Not reported to council" in text:
        NRTC = "Not reported to council"
        logging.warning(f"Detected '{NRTC}'. This has been set as the council in the DB.")
        data["council"] = NRTC
        return data

    # Check if it's a "Council ref" instead of "Sent to"
    if "Council ref:" in text:
        council_ref = text.split("Council ref:")[1].strip()
        council_name = f"Council ref: {council_ref}"
        logging.info(f"Council ref detected: {council_name}")
        data["council"] = council_name
        return data

    # Improved regex: stops before timing info or 'FixMyStreet ref'
    match = re.search(r"Sent to\s*(.+?)\s+(?:\d+|less than a minute|\w+ minutes|\w+ hours|\w+ days|FixMyStreet)", text)
    if not match:
        msg = f"Could not extract council name from text: {text}"
        logging.critical(msg)
        raise ValueError(msg)

    council_name = match.group(1).strip()

    # No need to add "Council" manually
    logging.info(f"Council: {council_name}")
    data["council"] = council_name
    return data

def get_title(side_report, data):
    logging.debug("Getting the report title...")

    title_tag = side_report.find("h1")
    if not title_tag:
        msg = "Could not find <h1> inside #side-report"
        logging.critical(msg)
        raise ValueError(msg)

    title = title_tag.get_text(strip=True)
    logging.info(f"Title: {title}")

    data["title"] = title
    return data

def get_description(side_report, data):
    logging.debug("Getting the report description...")

    description_div = side_report.find("div", class_="moderate-display")
    if not description_div:
        msg = "No <div class='moderate-display'> found inside #side-report"
        logging.critical(msg)
        raise ValueError(msg)

    # Get all <p> tags inside it
    paragraphs = description_div.find_all("p")
    if not paragraphs:
        msg = "No <p> tags found inside <div class='moderate-display'>"
        logging.warning(msg)
        data["description"] = None
        return data

    # Join all paragraphs into one block of text
    description_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
    
    logging.info(f"Extracted description: {description_text[:20]}...")  # preview first 20 chars
    data["description"] = description_text
    return data

def get_lat_lon(side_report, data):
    logging.debug("Extracting latitude and longitude...")

    a_tag = side_report.find("a", class_="problem-back")
    if not a_tag:
        raise ValueError("Could not find the 'problem-back' <a> tag in side-report.")

    href = a_tag.get("href", "")
    match = re.search(r"lat=([-\d.]+)&lon=([-\d.]+)", href)
    if not match:
        match = re.search(r"lon=([-\d.]+)&lat=([-\d.]+)", href)  # sometimes lon might come first
        if not match:
            raise ValueError(f"Could not extract lat/lon from href: {href}")
        lon, lat = match.groups()
    else:
        lat, lon = match.groups()

    data["lat"] = float(lat)
    data["lon"] = float(lon)
    logging.info(f"Extracted lat/lon: {data['lat']}, {data['lon']}")

    return data


def process_report_content(content, data):
    logging.debug("Processing contents...")

    soup = BeautifulSoup(content, 'html.parser')

    side_report = soup.find("div", id="side-report")
    if not side_report:
        msg = "Could not get dev 'side-report'"
        logging.critical(msg)
        return RuntimeError(msg)

    meta_tag = side_report.find("p", class_="report_meta_info")
    if not meta_tag:
        msg = "No <p class='report_meta_info'> found inside #side-report"
        logging.critical(msg)
        raise ValueError(msg)
    
    council_tag = side_report.find("p", class_="council_sent_info")
    if not council_tag:
        msg = "No <p class='council_sent_info'> found inside #side-report"
        logging.critical(msg)
        raise ValueError(msg)
    
    data = get_status(side_report, data)
    data = get_editable(side_report, data)
    data = get_timestamp(meta_tag, data)
    data = get_category(meta_tag, data)
    data = get_council_sentto(council_tag, data)
    data = get_title(side_report, data)
    data = get_description(side_report, data)
    data = get_lat_lon(side_report, data)

    logging.debug(f"Returning data: {data}")
    return data

    






    