import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def scrape_investing_calendar():
    """Scrape Investing.com Economic Calendar"""
    
    # URL for Investing.com economic calendar
    url = "https://www.investing.com/economic-calendar/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all event rows
            events = []
            rows = soup.find_all('tr', {'class': 'js-event-item'})
            
            print(f"\nFound {len(rows)} event rows\n")
            
            for row in rows[:10]:  # Test first 10
                try:
                    # Get event ID
                    event_id = row.get('data-event-id', '')
                    
                    # Get time
                    time_elem = row.find('td', {'class': 'time'})
                    time_str = time_elem.text.strip() if time_elem else ''
                    
                    # Get country
                    country_elem = row.find('td', {'class': 'flagCur'})
                    country = country_elem.find('span', {'class': 'ceFlags'}).get('title', '') if country_elem else ''
                    
                    # Get impact
                    impact_elem = row.find('td', {'class': 'sentiment'})
                    impact_class = impact_elem.get('class', []) if impact_elem else []
                    if 'redFont' in impact_class or 'sentiment sentiment--bearish' in str(impact_class):
                        impact = 'High'
                    elif 'yellowFont' in impact_class or 'sentiment sentiment--neutral' in str(impact_class):
                        impact = 'Medium'
                    else:
                        impact = 'Low'
                    
                    # Get event name
                    event_elem = row.find('td', {'class': 'event'})
                    event_name = event_elem.text.strip() if event_elem else ''
                    
                    # Get Actual value
                    actual_elem = row.find('td', {'class': 'act'})
                    actual = actual_elem.text.strip() if actual_elem else ''
                    
                    # Get Forecast value
                    forecast_elem = row.find('td', {'class': 'fore'})
                    forecast = forecast_elem.text.strip() if forecast_elem else ''
                    
                    # Get Previous value
                    previous_elem = row.find('td', {'class': 'prev'})
                    previous = previous_elem.text.strip() if previous_elem else ''
                    
                    event_data = {
                        'id': event_id,
                        'time': time_str,
                        'country': country,
                        'impact': impact,
                        'event': event_name,
                        'actual': actual,
                        'forecast': forecast,
                        'previous': previous
                    }
                    
                    events.append(event_data)
                    print(json.dumps(event_data, indent=2, ensure_ascii=False))
                    print('-' * 80)
                    
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
            
            return events
            
        else:
            print(f"Failed to fetch: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("Testing Investing.com Economic Calendar Scraper\n")
    events = scrape_investing_calendar()
    print(f"\n\nTotal events scraped: {len(events)}")
