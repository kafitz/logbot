#!/usr/bin/env python
# Kyle Fitzsimmons, 2015
import smtplib
from email.mime.text import MIMEText

def send(config, message):
    address = config.email.address
    password = config.email.password
    server = smtplib.SMTP_SSL(config.email.server, config.email.port)
    server.login(address, password)
    
    msg = MIMEText(message['body'], 'plain')
    msg['Subject'] = message['subject']
    msg['From'] = address
    msg['To'] = address
    server.sendmail(address, address, msg.as_string())
