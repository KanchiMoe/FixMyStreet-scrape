from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

def get_previous_weekday(target_weekday):
    """Return the most recent past date for a given weekday name (e.g., 'Monday')."""
    today = datetime.today()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Normalize for consistent matching
    target_weekday = target_weekday.capitalize()

    try:
        target_index = weekdays.index(target_weekday)
    except ValueError:
        raise ValueError(f"Unknown weekday name: {target_weekday}")

    today_index = today.weekday()
    days_difference = (today_index - target_index) % 7
    if days_difference == 0:
        days_difference = 7  # Go back to previous week if it's the same day

    return today - timedelta(days=days_difference)

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

    # Handle partial timestamp like "at 10:32, Monday"
    match_partial = re.search(r"at (\d{1,2}:\d{2}),\s(\w+)", text)
    if match_partial:
        time_part, weekday = match_partial.groups()
        logging.debug(f"Partial timestamp found: {time_part}, {weekday}")
        try:
            date_part = get_previous_weekday(weekday)
            time_obj = datetime.strptime(time_part, "%H:%M").time()
            full_datetime = datetime.combine(date_part.date(), time_obj)
            logging.info(f"Resolved partial timestamp to: {full_datetime}")
            data["timestamp"] = full_datetime
            return data
        except Exception as e:
            logging.critical(f"Failed to resolve partial timestamp: {e}")
            data["timestamp"] = None
            return data

    raise ValueError(f"Could not parse timestamp from meta info text: {text}")

def get_category(meta_tag, data):
    logging.debug("Getting category...")

    text = meta_tag.get_text(strip=True)
    
    # Allow optional "via ... " part
    match = re.search(r"Reported(?: via \w+)? in the (.*?) category", text)
    if not match:
        logging.warning(f"Category not found in meta info")
        logging.debug(f"Text: {text}")
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

    # Edge case: not reported
    if "Not reported to council" in text:
        data["council"] = "Not reported to council"
        logging.warning("Detected 'Not reported to council'")
        return data

    # Edge case: council ref only
    if "Council ref:" in text and "Sent to" not in text:
        council_ref = text.split("Council ref:")[1].strip()
        council_name = f"Council ref: {council_ref}"
        logging.info(f"Council ref detected: {council_name}")
        data["council"] = council_name
        return data

    # Edge case: council name in hyperlink
    a_tag = council_tag.find("a")
    if a_tag:
        council_name = a_tag.get_text(strip=True)
        logging.info(f"Council (via link): {council_name}")
        data["council"] = council_name
        return data

    # Fallback regex if no <a> tag
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
        logging.warning(f"No report method found in meta info")
        logging.debug(f"Text: {text}")
        data["method"] = "N/a"

    return data

def get_update_count(updates_tag):
    logging.debug("Counting update items...")
    update_items = updates_tag.find_all("li", class_="item-list__item--updates")
    count = len(update_items)
    logging.info(f"Found {count} update(s).")
    return count

def get_update_timestamp(updates_tag):
    logging.debug("Looking for the latest update timestamp...")

    update_items = updates_tag.find_all("li", class_="item-list__item--updates")

    for item in reversed(update_items):
        meta_tags = item.find_all("p", class_="meta-2")
        for tag in reversed(meta_tags):
            text = tag.get_text(strip=True)
            logging.debug(f"Checking update meta text: {text}")

            # Try full timestamp first
            match = re.search(r"(\d{1,2}:\d{2}),\s+(\w{3,9})\s+(\d{1,2})\s+(\w+)\s+(\d{4})", text)
            if match:
                time_str = f"{match.group(1)}, {match.group(2)} {match.group(3)} {match.group(4)} {match.group(5)}"
                try:
                    parsed_time = datetime.strptime(time_str, "%H:%M, %a %d %B %Y")
                    logging.info(f"Latest update timestamp parsed: {parsed_time}")
                    return parsed_time
                except ValueError:
                    try:
                        parsed_time = datetime.strptime(time_str, "%H:%M, %A %d %B %Y")
                        logging.info(f"Latest update timestamp parsed: {parsed_time}")
                        return parsed_time
                    except Exception as e2:
                        logging.warning(f"Failed to parse timestamp '{time_str}': {e2}")
                        continue

            # Try partial timestamp: e.g. "at 10:32, Monday"
            match_partial = re.search(r"at (\d{1,2}:\d{2}),\s(\w+)", text)
            if match_partial:
                time_part, weekday = match_partial.groups()
                logging.debug(f"Partial update timestamp found: {time_part}, {weekday}")
                try:
                    date_part = get_previous_weekday(weekday)
                    time_obj = datetime.strptime(time_part, "%H:%M").time()
                    full_datetime = datetime.combine(date_part.date(), time_obj)
                    logging.info(f"Resolved update partial timestamp to: {full_datetime}")
                    return full_datetime
                except Exception as e:
                    logging.critical(f"Failed to resolve partial update timestamp: {e}")
                    continue

    msg = "No valid update timestamp found in updates."
    logging.critical(msg)
    raise ValueError(msg)

def get_updates(updates_tag, data):
    logging.debug("Getting updates...")

    if not updates_tag:
        logging.warning("No updates_tag provided. Defaulting to 0 updates.")
        data["updates"] = 0
        data["latest_update"] = None
        return data

    count = get_update_count(updates_tag)
    if count is None:
        msg = "Updates count is 'None'"
        logging.critical(msg)
        raise ValueError(msg)

    data["updates"] = count
    data["latest_update"] = get_update_timestamp(updates_tag)

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
    
    updates_tag = soup.find("section", class_="full-width")
    if not updates_tag:
        msg = "No <section class='full-width'> (updates section) found"
        logging.warning(msg)
        data["updates"] = 0
        data["latest_update"] = None
   
    data = get_status(side_report, data)
    data = get_editable(side_report, data)
    data = get_timestamp(meta_tag, data)
    data = get_category(meta_tag, data)
    data = get_council_sentto(council_tag, data, meta_tag)
    data = get_title(side_report, data)
    data = get_description(side_report, data)
    data = get_lat_lon(side_report, data)
    data = get_method(meta_tag, data)
    data = get_updates(updates_tag, data)

    logging.debug(f"Returning data: {data}")
    return data
