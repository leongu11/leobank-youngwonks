from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://leotnguyen11:Nguyen2941@cluster0.irck5fp.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#for backends
import datetime
from flask import Flask, render_template, request, redirect
from bson.objectid import ObjectId

app = Flask('notemanager')
contdb = client.myContactManager.myContacts

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        contacts = contdb.find()
        return render_template('index.html',contacts = contacts)
    if request.method == 'POST':
        document = {}
        document['name'] = request.form.get('name')
        document['number'] = request.form.get('number')
        contdb.insert_one(document)
        return redirect('/')

@app.route('/delete/<note_id>')
def delete(note_id):
    contdb.delete_one({'_id':ObjectId(note_id)})
    return redirect('/')

# newnote = ""
# @app.route('/edit/',methods=['POST'])
# def edit():
#     newnoteid = request.form.get('noteid')
#     newnote = request.form.get('updnote')
#     print("text: "+newnote,"id: "+newnoteid)
#     notedb.notes.update_many({'_id':ObjectId(newnoteid)},{'$set':{'note':newnote,'timestamp':str(datetime.datetime.now())}})
#     return redirect('/')

app.run(port=8000,debug=True)
