import requests
from bs4 import BeautifulSoup
import json

url = "https://in.bookmyshow.com/movies/silchar/dhurandhar-the-revenge/buytickets/ET00478890/20260323"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    # Save precisely to a file to inspect, or just print keys
    # Let's find the active date. Often it's in props.pageProps
    # We will just dump it to a file and grep for 20260320 and 20260323
    with open('next_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Saved next_data.json")

