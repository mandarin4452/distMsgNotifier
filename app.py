from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from dateutil.parser import parse
from apscheduler.schedulers.background import BackgroundScheduler
from api_test import update_db as updating
from mail_sender import email_sender
import requests
import time
import atexit
import sqlite3
import datetime

def send_email():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('select * from clients')

    email_dict = dict()
    for row in cur:
        email_dict[row[1]] = row[0] # key = email, value = location
    for key, value in email_dict.items():
        cont = ""
        date = ""
        try:
            cur.execute("select * from message where location like ? limit 1",('%{}%'.format(value),))
            for row in cur:
                date = row[0]
                cont = row[2]
            subject = date + " 발송된 재난 문자입니다."
            email_sender(key,date,cont)
        except:
            continue
        



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

scheduler = BackgroundScheduler()
scheduler.add_job(send_email,'interval',minutes=60)
scheduler.start()





class Messages(db.Model):
    __tablename__ = "message"
    __table_agrs__ = { 'extend_existing' : True }
    date = db.Column(db.DateTime, primary_key = True)
    location = db.Column(db.Text, nullable = False)
    content = db.Column(db.Text, nullable = False)

class Clients(db.Model):
    __tablename__ = "clients"
    __table_agrs__ = { 'extend_existing' : True }
    location = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, primary_key = True)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    native = date.replace(tzinfo=None)
    format='%m-%d %H:%M'
    return native.strftime(format) 

@app.route('/',defaults = {"page":1})
@app.route('/page:<int:page>')
def index(page = 1):
    per_page = 10
    cont = Messages.query.order_by(Messages.date.desc()).paginate(page,per_page,False)
    
    return render_template(
        'index.html',
        cont_list = cont
    )

@app.route('/update')
def update():
    updating()
    return redirect('/')

@app.route('/mail', methods=['POST','GET'])
def mail_store():
    if request.method == 'POST':
        location = request.form['loc']
        email = request.form['email']
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        sql = 'insert into clients values (?,?)'
        cur.execute(sql,(location,email))
        conn.commit()
        return redirect('/')

app.run(host="0.0.0.0",port=5000)
atexit.register(lambda: scheduler.shutdown())