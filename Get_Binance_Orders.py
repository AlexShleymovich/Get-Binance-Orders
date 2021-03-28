from binance.client import Client
import pandas as pd
from datetime import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from datetime import date
from email import encoders
import config


class BinanceOrders:

    # Initialization with the API key and secret key
    def __init__(self, key, secret):
        self.client = Client(api_key=key, api_secret=secret)
        self.assets = self.get_assets()
        self.orders = self.get_orders()
        self.get_data()

# Get all the assets with positive balance
    def get_assets(self):
        info = self.client.get_account()
        assets_list = info['balances']
        my_assets = []
        for asset in assets_list:
            if float(asset['free']) > 0:
                my_assets.append(asset['asset'])
        return my_assets

# Get all the orders that were made
    def get_orders(self):
        orders = []
        for i in self.assets:
            if i != 'USDT':
                orders_list = self.client.get_all_orders(symbol=i + 'USDT')
                for order in orders_list:
                    orders.append(order)
        return orders

# Create a customized DataFrame with required information, only for orders that were filled
    def get_data(self):
        DF = pd.DataFrame(columns=['Date', 'Asset', 'Type', 'Price', 'Amount', 'Fee', 'Total'])
        for x in range(len(self.orders)):
            if self.orders[x]['status'] == 'FILLED':
                Date = datetime.fromtimestamp(self.orders[x]['time'] / 1000.0).strftime('%d.%m.%Y %H:%M')
                Asset = str(self.orders[x]['symbol']).replace('USDT', '')
                Type = self.orders[x]['side']
                Price = round(float(self.orders[x]['cummulativeQuoteQty']) / float(self.orders[x]['executedQty']), 2)
                Amount = round(float(self.orders[x]['executedQty']), 3)
                Total = round(float(self.orders[x]['cummulativeQuoteQty']), 3)
                if self.orders[x]['time'] < 1613816037557:
                    Fee = Price * 0.001
                else:
                    Fee = Price * 0.00075
                Fee = round(Fee, 3)

                DF = DF.append(pd.Series([Date, Asset, Type, Price, Amount, Fee, Total], index=DF.columns), ignore_index=True)

        DF.to_csv('*PATH TO WHERE YOU WANT TO SAVE THE FILE*', index=False)


class SendEmail:
    date = date.today()

# Initialization with the sender's credentials and receiver's address
    def __init__(self, from_adr, to_adr, password):
        self.from_adr = from_adr
        self.to_adr = to_adr
        self.password = password
        self.send_mail()

# Combining the email with text format and attachment
    def init_message(self):
        msg = MIMEMultipart()
        msg["From"] = self.from_adr
        msg['To'] = self.to_adr
        msg['Subject'] = f"Report from Binance {date}"
        body = "\t\t\t****  See the attached file  ****"
        msg.attach(MIMEText(_text=body, _subtype='plain'))
        attachment = open('*PATH TO THE FILE*', 'rb')
        filename = '*FILENAME*'
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)
        text = msg.as_string()
        return text

# Sending the encrypted email 
    def send_mail(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('*YOUR EMAIL HOST*', port=465, context=context) as server:
            server.login(self.from_adr, password=self.password)
            server.sendmail(from_addr=self.from_adr, to_addrs=self.to_adr, msg=self.init_message())


if __name__ == '__main__':
    trades = BinanceOrders(config.API_Key, config.Secret_Key)
    mail = SendEmail('*FROM ADDRESS*', '*TO ADDRESS*', config.password)






