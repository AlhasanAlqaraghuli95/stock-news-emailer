import requests
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
VANTAGE_API_KEY = os.getenv('VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
PASS = os.getenv('PASS')

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Send news to the email address
def send_email(articles: list):
    my_email = EMAIL_FROM
    password = PASS

    connection = smtplib.SMTP('smtp.gmail.com')
    connection.starttls()
    connection.login(user = my_email, password=password)

    for article in articles:

        title = article['title']
        try:
            desc = article['description']
        except AttributeError:
            desc= 'empty'

        print(title)
        print(desc)
        try:
            connection.sendmail(
                from_addr=my_email, 
                to_addrs=EMAIL_TO,
                
                    msg = f"Subject: {title} \n\n {desc}")
        except UnicodeEncodeError:
                    pass
    connection.close()

# Retrieve top 3 news articles about this company
def get_news():
    news_response = requests.get(url = NEWS_ENDPOINT, params={'apiKey': NEWS_API_KEY,
                                                     'q': COMPANY_NAME,
                                                     'searchIn': 'title',
                                                     'pageSize': 4,
                                                     'page': 1})
    data = news_response.json()

    articles_raw = data['articles']

    articles = [{'title': article['title'], 'description': article['description'] } for article in articles_raw]

    send_email(articles)


# Get formatted date
def get_date(days: int):
    today = datetime.today()

    date = today - timedelta(days=days)
    date_format = date.strftime('%Y-%m-%d')

    return date_format

# Get the stock info
stock_response = requests.get(url = STOCK_ENDPOINT, params={"apikey": VANTAGE_API_KEY,
                                                      "symbol": STOCK,
                                                      "function": 'TIME_SERIES_DAILY'})

data = stock_response.json()
daily_data = data['Time Series (Daily)']

# This way we can say yesterday = daily_data_list[0] for example to get the data from yesterday
daily_data_list = [value for (key, value) in daily_data.items()]

# Get formatted date for yesterday andthe day before yesterday
day_last_week = get_date(1)
day_before_that = get_date(2)

# When the stock difference between yesterday and the day before is +-5%, then send the top 3 headlines about this company -
# to my email

first_closing = round(float(daily_data[day_last_week]['4. close']),2)
second_closing = round(float(daily_data[day_before_that]['4. close']),2)

diff = second_closing - first_closing

pct_diff = (diff / first_closing) * 100

if abs(pct_diff) >= 5:
    get_news()






