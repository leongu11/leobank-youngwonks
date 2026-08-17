import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, session
from bson.objectid import ObjectId
import hashlib

app = Flask(__name__)

load_dotenv()
# Create a new client and connect to the server
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
uri = os.getenv('MONGODB_URI')

client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

loginroute = client.bigbankdb.bigbank

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        action = request.form.get("formsid")
        if action == "register":
            username = request.form.get("userans")
            password = request.form.get("passans")
            email = request.form.get("emailans")
            document = {}
            document["username"] = username

            # encoding passwords 
            encodepass = hashlib.new('sha256')
            encodepass.update(password.encode('utf-8'))
            result = encodepass.hexdigest()


            document["password"] = result

            # done
            document["email"] = email
            document["balance"] = 0
            loginroute.insert_one(document)
            return redirect('/')

        if action == "login":
            emailcheck = request.form.get("emailentry")
            passcheck = request.form.get("passtry")
            cursor = list(loginroute.find({}))
            for i in cursor:
                if i["email"] == emailcheck:
                    encodepass = hashlib.new('sha256')
                    encodepass.update(passcheck.encode('utf-8'))
                    result = encodepass.hexdigest()
                    if result == i["password"]:
                        session['email'] = i['email']
                        session['user'] = i['username']
                        session['balance'] = float(i['balance'])
                        print(session)
                        flash("logged in","alert")
                        return redirect('/home')
                        # return render_template('realhome.html',username=i["username"])                    
                    else:
                        flash('wrong password',"alert")
                else:
                    flash("create account first","alert")
            return redirect('/')
@app.route('/home',methods=["GET","POST"])
def home():
    if 'email' not in session:
        flash("login first reet","alert")
        return redirect('/')
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "withdrawl":
            withdrawlamount = request.form.get("withdrawlamount")
            spec = loginroute.find_one({"email":session["email"]})
            if spec["balance"]<float(withdrawlamount):
                flash("insufficient moneys","alert")
            else:
                loginroute.update_one({"email":session["email"]},
                {'$inc':{'balance': -float(withdrawlamount)}})
                flash("finished","alert")
                getDate = datetime.now()
                formatDate = getDate.strftime("%Y-%m-%d %H:%M:%S")
                flash("withdrew -$"+withdrawlamount+" at "+str(formatDate),"log")
        if action == "deposit":
            depositamount = request.form.get("depositamount")
            spec = loginroute.find_one({"email":session["email"]})
            loginroute.update_one({"email":session["email"]},
                                 {'$inc':{'balance': float(depositamount)}})
            
            flash("finished","alert")
            getDate = datetime.now()
            formatDate = getDate.strftime("%Y-%m-%d %H:%M:%S")
            flash("deposited $"+depositamount+" at "+str(formatDate),"log")

    fud = loginroute.find_one({'email': session['email']})
    if fud:
        session['balance'] = float(fud['balance'])
    return render_template('realhome.html')  

@app.route('/logout')
def logout():
    session.clear()
    flash('logout success',"alert")
    return redirect ('/')

if __name__ == '__main__':
    app.run(debug=True)
