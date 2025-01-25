import csv
import json
import requests
from datetime import datetime
import argparse
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

class SponsorAnalytics:
    def __init__(self, data: List[Dict]):
        self.data = data
        
    def location_analytics(self) -> Dict:
        # Cities with highest number of sponsors
        city_counts = Counter(item['location'] for item in self.data if item['location'])
        top_cities = dict(sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # County-wise distribution
        county_counts = Counter(item['county'] for item in self.data if item['county'])
        top_counties = dict(sorted(county_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "top_cities": top_cities,
            "top_counties": top_counties,
            "total_locations": len(city_counts),
            "total_counties": len(county_counts)
        }
    
    def visa_route_analysis(self) -> Dict:
        # Distribution by visa type
        route_counts = Counter(item['route'] for item in self.data)
        
        # Companies offering multiple visa routes
        company_routes = defaultdict(set)
        for item in self.data:
            company_routes[item['companyName']].add(item['route'])
            
        multi_route_companies = {
            company: list(routes)
            for company, routes in company_routes.items()
            if len(routes) > 1
        }
        
        # Skilled Worker vs Temporary Worker ratio
        skilled_count = sum(1 for item in self.data if 'Skilled Worker' in item['route'])
        temporary_count = sum(1 for item in self.data if 'Temporary Worker' in item['route'])
        
        return {
            "route_distribution": dict(route_counts),
            "multi_route_companies": multi_route_companies,
            "skilled_temporary_ratio": {
                "skilled_worker": skilled_count,
                "temporary_worker": temporary_count,
                "ratio": skilled_count / temporary_count if temporary_count > 0 else "N/A"
            }
        }
    
    def company_insights(self) -> Dict:
        # Organizations by rating type
        rating_counts = Counter(item['typeRating'] for item in self.data)
        
        # Companies with multiple entries (potential multi-branch)
        company_frequency = Counter(item['companyName'] for item in self.data)
        multi_branch_companies = {
            company: count
            for company, count in company_frequency.items()
            if count > 1
        }
        
        return {
            "rating_distribution": dict(rating_counts),
            "multi_branch_companies": dict(sorted(multi_branch_companies.items(), 
                                                key=lambda x: x[1], 
                                                reverse=True)[:10])
        }

def csv_to_json(csv_url: str):
    data = []
    
    response = requests.get(csv_url)
    response.raise_for_status()
    
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.DictReader(csv_content.splitlines())
    
    for row in csv_reader:
        data.append({
            "companyName": row["Organisation Name"].strip(),
            "location": row["Town/City"].strip(),
            "county": row["County"].strip() if row["County"] else None,
            "typeRating": row["Type & Rating"].strip(),
            "route": row["Route"].strip()
        })
    
    # Generate analytics
    analytics = SponsorAnalytics(data)
    
    result = {
        "metadata": {
            "total_sponsors": len(data),
            "generated_at": datetime.now().isoformat(),
            "source_url": csv_url
        },
        "analytics": {
            "location_analytics": analytics.location_analytics(),
            "visa_route_analysis": analytics.visa_route_analysis(),
            "company_insights": analytics.company_insights()
        },
        "sponsors": data
    }
    
    # Create timestamped JSON file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_file_path = f'uk-sponsers/json/sponsors_{timestamp}.json'
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert CSV to JSON with analytics.')
    parser.add_argument('csv_url', type=str, help='URL of the CSV file to download and convert')
    args = parser.parse_args()
    
    csv_to_json(args.csv_url)