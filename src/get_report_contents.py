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

    # Try full datetime first
    match = re.search(r"at (\d{1,2}:\d{2},\s(?:\w+)\s+\d{1,2}\s+\w+\s+\d{4})", text)
    if match:
        time_str = match.group(1)
        logging.debug(f"Reported timestamp (raw): {time_str}")
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M, %A %d %B %Y")
        except ValueError:
            parsed_time = datetime.strptime(time_str, "%H:%M, %a %d %B %Y")
        logging.info(f"Parsed timestamp: {parsed_time}")
        data["timestamp"] = parsed_time
        return data

    # Try matching partial (e.g., just weekday)
    match_partial = re.search(r"at (\d{1,2}:\d{2},\s\w+)", text)
    if match_partial:
        time_str = match_partial.group(1)
        logging.warning(f"Partial timestamp found (weekday only): {time_str}. Skipping precise datetime.")
        data["timestamp"] = None  # or set a fallback if needed
        return data

    raise ValueError(f"Could not parse timestamp from meta info text: {text}")

def get_category(meta_tag, data):
    logging.debug("Getting category...")

    text = meta_tag.get_text(strip=True)
    
    # Allow optional "via ... " part
    match = re.search(r"Reported(?: via \w+)? in the (.*?) category", text)
    if not match:
        logging.warning(f"Category not found in meta info: {text}")
        data["category"] = "N/a"
        return data
        
    category = match.group(1)
    logging.info(f"Category: {category}")

    data["category"] = category
    return data

def get_council_sentto(council_tag, data, meta_tag=None):
    logging.debug("Getting the council the report was sent to...")

    text = council_tag.get_text()
    text = " ".join(text.split())  # Normalize whitespace

    if "Not reported to council" in text:
        data["council"] = "Not reported to council"
        logging.warning("Detected 'Not reported to council'")
        return data

    if "Council ref:" in text and "Sent to" not in text:
        council_ref = text.split("Council ref:")[1].strip()
        council_name = f"Council ref: {council_ref}"
        logging.info(f"Council ref detected: {council_name}")
        data["council"] = council_name
        return data

    a_tag = council_tag.find("a")
    if a_tag:
        council_name = a_tag.get_text(strip=True)
        logging.info(f"Council (via link): {council_name}")
        data["council"] = council_name
        return data

    match = re.search(r"Sent to\s*(.+?)\s+(?:\d+|less than a minute|\w+ minutes|\w+ hours|\w+ days|FixMyStreet)", text)
    if match:
        council_name = match.group(1).strip()
        logging.info(f"Council (via regex): {council_name}")
        data["council"] = council_name
        return data

    # new: fallback from meta_tag
    if meta_tag:
        meta_text = meta_tag.get_text(strip=True)
        meta_match = re.search(r"by (.+?) at", meta_text)
        if meta_match:
            council_name = meta_match.group(1).strip()
            logging.info(f"Council (via report_meta_info): {council_name}")
            data["council"] = council_name
            return data

    # Fail if all else fails
    msg = f"Could not extract council name from text: {text}"
    logging.critical(msg)
    raise ValueError(msg)


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

def get_method(meta_tag, data):
    logging.debug("Getting report method...")

    text = meta_tag.get_text(strip=True)

    match = re.search(r"Reported via (\w+)", text)
    if match:
        method = match.group(1)
        logging.info(f"Report method: {method}")
        data["method"] = method
    else:
        logging.warning(f"No method found in meta info: {text}")
        data["method"] = "N/a"

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
    data = get_council_sentto(council_tag, data, meta_tag)
    data = get_title(side_report, data)
    data = get_description(side_report, data)
    data = get_lat_lon(side_report, data)
    data = get_method(meta_tag, data)

    logging.debug(f"Returning data: {data}")
    return data

    






    