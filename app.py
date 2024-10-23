from flask import Flask,render_template,request,url_for,session,redirect
import pytesseract
from PIL import Image
from flask_mysqldb import MySQL
import MySQLdb.cursors
app = Flask(__name__)
import pickle
import numpy as np
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
#connect to Xammp database
app.secret_key = 'a'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kavya'
mysql = MySQL(app)


#This is the homepage
@app.route('/')
def home():
    return render_template('Homepage.html')


#This is registration page for a user
@app.route('/Register',methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            print("user already exist")
            return render_template('Login.html')
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO register VALUES(NULL,% s,% s,% s)',(name,email,password))
        mysql.connection.commit()
        return redirect(url_for('login'))
    return render_template('Register.html')

#This is the login page
@app.route('/Login',methods=['GET','POST'])
def login():
    global user_id
    msg=' '
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM register WHERE email = % s AND password != % s', (email,password,))
        account2 = cursor.fetchone()
        cursor.execute('SELECT * FROM register WHERE email = % s AND password = % s', (email,password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True 
            session['user_id'] = account['user_id']
            id = account['user_id']
            session['email'] = account["email"]
            return redirect(url_for('Prediction'))
        elif account2:
            msg = "wrong password"
            return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    
        #return render_template('Homepage.html')
    return render_template('Login.html') 

#To upload the image as a data
# @app.route('/upload/',methods=['GET', 'POST'])
# def upload():
#     imagefile = request.files.get('imagefile', '') 
#     print('imagefile',imagefile)
#     img = Image.open(imagefile)
#     text = pytesseract.image_to_string(img)
#     return 'text'

#To make the predictions
#sc = pickle.load(open('sc.pkl', 'rb'))

model = pickle.load(open('model.pkl', 'rb'))
@app.route('/Prediction',methods=['GET','POST'])
def Prediction():
    loggedin = getLoginDetails()
    if loggedin == False:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tweet = request.form.get("tweet")
        tweet = [tweet,]
        print(tweet)
        prediction = model.predict(tweet)
        if(prediction == 0):
            value = 'age'
        elif(prediction == 1):
            value="ethnicity"
        elif(prediction == 2):
            value = 'gender'
        elif(prediction == 3):
            value = "not cyberbullying"
        elif(prediction == 4):
            value = "other cyberbullying"
        elif(prediction == 5):
            value = "religion"
        print(value)
        return render_template('Prediction.html',tweet=tweet,pred=value)
    return render_template('Prediction.html')

def getLoginDetails():
    cursor = mysql.connection.cursor()
    if 'email' not in session:
        loggedin = False
        name = ''
    else:
        loggedin = True
    return (loggedin)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True,port = 8080)