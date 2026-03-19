import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask
from curl_cffi import requests
from bs4 import BeautifulSoup

# Load environment variables from a .env file if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Target URL for 23 March 2026
URL = "https://in.bookmyshow.com/movies/silchar/dhurandhar-the-revenge/buytickets/ET00478890/20260323"

def send_alert_email():
    """ Sends an email alert if the tickets are available. """
    sender_email = os.environ.get("SENDER_EMAIL", "your_email@gmail.com")
    sender_password = os.environ.get("SENDER_PASSWORD", "your_app_password")
    receiver_email = os.environ.get("RECEIVER_EMAIL", "your_email@gmail.com")

    if sender_email == "your_email@gmail.com":
        print("Skipping email alert. Please configure SENDER_EMAIL, SENDER_PASSWORD, and RECEIVER_EMAIL.")
        return

    msg = MIMEText(f"Tickets for Dhurandhar The Revenge are now available for 23 March 2026!\n\nBook here: {URL}")
    msg['Subject'] = 'BookMyShow Ticket Alert!'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))

    try:
        # Connect to the configured SMTP server
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        # Note: You may need an App Password depending on your email provider
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/scrape')
def check_tickets():
    """ Endpoint to check ticket availability. Called by the cron-job. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        response = requests.get(URL, impersonate="chrome110", allow_redirects=True)
        print(f"Requested URL: {URL}")
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page Title: {soup.title.string.strip() if soup.title else 'None'}")
        
        if "access denied" in response.text.lower() or "just a moment" in response.text.lower():
            print("ALERT: BookMyShow served a Bot Protection Challenge Page!")
            
        # Extract the target date from the URL (e.g. '20260423')
        target_date = URL.rstrip('/').split('/')[-1]
        
        content = response.text.lower()
        if "buytickets" in response.url.lower():
            # If the page loads, we MUST verify that the requested date is actually available 
            # in the date picker. If BMS defaulted to "today", the target date link won't exist.
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # If tickets for the target date are actually available and selected,
            # BookMyShow will render showtimes. Every cinema listing has an href
            # containing both '/cinemas/' and the active date.
            # This is the most foolproof way to ignore disabled dates in the UI calendar.
            active_date_shows_found = False
            for a in soup.find_all('a', href=True):
                if target_date in a['href'] and '/cinemas/' in a['href']:
                    active_date_shows_found = True
                    break
                    
            if not active_date_shows_found:
                print(f"No shows found for {target_date} (page likely defaulted to another date).")
                return "Date not actively available yet.", 200

            if "currently there are no shows" in content or "no shows found" in content or "no shows" in content:
                print("No tickets available yet for this date.")
                return "No tickets available yet.", 200
            else:
                print("Tickets appear to be available for the requested date!")
                send_alert_email()
                return "Tickets available! Alert sent.", 200
        else:
            print("Redirected away from buytickets page. Tickets not available yet.")
            return "Redirected. Not available.", 200

    except Exception as e:
        print(f"Error checking tickets: {e}")
        return f"Error: {e}", 500

@app.route('/')
def ping():
    """ Simple endpoint to keep the server alive on Render. """
    return "Server is alive! Use the /scrape endpoint to trigger the ticket check.", 200

if __name__ == '__main__':
    # Bind to PORT if defined (Render sets this dynamically), otherwise default to 10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)