import smtplib
import pickle
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage

def email_sender(receiver, subject,content):
    with open('data.pickle','rb') as fr:
        ps = pickle.load(fr)
    sender = 'email-test@naver.com'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content(content)

    naver_server = smtplib.SMTP('smtp.naver.com',587)
    naver_server.ehlo()
    naver_server.starttls()
    naver_server.login('email-test@naver.com',ps)
    naver_server.send_message(msg)
    naver_server.quit()
