import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import smtplib 
from email.message import EmailMessage
import yfinance as yahooFinance
from datetime import datetime, timedelta
import pytz
import sys


## Created by Kunisuke Ishigaki

'''
Stock Price Management Project

The purpose of this project is to understand price trend of a certain stock and set the price alert for the stock 
for the stock price management. 
The program is running into 2 parts. 
The first part will help to make a yearly stock pricing graph with 30/200 days moving average 
to understand what the current price level of the specfic stock.
The second part will help to set up the stock price alert for a specific stock. Once the stock price hits the price level, 
it will send out the email notification to the receiver.
'''


#============================= First part===================================== #


#-------change the below stock symbol for the stock level graph----------#

stock_tick_tracking = "NDQ.AX"

#----------------------------------------------------#


# download data from yahoofinance
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=1*365)).strftime("%Y-%m-%d")
df = yahooFinance.download(f'{stock_tick_tracking}', start=start_date, end=end_date)

# 200/30 days moving average - which we will use as an indication for buy/sell
long_MA = 200
short_MA = 30

# add support data
def moving_average(data, long_MA, short_MA):
    df['long_MA'] = df['Close'].rolling(window=long_MA, min_periods=1).mean()
    df['short_MA'] = df['Close'].rolling(window=short_MA, min_periods=1).mean()
    return df

moving_average(df, long_MA, short_MA)

# plot setting
ax = df.plot(y='Close', color='blue', ls='-', figsize=(10, 6), ylabel='Price (A$)')

# time format
date_fmt = '%m-%Y'
months = mdates.MonthLocator()   # every month in a year
monthsFmt = mdates.DateFormatter(date_fmt)

# x-axis time interval and xlabel name
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
ax.set_xlabel("Time")

# plot line format
ax.plot(df.index, df['long_MA'],color='red', ls='--', label='long_MA')
ax.plot(df.index, df['short_MA'],color='orange', ls='--', label='short_MA')

# plot legend position setting
line_2, label_2 = ax.get_legend_handles_labels()
ax.legend(line_2, label_2, loc='upper left')

# graph title and show graph
plt.title("Stock Level Chart")
plt.setp(ax.get_xticklabels(), ha="center")
plt.show() # make sure to close the graph to trigger the second part




#============================= Second part===================================== #
global scrapping_count
scrapping_count = 0
price_trigger_flag = False


# Notification email sending and reciving account and password
#----------------------------------------------#
sender_email = "sender@gmail.com"                  # change the email to the sender's email account
recv_email = "receiever@gmail.com"                 # change the email to the receiever's email account
gmail_password = "mmmm uuuu ffff tttt"             # change the sender's gmail password key
#----------------------------------------------#
# Reference for setting up gmail_password: https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp

msg = EmailMessage()
msg['Subject'] = "[Notification] Stock Target Purchase Level Reached"
msg['From'] = sender_email
msg['To'] = recv_email


#-----Stock Symbol and Its Alert Price Setting-------#

stock_symbol_one = "NDQ.AX"
stock_alert_price_one = 41.4

#----------------------------------------------------#



while not price_trigger_flag:

# ------------------------------------ Stock #1------------------------------------------------------------#
    getInformation = yahooFinance.Ticker(f'{stock_symbol_one}')

    stock_info_dict = getInformation.info
    # stock_info_dict has all the info stored for the stock as dict

    # the time that we scrapped this stock info
    currentitme_aus = datetime.now(pytz.timezone("Australia/Sydney"))
    currentitme_aus_format = currentitme_aus.strftime("%Y:%m:%d %H:%M:%S %Z %z")
    print(f"Current time: {currentitme_aus_format}")
    print()

    current_buy_price = stock_alert_price_one  # check the alert price setting to see the current buy price

    target_buy_price = round(current_buy_price * 0.95, 2) # we assume if the current price is 5% below my current buy price we will get the program to notify us

    name_of_the_stock = stock_info_dict['symbol']
    print(f"Stock symbol: {name_of_the_stock}")
    print()

    current_price_of_the_stock = stock_info_dict["bid"]
    print(f"Current price: {current_price_of_the_stock}")
    print()

    print(f"Target buy price: {target_buy_price}")
    print()


    # the target buy price is above the current price of the stock meaning the price of stock is lower than we expected
    if target_buy_price > int(current_price_of_the_stock):
        print(f"Yes, the stock price for {name_of_the_stock} is currently lower than what we set.")
        print()

        msg.set_content(f"The stock {name_of_the_stock} has hit the target buy price at {target_buy_price}! The current stock price is at {current_price_of_the_stock}.")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(sender_email, gmail_password)
        print("Logining to the email account is successful.")
        print()

        server.send_message(msg)
        print("Email notification is sent!")
        print()

        server.quit()
        price_trigger_flag = True # this will stop the while loop after checking all stocks in this program

    scrapping_count += 1
    print(f"Scrapping count: {scrapping_count}")
    print("===========================================")
    time.sleep(30) # give interval of 30 sec between each yfinance scraping to avoid rate limit/blacklisted

    if currentitme_aus_format[11:13] == "17":
        sys.exit() # if the current aus time is 17:00 or later, we close this program. 
                   # if the program is started after 18:00, this program will continue running to serve the purpose of debugging/updating the program. 
