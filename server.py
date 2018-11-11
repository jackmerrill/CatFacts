import shawk
import json
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from time import sleep
import requests

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

user = "thesmscatfacts@gmail.com"
password = config["password"]
client = shawk.Client(user, password)



def firstMsg(num, name, network):
    u = Users.query.filter_by(phone=num)
    client.send("Hey {}! An anonymous friend signed you up for daily CatFacts! Every day you will recieve interesting cat related facts! *If you would like to unsubscribe, please visit this link: http://0.0.0.0/stop/{}".format(name, num), number=num, carrier=network) # replace link with domain

def dailymsg(phone, network):
    fact = requests.get("https://catfact.ninja/fact")
    fact = fact.json()
    u = Users.query.filter_by(phone=phone)
    client.send("Your daily catfact is here! FACT: {}".format(fact["fact"]), number=phone, carrier=network)


def iterate():
    for user in Users.query.all():
        dailymsg(user.phone, user.network)



setInterval(86400, iterate)

# setInterval(10, iterate)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        phone = int(request.form.get("phone"))
        network = request.form.get("network")
        name = request.form.get("name")
        tocommit = Users(id=len(Users.query.all())+1, phone=phone, network=network, name=name)
        db.session.add(tocommit)
        db.session.commit()
        client.add_contact(phone, network, name)
        firstMsg(phone, name, network)
        return redirect("/")
    return render_template("signup.html")

@app.route("/stop/<phone>")
def stop(phone):
    todelete = Users.query.filter_by(phone=phone)
    db.session.delete(todelete)
    db.session.commit()
    client.remove_contact(number=phone)
    return render_template("stop.html", msg="Success!")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80", debug=True)


