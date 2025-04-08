import csv
import os
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSE5yJ6z240_i34nXdBc1t-avF6Jct4YyeAhHcwyP-nzM4FPM_4h6_58SKsG1oaxXTUNvT-qD-Arh5X/pub?gid=0&single=true&output=csv"

def fetch_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    return response.text.splitlines()

def build_rss(csv_lines):
    reader = csv.DictReader(csv_lines)
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')

    # Channel information
    SubElement(channel, 'title').text = "My CSV RSS Feed"
    SubElement(channel, 'link').text = "https://yourusername.github.io/csv-to-rss/feed.xml"
    SubElement(channel, 'description').text = "Auto-generated RSS feed from a CSV"

    for row in reader:
        item = SubElement(channel, 'item')

        # Title
        SubElement(item, 'title').text = row.get('Title', 'No Title')

        # URL goes into <link>
        SubElement(item, 'link').text = row.get('URL', '')

        # Build the description from Body Copy and Image only
        description_parts = []

        # Body Copy
        body_copy = row.get('Body Copy', '')
        if body_copy:
            description_parts.append(body_copy)

        # Image: added as an HTML <img> element if available
        image_url = row.get('Image', '')
        if image_url:
            description_parts.append(f"<img src='{image_url}' alt='Image'/>")

        full_description = "\n".join(description_parts)
        SubElement(item, 'description').text = full_description

        # Add the call-to-action (CTA) text in a separate <cta> element
        cta_text = row.get('CTA', '')
        if cta_text:
            cta_elem = SubElement(item, 'cta')
            cta_elem.text = cta_text

        # Parse the publish date (expected format: MM/DD/YYYY)
        date_str = row.get('Publish Date', '')
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        SubElement(item, 'pubDate').text = pub_date

        # Add a GUID element so feed readers can uniquely identify each item
        guid
