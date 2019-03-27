from flask import Flask, render_template, request, jsonify, json
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import requests
from pprint import pprint
import requests_cache
from datetime import datetime
from cassandra.cluster import Cluster
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from datetime import datetime, date, time, timedelta
from passlib.hash import sha256_crypt


requests_cache.install_cache('air_api_cache' , backend= 'sqlite' , expire_after=36000)

cluster = Cluster(['cassandra'])
session = cluster.connect()

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

#crime and google geolocation APIs access URIs
crime_url_template = 'https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={lng}&date={data}'
geolocation_url_template = 'https://maps.googleapis.com/maps/api/geocode/json?address={addressLocation}&key={API_KEY}'
categories_url_template = 'https://data.police.uk/api/crime-categories?date={date}'

#google API Geolocation api key
MY_API_KEY = app.config['MY_API_KEY']

@app.route('/', methods=['GET'])
def get_api_welcome():
    #welcome api message
    return jsonify(message='welcome to the crimes api! '), 200

#get student accomodation crimes details
@app.route('/records/<postcodeValue>', methods=['GET'])
@jwt_required
def get_crimes_details_by_address(postcodeValue):

    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()

    address = postcodeValue

    if not address:
        return jsonify(message='please provide the address details'), 400

    #gets the most recent date
    my_date = request.args.get('date','2019-01')

    #get the geolocation details by the address provided by the API client
    geolocation_url = geolocation_url_template.format(addressLocation = address, API_KEY=MY_API_KEY)

    #make a request to the google geolocation api
    resp = requests.get(geolocation_url)
    if resp.ok:
        jsonResponse = resp.json()
        latVal = jsonResponse['results'][0]['geometry']['location']['lat']
        lngVal = jsonResponse['results'][0]['geometry']['location']['lng']
    else:
        return "Address retreival failed!"

    #validate latitude and longitude values and call the crimes API
    if latVal and lngVal:
        crime_url = crime_url_template.format(lat = latVal, lng = lngVal, data = my_date)
    else:
        return "Address not found!"

    #make a call to the crimes API
    resp = requests.get(crime_url)
    if resp.ok:
        crimes = resp.json()
        pprint(crimes)

    resp = requests.get(categories_url_template.format(date = my_date))
    if resp.ok:
        categories_json = resp.json()
    else:
        print(resp.reasone)

    categories = {categ["url"]:categ["name"] for categ in categories_json}

    crime_category_stats = dict.fromkeys(categories.keys(), 0)
    crime_category_stats.pop("all-crime")

    for crime in crimes:
        crime_category_stats[crime["category"]] += 1

    # compute crime_outcome_stats
    crime_outcome_stats = {'None': 0}
    for crime in crimes:
        outcome = crime["outcome_status"]
        if not outcome:
            crime_outcome_stats['None'] += 1
        elif outcome['category'] not in crime_outcome_stats.keys():
            crime_outcome_stats.update({outcome['category']:1})
        else:
            crime_outcome_stats[outcome['category']] += 1

    graphs = [
            dict(
                data=[
                    dict(
                        values=list(crime_category_stats.values()),
                        labels=list(crime_category_stats.keys()),
                        hole=.4,
                        type='pie',
                        name='Category'
                    ),
                ],
                layout=dict(
                    title='Crime Categoty Stats During {}'.format(my_date)
                )
            ),
            dict(
                data=[
                    dict(
                        values=list(crime_outcome_stats.values()),
                        labels=list(crime_outcome_stats.keys()),
                        hole=.4,
                        type='pie',
                        name='Outcome'
                    ),
                ],
                layout=dict(
                    title='Crime Outcome Stats During {}'.format(my_date)
                )
            ),
        ]

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=PlotlyJSONEncoder)
    return render_template('plotholder.html',ids=ids,graphJSON=graphJSON)


@app.route('/createuser', methods=['POST'])
def create_a_user():

    #validates whether the right arguments have been provided
    if not request.json.get('username'):
        return jsonify({'error':'the new record needs to have a username'}), 400
    elif not request.json.get('password'):
        return jsonify({'error':'the new record needs to have a password'}), 400

    #if paremeters not empty assign them to variables
    username = request.json.get('username')
    password = request.json.get('password')

    enc_password = sha256_crypt.encrypt(password)

    #checks if the user with provided by the paremeter username already exists
    users = session.execute("""Select * From CrimeApp.Users where username = '{}'""".format(username))

    #if user already exists returns forbidden request as it cannot be done
    for user in users:
        return jsonify(message='this user already exists!'), 409

    #if user does not exist, insert the record to the database
    session.execute("""INSERT INTO CrimeApp.Users (username, password, usertype) VALUES ('{}', '{}', '{}')""".format(username, enc_password, 'R'))

    #system response to the successfull post request
    return jsonify(message='user {} has been successfully created!'.format(username)), 201

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    #checks whether the json message is in the right format
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    #gets username and password values from the request
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    #checks whether both password and username values have been provided
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    #searches for a specific user in the database
    users = session.execute("""Select * From CrimeApp.Users where username = '{}'""".format(username))

    #if user exists create authentication token with preset expiration time
    for user in users:
        if not sha256_crypt.verify(password, user.password):
            return jsonify({"msg": "wrong password"}), 400
        #set authentication token expiration time
        expires = timedelta(minutes=10)
        #create token
        access_token = create_access_token(identity=username, expires_delta=expires)
        #return token
        return jsonify(access_token=access_token), 200

    #returns this message if the user has not been found in the database
    return jsonify(message='this user does not exist!'), 409


@app.route('/updatepassword', methods=['PUT'])
@jwt_required
def update_the_password():

    #identify logged in user
    current_user = get_jwt_identity()

    #if paremeters not empty assign them to variables
    password = request.json.get('password')

    #if paremeters not empty assign them to variables
    username = request.json.get('username')

    #check if password paremeter is empty
    if not password:
        return jsonify(message='please provide the value of a new password'), 400

    #check if user paremeter is empty
    if not username:
        return jsonify(message='please provide the name of the user'), 400

    #gets the user that tries to perfrom deletion operation to find out its role
    users = session.execute("""Select * From CrimeApp.Users where username = '{}'""".format(current_user))

    #iterate over any possibly found data in the database
    for user in users:
        #for the purpose of the security it double checks whether the user to delete is correct
        if user.usertype != 'A' and username != current_user:
            return jsonify(message='provided username is not correct'), 400

    #encrypt new value for the password
    enc_password = sha256_crypt.encrypt(password)

    #updates the value of a password in the database
    session.execute("""Update CrimeApp.Users SET password = '{}' where username = '{}'""".format(enc_password, username))

    #return the outcome of the message
    return jsonify(message='password has been successfully updated'), 200

@app.route('/deleteuser', methods=['DELETE'])
@jwt_required
def delete_a_user():

    #identify logged in user
    current_user = get_jwt_identity()

    #if paremeters not empty assign them to variables
    username = request.json.get('username')

    if not username:
        return jsonify(message='missing username parameter'), 400

    #gets the user that tries to perfrom deletion operation to find out its role
    users = session.execute("""Select * From CrimeApp.Users where username = '{}'""".format(current_user))

    for user in users:
        #for the purpose of the security it double checks whether the user to delete is correct
        if user.usertype != 'A' and username != current_user:
            return jsonify(message='provided username is not correct'), 400


    #deletes the user from the database
    session.execute("""DELETE from CrimeApp.Users where username = '{}'""".format(current_user))

    #deletes the user from the list of logged in users so the token cannot be reused

    #return the outcome of the message
    return jsonify(message='user has been successfully deleted'), 200


if __name__ == '__main__':
	app.run(debug=True)
