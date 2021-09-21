import requests as reqs
import yelpapi
import pandas as pd
from IPython.display import display
from flask import Flask, request, session, url_for, render_template, flash, redirect
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
import re
import json
import sys

#TODO: DEVELOP LOGIN SYSTEM
#Create SQL connection using psycopg2
"""Connect to POSTGRESQL"""
conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="1123",
    host='localhost',
    port='5432')
cursor = conn.cursor()
#Create cursor object using built in cursor() method
cursor.execute("CREATE TABLE IF NOT EXISTS webapplogin (full_name VARCHAR ( 250 ) NOT NULL, username VARCHAR( 200 ) UNIQUE NOT NULL, password VARCHAR( 250 ) NOT NULL, email VARCHAR ( 200 ) NOT NULL)")
# conn.commit()
# conn.close()
# class weblogin(db.Model):
#     """User account model."""
#     __tablename__ = 'webapplogin'
#     id = db.Column(
#         db.Integer,
#         primary_key=True
#     )
#     full_name = db.Column(
#         db.String(100),
#         nullable=False,
#         unique=False
#     )
#     username = db.Column(
#         db.String(150)
#         nullable=False,
#         unique=True
#         )
#     )
#     email = db.Column(
#         db.String(40)
#     )
#     password = db.Column(
#         db.String(200),
#         primary_key=False,
#         unique=False,
#         nullable=False
#     )
    

#cursor.execute('SELECT * FROM gym_df')
gym_df = pd.DataFrame(columns=('Picture','Name','Location','Rating','Phone#'))
histore = pd.DataFrame(columns=('Picture','Name','Location','Rating','Phone#'))
#instantiate flask module
app = Flask(__name__, template_folder='C:\\Users\\derek\\PycharmProjects\\pythonProject1\\gyms-near-you-master\\gyms-near-you\\templates',
                        static_folder='C:\\Users\\derek\\PycharmProjects\\pythonProject1\\gyms-near-you-master\\gyms-near-you\\static')
app.secret_key = 'a1a1s2d3d3f4g5g5gdfc4trby65ASED#EWf4tserfd3R#DFSF43sfdr$#FF'

#app.route

#TODO:FLASK <--LOOK
#Navigation
@app.route("/") 
def index():
    return render_template("index.html")

@app.route("/signup",methods=["GET"])
def signav():
    return render_template('signup.html')

@app.route("/signin",methods=["GET"])
def signinav():
    return render_template('signin.html')

@app.route("/about",methods=["GET"])
def aboutus():
    return render_template('about.html')

@app.route("/table",methods=["GET"])
def totable():
    return render_template('table.html')

#Flask: Displays SQL database on HTML
@app.route("/history",methods=["GET","POST"])
def shistory():
    global histore   
    dfd =  pd.read_sql_query('''SELECT * FROM gym_df''', conn)
    histore = histore.append(dfd, ignore_index=True)
    if histore is histore:
        return redirect(url_for('history.html'))
    # #TODO:Set column names and pass tuples through as list of rows
    return render_template('history.html', column_names=histore.columns.values, row_data=list(histore.values.tolist()), zip=zip)

# #Flask: Upload top 5 results from df to page after button on HTML is clicked (POST request) 
@app.route("/",methods=["POST", "GET"])
def zipsub():
    global gym_df
    if request.method == "POST":
        zip_code = request.form.get('zipsearch')
        #Client ID
        clientid = 'Cev8jNKeXB1tVYbl3wwIUw'
        #define api key, endpoint and header for request to yelp API
        api_key = 'Uwp9Zz4K0F4VfCus7U3GWbbKbik7sX4UOdA7r8ir2XONuRcg1natwEwxNsxfeshBwvzxuBDuKJMziT9JnkJhQU6Ez20FGer5h-CJiVJW35DIbXvgnLol6IJ2EW47YXYx'
        end_point = 'https://api.yelp.com/v3/businesses/search'
        resp_header = {'Authorization': 'bearer {}'.format(api_key)}
        
        #define parameters
        parameters = {'term':'gym',
                        'limit':5,
                        'radius':3200,
                        'location':'{}'.format(zip_code),
                        'sort-by':'rating'
                        }
        #make api call
        response = reqs.get(url=end_point, params=parameters, headers=resp_header)

        #Change json into dict then to pandas dataframe
        gym_dict = response.json()

        #unpack the json
        for valg in gym_dict['businesses']:
            #only display street address
            valg['location']['display_address'] = valg['location']['display_address'][0]
            '''create dataset. This will result in a creation of a tuple, which then can turned into a list and 
            then into a panda series which then can be appended onto the dataframe.
            This function is so we can choose which specific information we want from yelp.
            '''
            data = valg['image_url'],valg['name'],valg['location']['display_address'],valg['rating'],valg['phone']
            datalist = list(data)
            seriesly = pd.Series(datalist, index = gym_df.columns)
            gym_df = gym_df.append(seriesly, ignore_index=True)
            #print(gym_df, file=sys.stdout)

        gym_df.to_sql("gym_df", engine, if_exists='replace')

            #ORDER DATAFRAME BY RATING
        gym_df = gym_df.sort_values(by=['Rating'], ascending=False)
                
    return render_template('table.html', column_names=gym_df.columns.values, row_data=list(gym_df.values.tolist()), zip=zip)
    #, tables=[gym_df.to_html(table_id='my_table')])
   
@app.route('/signin', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        uname = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM webapplogin WHERE username = %s', (uname,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('/index.html'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('/index.html')

#Flask script for registration page.
@app.route("/signup", methods=["GET","POST"])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #Check if username, password, and email POST requests exist in HTML form
    if request.method == 'POST' and 'fullname' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        fname = request.form['fullname']
        uname = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #hash password before sending to db
        _hashed_password = generate_password_hash(password)
    
        cursor.execute('SELECT * FROM webapplogin WHERE username = %s', (uname,))
        account = cursor.fetchone()
        print(account)

        #if account exists show error and validation check
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', uname):
            flash('Username must contain only characters and numbers!')
        elif not uname or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO webapplogin (full_name, username, password, email) VALUES (%s,%s,%s,%s)", (fname, uname, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('signup.html')


if __name__ == '__main__':
    #TODO: add timestamp
    #Create SQL engine using SQLAlchemy
    engine = create_engine('postgresql+psycopg2://postgres:1123@localhost:5432/postgres')

    #run flask
    app.debug=True
    app.run(threaded=True)
    #instantiate unpackker function
    #pd to SQL for search history
    cursor.close()
    #TODO:Create post event

