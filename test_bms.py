import urllib.request
import re
import sys

def check_bms(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            print(f"Status: {response.getcode()}")
            print(f"Final URL: {response.geturl()}")
            print(f"Contains target date 20260423 in text: {'20260423' in html}")
            
            # Print a snippet around the date if found, or around the active date container
            if '20260423' in html:
                idx = html.find('20260423')
                print("Snippet surrounding target date:")
                print(html[max(0, idx-50):idx+50])
            else:
                print("Target date 20260423 NOT found anywhere in HTML.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    url = "https://in.bookmyshow.com/movies/silchar/dhurandhar-the-revenge/buytickets/ET00478890/20260423"
    check_bms(url)
