import smtplib
import json
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from time import sleep
import requests
from email.message import EmailMessage

Gateways = {
    'President\'s Choice': 'txt.bell.ca',
    '3 River Wireless': 'sms.3rivers.net',
    'ACS Wireless': 'paging.acswireless.com',
    'AT&T': 'txt.att.net',
    'Alltel': 'message.alltel.com',
    'BPL Mobile': 'bplmobile.com',
    'Bell Canada': 'txt.bellmobility.ca',
    'Bell Mobility (Canada)': 'txt.bell.ca',
    'Bell Mobility': 'txt.bellmobility.ca',
    'Blue Sky Frog': 'blueskyfrog.com',
    'Bluegrass Cellular': 'sms.bluecell.com',
    'Boost Mobile': 'myboostmobile.com',
    'Cellular One': 'mobile.celloneusa.com',
    'Cellular South': 'csouth1.com',
    'Centennial Wireless': 'cwemail.com',
    'CenturyTel': 'messaging.centurytel.net',
    'Chennai RPG Cellular': 'rpgmail.net',
    'Chennai Skycell / Airtel': 'airtelchennai.com',
    'Cingular': 'txt.att.net',
    'Clearnet': 'msg.clearnet.com',
    'Comcast': 'comcastpcs.textmsg.com',
    'Comviq': 'sms.comviq.se',
    'Corr Wireless Communications': 'corrwireless.net',
    'DT T-Mobile': 't-mobile-sms.de',
    'Delhi Aritel': 'airtelmail.com',
    'Delhi Hutch': 'delhi.hutch.co.in',
    'Dobson': 'mobile.dobson.net',
    'Dutchtone / Orange-NL': 'sms.orange.nl',
    'EMT': 'sms.emt.ee',
    'Edge Wireless': 'sms.edgewireless.com',
    'Escotel': 'escotelmobile.com',
    'Fido': 'fido.ca',
    'German T-Mobile': 't-mobile-sms.de',
    'Goa BPLMobil': 'bplmobile.com',
    'Golden Telecom': 'sms.goldentele.com',
    'Gujarat Celforce': 'celforce.com',
    'Helio': 'messaging.sprintpcs.com',
    'Houston Cellular': 'text.houstoncellular.net',
    'Idea Cellular': 'ideacellular.net',
    'Illinois Valley Cellular': 'ivctext.com',
    'Inland Cellular Telephone': 'inlandlink.com',
    'JSM Tele-Page': 'pinjsmtel.com',
    'Kerala Escotel': 'escotelmobile.com',
    'Kolkata Airtel': 'airtelkol.com',
    'Kyivstar': 'smsmail.lmt.lv',
    'LMT': 'smsmail.lmt.lv',
    'MCI': 'pagemci.com',
    'MTS': 'text.mtsmobility.com',
    'Maharashtra BPL Mobile': 'bplmobile.com',
    'Maharashtra Idea Cellular': 'ideacellular.net',
    'Manitoba Telecom Systems': 'text.mtsmobility.com',
    'Meteor': 'mymeteor.ie',
    'Metro PCS': 'mymetropcs.com',
    'MiWorld': 'm1.com.sg',
    'Microcell': 'fido.ca',
    'Midwest Wireless': 'clearlydigital.com',
    'Mobilcomm': 'mobilecomm.net',
    'Mobileone': 'm1.com.sg',
    'Mobilfone': 'page.mobilfone.com',
    'Mobility Bermuda': 'ml.bm',
    'Mobistar Belgium': 'mobistar.be',
    'Mobitel Tanzania': 'sms.co.tz',
    'Mobtel Srbija': 'mobtel.co.yu',
    'Movistar': 'correo.movistar.net',
    'Mumbai BPL Mobile': 'bplmobile.com',
    'Netcom': 'sms.netcom.no',
    'Nextel': 'messaging.nextel.com',
    'Ntelos': 'pcs.ntelos.com',
    'O2 (M-mail)': 'mmail.co.uk',
    'O2': 'o2imail.co.uk',
    'One Connect Austria': 'onemail.at',
    'OnlineBeep': 'onlinebeep.net',
    'Optus Mobile': 'optusmobile.com.au',
    'Orange Mumbai': 'orangemail.co.in',
    'Orange NL / Dutchtone': 'sms.orange.nl',
    'Orange': 'orange.net',
    'Oskar': 'mujoskar.cz',
    'P&T Luxembourg': 'sms.luxgsm.lu',
    'PCS One': 'pcsone.net',
    'Pondicherry BPL Mobile': 'bplmobile.com',
    'Primtel': 'sms.primtel.ru',
    'Project Fi': 'msg.fi.google.com',
    'Public Service Cellular': 'sms.pscel.com',
    'Qwest': 'qwestmp.com',
    'Rogers AT&T Wireless': 'pcs.rogers.com',
    'Rogers Canada': 'pcs.rogers.com',
    'SCS-900': 'scs-900.ru',
    'SFR France': 'sfr.fr',
    'Safaricom': 'safaricomsms.com',
    'Satelindo GSM': 'satelindogsm.com',
    'Simple Freedom': 'text.simplefreedom.net',
    'Smart Telecom': 'mysmart.mymobile.ph',
    'Solo Mobile': 'txt.bell.ca',
    'Southern LINC': 'page.southernlinc.com',
    'Southwestern Bell': 'email.swbw.com',
    'Sprint': 'messaging.sprintpcs.com',
    'Sumcom': 'tms.suncom.com',
    'Sunrise Mobile': 'mysunrise.ch',
    'Surewest Communicaitons': 'mobile.surewest.com',
    'Surewest Communications': 'freesurf.ch',
    'Swisscom': 'bluewin.ch',
    'T-Mobile Austria': 'sms.t-mobile.at',
    'T-Mobile Germany': 't-d1-sms.de',
    'T-Mobile UK': 't-mobile.uk.net',
    'T-Mobile': 'tmomail.net',
    'TIM': 'timnet.com',
    'Tamil Nadu BPL Mobile': 'bplmobile.com',
    'Tele2 Latvia': 'sms.tele2.lv',
    'Telefonica Movistar': 'movistar.net',
    'Telenor': 'mobilpost.no',
    'Telia Denmark': 'gsm1800.telia.dk',
    'Telus': 'msg.telus.com',
    'Tracfone': 'txt.att.net',
    'Triton': 'tms.suncom.com',
    'UMC': 'sms.umc.com.ua',
    'US Cellular': 'email.uscc.net',
    'US West': 'uswestdatamail.com',
    'Unicel': 'utext.com',
    'Uraltel': 'sms.uraltel.ru',
    'Uttar Pradesh Escotel': 'escotelmobile.com',
    'Verizon': 'vtext.com',
    'Virgin Mobile Canada': 'vmobile.ca',
    'Virgin Mobile': 'vmobl.com',
    'Vodafone Italy': 'sms.vodafone.it',
    'Vodafone Japan': 'c.vodafone.ne.jp',
    'Vodafone UK': 'vodafone.net',
    'West Central Wireless': 'sms.wcc.net',
    'Western Wireless': 'cellularonewest.com',
    'Wyndtell': 'wyndtell.com'
}


with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catfacts.db'
db = SQLAlchemy(app)

def call_at_interval(period, callback, args):
    while True:
        sleep(period)
        callback(*args)

def setInterval(period, callback, *args):
    Thread(target=call_at_interval, args=(period, callback, args)).start()

class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    phone = db.Column(db.String(100))
    network = db.Column(db.String(100))
    name = db.Column(db.String(100))

db.create_all()


 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("thesmscatfacts@gmail.com", config["password"])
msg = EmailMessage()
msg['From'] = "thesmscatfacts@gmail.com"

def send(message, tosend):
    msg.set_content(message)
    msg['To'] = tosend
    server.send_message(msg)



def firstMsg(num, name, network):
    u = Users.query.filter_by(phone=num)
    message = "Hey {}! An anonymous friend signed you up for daily CatFacts! Every day you will recieve interesting cat related facts!"
    email = num+"@"+Gateways[network]
    send(message, email)
    send("If you would like to unsubscribe, please visit this link: http://catfacts.jackmerrill.com/stop/{}".format(num), email)

def dailymsg(phone, network):
    fact = requests.get("https://catfact.ninja/fact")
    fact = fact.json()
    message = "Your daily catfact is here! FACT: {}".format(fact["fact"])
    num = phone+"@"+network
    send(message, num)


def iterate():
    for user in Users.query.all():
        dailymsg(user.phone, user.network)



# setInterval(86400, iterate)

setInterval(10, iterate)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        phone = request.form.get("phone")
        network = request.form.get("network")
        name = request.form.get("name")
        tocommit = Users(id=len(Users.query.all())+1, phone=phone, network=network, name=name)
        db.session.add(tocommit)
        db.session.commit()
        
        firstMsg(phone, name, network)
        return redirect("/")
    return render_template("signup.html", networks=Gateways)

@app.route("/stop/<phone>")
def stop(phone):
    todelete = Users.query.filter_by(phone=phone)
    db.session.delete(todelete)
    db.session.commit()
    return render_template("stop.html", msg="Success!")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80", debug=True)


