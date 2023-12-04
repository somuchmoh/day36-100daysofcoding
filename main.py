import requests
import os
from datetime import datetime, timedelta
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
stock_api_key = os.getenv("API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key
}

news_params = {
    "q": COMPANY_NAME,
    "apikey": news_api_key,
    "language": "en",
    "pageSize": 3,
}

today = datetime.now()
year = today.year
month = today.month
day = today.day
date_today = f"{year}-{month}-{"{:02d}".format(day)}"

if today.weekday() != 6 and today.weekday() != 0:
    yest_date = today - timedelta(days=1)
elif today.weekday() == 6:
    yest_date = today - timedelta(days=2)
elif today.weekday() == 0:
    yest_date = today - timedelta(days=3)

dby_date = f"{(yest_date-timedelta(days=1)).date()}"
yest_date = f"{yest_date.date()}"


# STEP 1: Use https://newsapi.org/docs/endpoints/everything
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# HINT 1: Get the closing price for yesterday and the day before yesterday.
# Find the positive difference between the two prices. e.g. 40 - 20 = -20, but the positive difference is 20.
# HINT 2: Work out the value of 5% of yesterday's closing stock price.
stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()
print(stock_data)
yest_closing = stock_data['Time Series (Daily)'][yest_date]['close']
dby_closing = stock_data['Time Series (Daily)'][dby_date]['close']
change_in_close = (yest_closing - dby_closing)/dby_closing

if change_in_close >= 0.05 or change_in_close <= -0.05:

    # STEP 2: Use https://newsapi.org/docs/endpoints/everything
    # Instead of printing ("Get News"), actually fetch the first 3 articles for the COMPANY_NAME.
    # HINT 1: Think about using the Python Slice Operator
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()


# STEP 3: Use twilio.com/docs/sms/quickstart/python
# Send a separate message with each article's title and description to your phone number. 
# HINT 1: Consider using a List Comprehension.
    client = Client(account_sid, auth_token)
    for article in range(0, len(news_data['articles'])):
        message = client.messages \
                    .create(body=f"{STOCK} \n Headline: {news_data['articles'][article]['title']}️ \n "
                                 f"Brief: {news_data['articles'][article]['description']}",
                            from_= os.getenv("TWILIO_FROM"),
                            to= os.getenv("TWILIO_TO"))
        print(message.status)


# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file
 by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the 
 coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file 
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the 
coronavirus market crash.
"""
