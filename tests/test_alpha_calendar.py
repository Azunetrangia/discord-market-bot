import requests
import json
from datetime import datetime

api_key = 'CG1WM7WHSHL4T2EX'

# Test Economic Calendar endpoint
url = f'https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR&apikey={api_key}'
response = requests.get(url)
print('Status:', response.status_code)
print('\nResponse:')
data = response.json()

# Print first few events
if 'data' in data:
    print(f"Total events: {len(data['data'])}")
    print("\nFirst 3 events:")
    for event in data['data'][:3]:
        print(json.dumps(event, indent=2))
else:
    print(json.dumps(data, indent=2))
