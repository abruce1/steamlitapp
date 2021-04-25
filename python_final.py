# Project packages
# import wsb_reasoner --> this was causing and error so I removed it.
import streamlit as st
import datetime
import pandas_datareader as web
import pandas as pd
import numpy as np
import pytz as tz
import praw
from tqdm.notebook import tqdm


# Config streamlit page
st.set_page_config(
    page_title="Python Final Project",
    page_icon="💖",
    initial_sidebar_state="expanded",
    layout='wide'
)
# Funtion to load dataset
@st.cache
def load_data(filename):
    data = pd.read_csv(filename)
    data = data.set_index(pd.DatetimeIndex(data['Date'].values))
    data.drop('Date', axis=1, inplace=True)
    return data

# Sidebar
st.sidebar.header('Python Final Project')
sidebar_text = """Project created by:
Andres, Carolyne and Rory"""
st.sidebar.text(sidebar_text)
menu = ['PALANTIR', 'APPLE', "AMAZON", 'TESLA', 'MICROVISION']
st.sidebar.image(r'/Users/afb2019/PycharmProjects/pythonProject6/final/hot-stocks.jpeg', use_column_width='auto')
st.sidebar.header('Company Name')

choice = st.sidebar.selectbox('Select Company', menu)
start = st.sidebar.date_input("Select start date", datetime.date(2020, 3, 11))
end = st.sidebar.date_input("End  start date", datetime.date(2021, 4, 11))

# Page title
st.title('Stock Price')
about = """
We built this site using Python and streamlit with code we sourced and pieced togeather from the internet. 
In this section we pull current stock data from yahoo finance.
"""
st.code(about, language='')

# Import ticker data
if choice == 'PALANTIR':
    df = web.DataReader('PLTR','yahoo',start,end)
elif choice == 'APPLE':
    df = web.DataReader('AAPL','yahoo',start,end)
elif choice == 'AMAZON':
    df = web.DataReader('AMZN','yahoo',start,end)
elif choice == 'MICROVISION':
    df = web.DataReader('MVIS','yahoo', start, end)
else:
    df = web.DataReader('TSLA', 'yahoo', start, end)

# Filter df
df1 = df.loc[start:end, :]


# Plot Columns on graph
st.title('Plot Columns {}'.format(choice))
select_columns = df1.columns.tolist()
selection = st.selectbox('Select columns to Plot', select_columns)
new_df = df1[selection]
st.line_chart(new_df)

# Import data to table
st.write(df1)

# Display Simple Stats
st.title('Simple Stats')
select_columns = df1.columns.tolist()
selection = st.multiselect('Select View Stats', select_columns, default=['Close'])
new_df = df1[selection]
st.table(new_df.describe().T)
# Get the last time (to check for updates in the db)
#last_updated_utc = wsb_reasoner.get_last_upload_time() --> not working so I removed it

# Sentiment Analysis

# Reddit API key
reddit = praw.Reddit(client_id='2Cursa04i2lL3w',
                     client_secret='mytY_LbNGwHX4s22yw1LYpwtU--SAg',
                     user_agent='Training_Sandwich793')

# Search wall street bets for text
stop = False
limit = 100
# We first connected to Reddit's API, specifically to the Wallstreetbets channel. As the channel has different discussion
# boards we decided to focus in the 'what are your moves tomorrow' daily discussion.
mylist = []
search = reddit.subreddit('wallstreetbets').search("What Are Your Moves Tomorrow",limit=limit)
for submission in tqdm(search):
    mylist.append(submission)
print(len(mylist))

mylist =sorted(mylist,key=lambda x:x.created_utc,reverse=True)

# we aggregate the comments mentioning the ticker of choice
data = []
for submission in tqdm(mylist):
    morecomments = submission.comments
    try:
        for reply in morecomments:
            if 'choice' in reply.body.lower():
                data.append(reply)
    except:
        morecomments = reply
        pass
    if len(data) > 100:
        break

from datetime import datetime, timezone
x = datetime.now(timezone.utc)

sentiment_raw = []
for reply in data:
    pltr_index = reply.body.lower().find('choice')
    start = pltr_index - 100
    end = pltr_index + 100
    if start < 0:
        start = 0
    if end > len(reply.body):
        end = len(reply.body)
    # reply.body,reply.ups,reply.created_utc
    item = {
        'timestamp': datetime.fromtimestamp(reply.created_utc).astimezone(tz.timezone('US/Eastern')).date(),
        'reply': reply,
        'ups': reply.ups
    }
    if 'buy' in reply.body[start:end].lower():
        item['sentiment'] = 'buy'
    if 'sell' in reply.body[start:end].lower():
        item['sentiment'] = 'sell'

    if 'sentiment' in item.keys():
        sentiment_raw.append(item)

timestamp_list = sorted(np.unique([x['timestamp'] for x in sentiment_raw]))

sentiment_list = []
for timestamp in timestamp_list:
    sell = [x['ups'] for x in sentiment_raw if x['timestamp'] == timestamp and x['sentiment'] == 'sell']
    sell_count = np.sum(sell)

    buy = [x['ups'] for x in sentiment_raw if x['timestamp'] == timestamp and x['sentiment'] == 'buy']
    buy_count = np.sum(buy)

    item = dict(
        timestamp=timestamp,
        sell_count=sell_count,
        buy_count=buy_count,
        total_count=sell_count + buy_count,
    )
    sentiment_list.append(item)

wsbdf = pd.DataFrame(sentiment_list)
wsbdf.resetindexindex = wsbdf.timestamp
wsbdf['sentiment'] = wsbdf['sell_count'] / wsbdf['total_count']


# Chart of Sentiment Anlysis
st.title('Sentiment Analysis {}'.format(choice))
sentiment_expl = """
Buy counting the number of Buy/Sell words on the 'What are your moved tomorrow' discussion on Wallstreetbets, and 
comparing the results with the stock price, we want to provide useful information
to see if there is actually a relation between the number of buy/sell mentions 
and the price of a certain stock, and help users make more informed decisions.
"""
st.code(sentiment_expl, language='')

wsbdf =wsbdf.rename(columns={'timestamp':'index'}).set_index('index')
select_columns = wsbdf.columns.tolist()
selection = st.selectbox('Select columns to Plot', select_columns)
chart_data= wsbdf[selection]
st.line_chart(chart_data)





# Thank you
st.title('THANK YOU')
thankyou = """
We learned a lot while building this app. Thank you to Professor Nada, our TA and the world wide web for 
all the support this semester, we couldn't have done it without you all!
"""
st.code(thankyou, language='')