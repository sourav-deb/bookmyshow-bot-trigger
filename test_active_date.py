import requests
from bs4 import BeautifulSoup
import sys

url = "https://in.bookmyshow.com/movies/silchar/dhurandhar-the-revenge/buytickets/ET00478890/20260323"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

print("Fetching:", url)
print("Final URL:", r.url)

for a in soup.find_all('a', href=True):
    if '20260320' in a['href']:
        print("--- 20 ---")
        print(a.get('class', []))
        if a.parent:
            print(a.parent.get('class', []))
        if a.parent and a.parent.parent:
            print(a.parent.parent.get('class', []))

    if '20260323' in a['href']:
        print("--- 23 ---")
        print(a.get('class', []))
        if a.parent:
            print(a.parent.get('class', []))
        if a.parent and a.parent.parent:
            print(a.parent.parent.get('class', []))

