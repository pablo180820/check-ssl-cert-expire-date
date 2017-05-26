import socket
import ssl
import datetime
import requests

from config import *


date_fmt = r'%b %d %H:%M:%S %Y %Z'

# tg
def send_message(text):
    requests.post(CODEXBOT_NOTIFICATIONS, data={'message': text})

'''
Source link: https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
'''
def ssl_expiry_datetime(hostname):

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    # parse the string from the certificate into a Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], date_fmt)

def check_ssl_time_left(domain):
    cert_expire_at = ssl_expiry_datetime(domain)
    time_left = cert_expire_at - datetime.datetime.now()
    if time_left.days <= DAYS_LIMIT:
        send_message('‼️ SSL cert for {} has {}'.format(domain, days_left_to_format_string(time_left)))

def days_left_to_format_string(timedelta):
    return '{} day{} left'.format(timedelta.days,  ('s', '')[timedelta.days == 1])

for domain in DOMAINS:
    check_ssl_time_left(domain)