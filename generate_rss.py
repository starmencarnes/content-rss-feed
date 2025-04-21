import csv
import os
import requests
import mimetypes
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSE5yJ6z240_i34nXdBc1t-avF6Jct4YyeAhHcwyP-nzM4FPM_4h6_58SKsG1oaxXTUNvT-qD-Arh5X/pub?gid=0&single=true&output=csv"

def fetch_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    return response.text.splitlines()

def add_tracking_param(url, param_key='tracking_id', param_val='newsletter'):
    if not url:
        return ''
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs[param_key] = param_val
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def build_rss(csv_lines):
    reader = csv.DictReader(csv_lines)
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')

    SubElement(channel, 'title').text = "6AM City – National Content Feed"
    SubElement(channel, 'link').text = "https://starmencarnes.github.io/content-rss-feed/feed.xml"
    SubElement(channel, 'description').text = "RSS feed housing daily national ad copy designed for site ingestion"

    for row in reader:
        item = SubElement(channel, 'item')

        # Title
        SubElement(item, 'title').text = row.get('Title', 'No Title')

        # Add tracking param to URL
        raw_url = row.get('URL', '').strip()
        link_url = add_tracking_param(raw_url)
        SubElement(item, 'link').text = link_url

        # Body Copy + inline image for description
        body_copy = row.get('Body Copy', '')
        image_url = row.get('Image', '')

        description_parts = []
        if body_copy:
            description_parts.append(body_copy)
        if image_url:
            description_parts.append(f"<img src='{image_url}' alt='Ad' style='max-width:100%;' />")

        full_description = "\n".join(description_parts)
        SubElement(item, 'description').text = f"<![CDATA[{full_description}]]>"

        # CTA in its own tag
        cta_text = row.get('CTA', '')
        if cta_text:
            cta_elem = SubElement(item, 'cta')
            cta_elem.text = cta_text

        # Publish date parsing
        date_str = row.get('Publish Date', '')
        try:
            dt = datetime.strptime(date_str, '%m/%d/%Y')
            pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            dt = datetime.now()
            pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        SubElement(item, 'pubDate').text = pub_date

        # Enclosure for Sailthru compatibility
        if image_url:
            mime_type, _ = mimetypes.guess_type(image_url)
            mime_type = mime_type or "image/jpeg"
            enclosure = SubElement(item, 'enclosure')
            enclosure.set('url', image_url)
            enclosure.set('type', mime_type)

        # GUID (based on URL + publish date)
        date_part = dt.strftime('%Y-%m-%d')
        guid_val = f"{raw_url}-{date_part}"
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
