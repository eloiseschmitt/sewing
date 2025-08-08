import csv
import xml.etree.ElementTree as ET

csv_file = "couturiers.csv"
xml_file = "couturiers.xml"

root = ET.Element("root")

with open(csv_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        item = ET.SubElement(root, "row")
        for key, value in row.items():
            child = ET.SubElement(item, key)
            child.text = value

tree = ET.ElementTree(root)
tree.write(xml_file, encoding="utf-8", xml_declaration=True)
