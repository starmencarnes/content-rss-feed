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
    SubElement(channel, 'title').text = 'My CSV RSS Feed'
    SubElement(channel, 'link').text = 'https://yourusername.github.io/csv-to-rss/feed.xml'
    SubElement(channel, 'description').text = 'Auto-generated RSS feed from a CSV'

    for row in reader:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = row.get('title', 'No Title')
        SubElement(item, 'link').text = row.get('link', '')
        SubElement(item, 'description').text = row.get('description', '')
        SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

    return parseString(tostring(rss)).toprettyxml(indent="  ")

if __name__ == "__main__":
    csv_lines = fetch_csv()
    rss_content = build_rss(csv_lines)

    os.makedirs('docs', exist_ok=True)
    with open('docs/feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_content)
