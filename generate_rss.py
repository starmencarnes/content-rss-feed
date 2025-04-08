import csv
import os
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSE5yJ6z240_i34nXdBc1t-avF6Jct4YyeAhHcwyP-nzM4FPM_4h6_58SKsG1oaxXTUNvT-qD-Arh5X/pub?gid=0&single=true&output=csv"

def fetch_csv():
    """
    Downloads the CSV file from the CSV_URL.
    Returns a list of lines (strings).
    """
    response = requests.get(CSV_URL)
    response.raise_for_status()
    return response.text.splitlines()

def build_rss(csv_lines):
    """
    Parses the CSV data and builds an RSS 2.0 feed.
    """
    reader = csv.DictReader(csv_lines)

    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')

    # Basic channel info
    SubElement(channel, 'title').text = "My CSV RSS Feed"
    SubElement(channel, 'link').text = "https://yourusername.github.io/csv-to-rss/feed.xml"  
    SubElement(channel, 'description').text = "Auto-generated RSS feed from a CSV"

    for row in reader:
        item = SubElement(channel, 'item')

        # Title of the item
        SubElement(item, 'title').text = row.get('Title', 'No Title')

        # Use the CSV's "URL" column as the RSS <link>
        SubElement(item, 'link').text = row.get('URL', '')

        # Build the <description> from multiple fields
        description_parts = []

        # Body Copy
        body_copy = row.get('Body Copy', '')
        if body_copy:
            description_parts.append(body_copy)

        # Image (we’ll embed as an <img> tag)
        image_url = row.get('Image', '')
        if image_url:
            description_parts.append(f"<img src='{image_url}' alt='Image'/>")

        # CTA (anchor link) 
        cta_text = row.get('CTA', '')
        url_text = row.get('URL', '')
        if cta_text and url_text:
            description_parts.append(f"<a href='{url_text}'>{cta_text}</a>")

        # Join everything with some spacing / line breaks 
        full_description = "\n".join(description_parts)
        SubElement(item, 'description').text = full_description

        # Publish date
        # Attempt to parse Publish Date from MM/DD/YYYY 
        date_str = row.get('Publish Date', '')
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            # If parsing fails, use the current date/time 
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        SubElement(item, 'pubDate').text = pub_date

        # Optional: Add a GUID so readers can keep track of unique items
        guid_val = row.get('URL', '').strip() or row.get('Title', 'No Title')
        guid = SubElement(item, 'guid')
        guid.text = guid_val
        # Setting isPermaLink to false means we treat the GUID as a unique string rather than a valid URL
        guid.set('isPermaLink', 'false')

    # Prettify the XML
    return parseString(tostring(rss)).toprettyxml(indent="  ")

if __name__ == "__main__":
    # Fetch and parse the CSV
    csv_lines = fetch_csv()

    # Build RSS content
    rss_content = build_rss(csv_lines)

    # Ensure the docs folder exists
    os.makedirs("docs", exist_ok=True)

    # Write out the RSS file
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_content)
