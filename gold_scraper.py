import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# Keywords that traditionally spell trouble/boost for Gold
BULLISH_KEYWORDS = ["miss", "lower than expected", "dropped", "fell", "weak", "cut", "recession"]
BEARISH_KEYWORDS = ["beat", "higher than expected", "rose", "hiked", "strong", "growth", "surge"]

def analyze_sentiment(title, description):
    """Simple keyword analysis for Gold direction based on USD strength."""
    text = (title + " " + description).lower()
    
    bullish_score = sum(1 for word in BULLISH_KEYWORDS if word in text)
    bearish_score = sum(1 for word in BEARISH_KEYWORDS if word in text)
    
    # Bad USD data = Bullish for XAUUSD; Good USD data = Bearish for XAUUSD
    if bullish_score > bearish_score:
        return "📈 BULLISH FOR GOLD (Weak USD data)"
    elif bearish_score > bullish_score:
        return "📉 BEARISH FOR GOLD (Strong USD data)"
    return "⚖️ NEUTRAL / UNCERTAIN"

def get_impact_emoji(impact_level):
    """Maps impact levels to your requested color codes using emojis."""
    impact = impact_level.lower()
    if "high" in impact or "red" in impact:
        return "🔴 RED ALERT (High Impact!)"
    elif "medium" in impact or "orange" in impact:
        return "🟠 ORANGE ALERT (Mediocre Impact)"
    else:
        return "🟡 YELLOW ALERT (Normal News)"

def scrape_forex_factory():
    """Scrapes Forex Factory's live calendar feed."""
    url = "https://www.forexfactory.com/ffcal_week_this.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        events = []
        
        for event in root.findall('event'):
            # We focus on USD events as they heavily impact XAUUSD
            if event.find('currency').text == 'USD':
                events.append({
                    'title': event.find('title').text,
                    'impact': event.find('impact').text,
                    'time': event.find('time').text,
                    'date': event.find('date').text
                })
        return events
    except Exception as e:
        print(f"Error scraping: {e}")
        return []

def send_telegram_alert(message):
    """Sends the formatted alert to your phone."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    print("Checking for high volatility triggers...")
    events = scrape_forex_factory()
    
    # For a real automated setup, filter by current time. 
    # Here we check the upcoming/recent events:
    for event in events:
        # Filter for high/medium impact to avoid spam
        if event['impact'] in ['High', 'Medium']:
            alert_color = get_impact_emoji(event['impact'])
            sentiment = analyze_sentiment(event['title'], "")
            
            msg = (
                f"{alert_color}\n"
                f"**Event:** {event['title']}\n"
                f"**Time:** {event['date']} {event['time']}\n"
                f"**Bias:** {sentiment}\n\n"
                f"⚠️ *Check if Grid Monster needs to be paused!*"
            )
            
            print(f"Sending alert for {event['title']}...")
            send_telegram_alert(msg)
            break # Remove break to blast all events found

if __name__ == "__main__":
    main()
