import time, smtplib, sys, creds, gspread, pytz
import tkinter as tk
#from gsheet_plotter import GSheetPlotter
from string import ascii_lowercase
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import cryptocompare as cp
from email.message import EmailMessage

auth_key = creds.auth_key
cp.cryptocompare._set_api_key_parameter(auth_key)
scope =["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds_gspread = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds_gspread)
tz_PST = pytz.timezone('America/Los_Angeles')
lists_of_sheets = []
for spreadsheet in client.openall():
  lists_of_sheets.append(str(spreadsheet.title))

def addToSpreadsheet(price, coin):
    if str(coin) not in lists_of_sheets:
      new_worksheet = client.create(str(coin))
      new_worksheet.share('<personal_email_withheld>@gmail.com', perm_type='user', role='owner')
      lists_of_sheets.append(str(coin))  
    sheet = client.open(str(coin)).sheet1
    sheet.update_cell(1,1, 'Date')
    sheet.update_cell(1,2, 'Time')
    sheet.update_cell(1,3, 'Coin')
    sheet.update_cell(1,4, 'Price')
    data = sheet.get_all_records()
    #Appends a row to the current google sheet, firstly getting current date, then time, then coin, then price
    sheet.append_row([str(datetime.today().date()), str((datetime.now(tz_PST).time()).strftime("%H:%M:%S")), coin, price])

def sendText(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = "<personal_email_withheld>@gmail.com"
    msg['from'] = user
    passwd = creds.gmail_passwd
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(user, passwd)
    s.send_message(msg)
    s.quit()

def getCryptoPrice(coins):
    finMsg = ""
    msg = cp.get_price(coins, currency='USD')
    for i in coins:
        val = msg[i]["USD"]
        finMsg += "Value of " + str(i) + ":\n$" + str(val) + "\n\n"
        addToSpreadsheet(msg[i]["USD"], i)
    return finMsg

"""if "-c" in sys.argv[1]:
    coins = sys.argv[2:]"""
coin_file = open('coins.txt', 'r')
coins = [coin.strip() for coin in coin_file.readlines()]


starttime = time.time()
#Personal Coin Watchlist: BTC BAT DOGE XMR
while True:
    msg = getCryptoPrice(coins)
    sendText("", msg, "<phone-number-withheld>@vtext.com")
    time.sleep(7200.0 - ((time.time() - starttime) % 7200.0))
