import csv
import json
import requests
from datetime import datetime
import argparse

def csv_to_json(csv_url):
    data = []
    
    # Download the CSV file
    response = requests.get(csv_url)
    response.raise_for_status()  # Raise an error for bad responses

    # Read the CSV content
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.DictReader(csv_content.splitlines())
    
    for row in csv_reader:
        # Assuming the CSV headers are "Organisation Name", "Town/City", "County", "Type & Rating", "Route"
        data.append({
            "companyName": row["Organisation Name"].strip(),
            "location": row["Town/City"].strip(),
            "county": row["County"].strip() if row["County"] else None,
            "typeRating": row["Type & Rating"].strip(),
            "route": row["Route"].strip()
        })
    
    # Create a timestamped JSON file name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_file_path = f'sponsors_{timestamp}.json'
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert CSV to JSON.')
    parser.add_argument('csv_url', type=str, help='URL of the CSV file to download and convert')
    args = parser.parse_args()

    csv_to_json(args.csv_url)