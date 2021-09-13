import requests
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

zip_code = '11214'#input('Zipcode')

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
cursor.execute("CREATE TABLE IF NOT EXISTS webapplogin (full_name TEXT NOT NULL, username VARCHAR(25) UNIQUE NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL)")
conn.commit()
#cursor.execute('SELECT * FROM gym_df')
conn.close()


#instantiate flask module
app = Flask(__name__)
app.secret_key = 'replace later'

#Client ID
client_id = 'Cev8jNKeXB1tVYbl3wwIUw'

#define api key, endpoint and header for request to yelp API
api_key = 'Uwp9Zz4K0F4VfCus7U3GWbbKbik7sX4UOdA7r8ir2XONuRcg1natwEwxNsxfeshBwvzxuBDuKJMziT9JnkJhQU6Ez20FGer5h-CJiVJW35DIbXvgnLol6IJ2EW47YXYx'
end_point = 'https://api.yelp.com/v3/businesses/search'
resp_header = {'Authorization': 'bearer {}'.format(api_key)}

#define parameters
parameters = {'term':'gym',
                'limit':5,
                'radius':3200,
                'location':'{}'.format(zip_code),
                'sort_by':'rating',
                }

#make api call
response = requests.get(url=end_point, params=parameters, headers=resp_header)

#Change json into dict then to pandas dataframe
gym_dict = response.json()

#set columns we want to display
#gym_df = pd.DataFrame(columns=('Picture','Name','Location','Rating','Website Link','Phone#','distance(m)','business_id'))
gym_df = pd.DataFrame(columns=('Picture','Name','Location','Rating','Phone#'))

#unpack function
def unpacker(*args):
    global gym_df
    #unpack the json
    for unpac in gym_dict['businesses']:
        #only display street address
        unpac['location']['display_address'] = unpac['location']['display_address'][0]
        '''create dataset. This will result in a creation of a tuple, which then can to turned into a list and 
        then into a panda series which then can be appended onto the dataframe
        This function is so we can choose which specific information we want from yelp.
        '''
        #print(unpac)
        #data = unpac['image_url'],unpac['name'],unpac['location']['display_address'],
        #unpac['rating'],unpac['url'],unpac['phone'],unpac['distance'],unpac['id']
        data = unpac['image_url'],unpac['name'],unpac['location']['display_address'],unpac['rating'],unpac['phone']
        datalist = list(data)
        seriesly = pd.Series(datalist, index = gym_df.columns)
        gym_df = gym_df.append(seriesly, ignore_index=True)


#display df in terminal
display(gym_df)

#TODO:FLASK <--LOOK
#Flask: Displays SQL database on HTML
# @app.route("/history.html")
# def shistory():
#     cursor.execute("SELECT * FROM gym_df")
#     dfd = cursor.fetchall()
#     return render_template('history.html', data=dfd)

# #Flask: Upload top 5 results to page after button on HTML is clicked (POST request) 
# @app.route("/",methods=["POST"])
# def zipsub():
#     if request.method == "POST":
#         return render_template('/' column_names=gym_df.columns.values, row_data=list(gym_df.values.tolist()))

@app.route("/signup.html", methods=["GET","POST"])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #Check if username, password, and email POST requests exist in HTML form
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        fname = request.form['fullname']
        uname = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)
    
        cursor.execute('SELECT * FROM users WHERE username = ?', (uname,))
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
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (?,?,?,?)", (fname, uname, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')

if __name__ == '__main__':
    #instantiate unpacker function
    unpacker()

    #ORDER DATAFRAME BY RATING
    gym_df = gym_df.sort_values(by=['Rating'], ascending=False)
    #TODO: add timestamp

    #Create SQL engine using SQLAlchemy
    engine = create_engine('postgresql+psycopg2://postgres:1123@localhost:5432/yhistory')

    #pd to SQL for search history
    gym_df.to_sql("gym_df", engine, if_exists='append')

    #shistory()

    #TODO:Create post event


