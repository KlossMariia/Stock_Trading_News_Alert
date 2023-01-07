import requests
from datetime import datetime, timedelta
import html
from twilio.rest import Client
# Constants
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NEWS_API = "58f13d691eea4706a2a48499d28d307e"
STOCK_API = "UJPQQWEU96A4NAKL"

# Getting yesterday date
today = datetime.today()
YESTERDAY_DATE = str((today - timedelta(days=3)).date())
relative_change = 0
news_data = []
account_sid = "AC8384312a2a9d322e0e824dadd67cd134"
auth_token = 'a42bbbf720841be433d5b1f3a4413c5f'

# gets stock data by using API
def get_stock_data():
    global relative_change
    parameters = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": STOCK,
        "interval": "60min",
        "apikey": STOCK_API,
    }
    stock_data = requests.get(url="https://www.alphavantage.co/query?", params=parameters)
    stock_data = stock_data.json()

    # Deleting unneeded information from response's text
    keys = stock_data["Time Series (60min)"]
    keys = list(keys.items())[:17]
    for key in keys[1:16]:
        keys.remove(key)
    stock_data = dict(keys)
    stock_data = {key:value["4. close"] for (key,value) in stock_data.items()}
    # caclulating price change
    # x1 is stock price yesterday and x2 today (price at the time of stock closing)
    x1 = float(list(stock_data.values())[1])
    x2 = float(list(stock_data.values())[0])
    relative_change = round(((x2 - x1) / x1) * 100, 1)

# fun checks if today is not a weekend and if relative change is more than 5%
# if conditions are met, code will run
def run_program():
    global relative_change
    if datetime.now().weekday() > 4 and abs(relative_change) >= 5:
        return False
    else:
        return True

# This function gets the most popular news by key-word "tesla"
# API is used for searching
def get_news():
    global news_data
    parameters = {
        "q": "Tesla",
        "from": YESTERDAY_DATE,
        "sortBy": "popularity",
        "apiKey": NEWS_API,
    }
    # editing data
    news_data = requests.get(url='https://newsapi.org/v2/everything?', params=parameters)
    news_data = news_data.json()["articles"]
    news_data = news_data[:3]
    news_data = [{"title": html.unescape(item["title"]), "source": html.unescape(item["source"]["name"])} for item in news_data]


# This function sends SMS with stock relative change and most popular news
def send_SMS():
    # forming SMS text
    global news_data
    if relative_change > 0:
        stock_change_symbol = "🔺"
    else:
        stock_change_symbol = "🔻"
    SMS_text = f"""
    TSLA: {stock_change_symbol}{abs(relative_change)}
        ‼️HOT NEWS‼️
    Source: {news_data[0]["source"]}
    Title: {news_data[0]["title"]}
    
    Source: {news_data[1]["source"]}
    Title: {news_data[1]["title"]}
    
    Source: {news_data[2]["source"]}
    Title: {news_data[2]["title"]}
    """
    print(SMS_text)
    # Sending SMS
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body=SMS_text,
            from_='+19035056220',
            to='+40728469967'
        )
    print(message.status)

# Format pf SMS
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
get_stock_data()
if run_program():
    get_news()
    # send_SMS()
