from flask import Flask, render_template, session, redirect,request
from functools import wraps
from psutil import users
import pymongo
import user.models as um
import ocr
import os
from PIL import Image
import requests

from utils.general import methods

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system


# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Routes
@app.route('/user/signup', methods=['POST'])
def signup():
  return um.User().signup()

@app.route('/user/signout')
def signout():
  return um.User().signout()

@app.route('/user/login', methods=['POST'])
def login():
  print(db.inserted_id)
  return um.User().login()

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/dashboard/', methods=['GET'])
@login_required
def dashboard():
  harga = session['user']['harga']
  diskon = session['user']['hargadisc']
  total = sum(harga) - sum(diskon)
  return render_template('dashboard.html', total=total)

@app.route('/dashboard/cek', methods=['GET'])
def cek():
  return session['user']['_id']

@app.route('/dashboard/upload', methods=['POST'])
def upload():
  try:
    csvfile = request.files["file"]
    img = Image.open(csvfile)
    img.save("data/images/zzzz.jpg")
    return render_template('dashboard.html', messege_info="upload berhasil")
  except:
    return render_template('dashboard.html', messege_info="Anda belum memasukan struk")


@app.route('/dashboard/scan', methods=['GET'])
def scans():
  try:
    id = session['user']['_id']
    konek = ocr.connect()
    semua = ocr.diskon1(konek)

    db.users.update_one(
        {"_id":id},
        {'$push':{"produk" : {'$each' : semua[0]}}})
    db.users.update_one(
        {"_id":id},
        {'$push':{"hargadisc" : {'$each' : semua[1]}}})
    db.users.update_one(
        {"_id":id},
        {'$push':{"harga" : {'$each' : semua[2]}}})
    
    harga = session['user']['harga']
    diskon = session['user']['hargadisc']
    total = sum(harga) - sum(diskon)
    os.remove("data/images/zzzz.jpg")
    pesan = "berhasil"
    #return pesan
    return render_template('dashboard.html', messege_info=pesan, total=total)
  except:
    harga = session['user']['harga']
    diskon = session['user']['hargadisc']
    total = sum(harga) - sum(diskon)
    pesan = "Tidak ada struk, mohon upload struk terlebih dahulu"
    return render_template('dashboard.html', messege_info=pesan, total=total)



if __name__ == "__main__":
    app.run(port=80, debug=True)