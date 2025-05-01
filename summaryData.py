import os
import xml.etree.ElementTree as ET
import csv

def process_xml_file(file_path):
    """
    Processes an XML file to compute average attributes in <step> elements.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    attributes = {}
    step_count = 0

    for step in root.findall('step'):
        step_count += 1
        for attr, value in step.attrib.items():
            if attr not in attributes:
                attributes[attr] = 0.0
            attributes[attr] += float(value)

    averages = {attr: value / step_count for attr, value in attributes.items()}
    averages["file_name"] = os.path.basename(file_path)
    return averages

def process_folder(folder_path, output_csv):
    """
    Processes XML files starting with 'summary' in the folder and writes the results to a CSV file.
    """
    rows = []
    column_headers = set()

    for file_name in os.listdir(folder_path):
        if file_name.startswith("summary") and file_name.endswith('.xml'):
            file_path = os.path.join(folder_path, file_name)
            row = process_xml_file(file_path)
            rows.append(row)
            column_headers.update(row.keys())

    # Ensure consistent column order
    column_headers = sorted(column_headers)

    # Write results to CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_headers)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    folder_path = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\CN75"  # Adjusted folder path
    output_csv = r"C:\Users\bobbi\Documents\YEAR 3\sumo3\results\CN75\outputCN75.csv"
    process_folder(folder_path, output_csv)
    print(f"Results written to {output_csv}")
