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

    SubElement(channel, 'title').text = "6AM City - National Content Feed"
    SubElement(channel, 'link').text = "https://starmencarnes.github.io/content-rss-feed/feed.xml"
    SubElement(channel, 'description').text = "RSS feed housing daily national ad copy designed for site ingestion"

    for row in reader:
        item = SubElement(channel, 'item')

        # Title
        SubElement(item, 'title').text = row.get('Title', 'No Title')

        # URL goes into <link>
        SubElement(item, 'link').text = row.get('URL', '')

        # Description (HTML-wrapped in CDATA)
        body_copy = row.get('Body Copy', '')
        if body_copy:
            description_elem = SubElement(item, 'description')
            description_elem.text = f"<![CDATA[{body_copy}]]>"

        # Image pulled out into its own <image> element
        image_url = row.get('Image', '')
        if image_url:
            image_elem = SubElement(item, 'image')
            image_elem.text = image_url

        # CTA in its own tag
        cta_text = row.get('CTA', '')
        if cta_text:
            cta_elem = SubElement(item, 'cta')
            cta_elem.text = cta_text

        # Publish Date (MM/DD/YYYY)
        date_str = row.get('Publish Date', '')
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        SubElement(item, 'pubDate').text = pub_date

        # GUID (based on URL or title fallback)
        guid_val = row.get('URL', '').strip() or row.get('Title', 'No Title')
        guid = SubElement(item, 'guid')
        guid.text = guid_val
        guid.set('isPermaLink', 'false')

    return parseString(tostring(rss)).toprettyxml(indent="  ")

if __name__ == "__main__":
    csv_lines = fetch_csv()
    rss_content = build_rss(csv_lines)

    os.makedirs("docs", exist_ok=True)
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_content)
