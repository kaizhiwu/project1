import os, requests, json

from flask import Flask, session, request, render_template, redirect, url_for, escape, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\ndsaksacjsac\asc]/'


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route('/')
def index():
    # detect if the user has logged in.
    #if logged in, show the success message.
    if 'username' in session:
        message = "Logged in as %s" % escape(session['username'])
        locations = db.execute("SELECT * FROM zip_codes").fetchall()
        return render_template("index.html", message = message, locations = locations)
    #if not logged in, let the user logged in.
    #return redirect(url_for('signin'))
    return render_template("signin.html")

@app.route('/signin', methods=['POST'])
def signin():
    # Get form information.
    username = request.form["username"]
    psw = request.form["psw"]
    # Check to see if the user exists.
    if db.execute("SELECT * FROM userlogins WHERE username = :username AND psw = :psw", {"username": username, "psw": psw}).rowcount == 1:
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template("error.html", message="Wrong password or user doesn't exist, try again")

@app.route('/signout')
def signout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template("register.html" )

@app.route('/signup', methods=['POST'])
def signup():
    #Get the registration information from form at the register page.
    username = request.form['username']
    psw = request.form['psw']

    # Save the data back into the database.
    db.execute("INSERT INTO userlogins (username, psw) VALUES (:x, :y)", {"x": username, "y": psw})
    db.commit()
    # display the success message,and log the user in
    session['username'] = username
    message = "You are registered as %s" % escape(session['username'])
    return render_template("index.html", message = message)

@app.route('/location', methods=['POST'])
def location():
    #get the user query information
    zipcode = request.form['zipcode']
    city = request.form['city']

    # search the database
    location = db.execute("SELECT * FROM zip_codes WHERE zipcode = :zipcode or city = :city",
    {"zipcode": zipcode, "city": city}).fetchone()

    #generate an url for the api call.
    KEY = 'e613b2582952ed3093a1ce6dde1b1521'
    api_url= "https://api.darksky.net/forecast/" + KEY + '/'+ location.lat + ','+ location.long
    weather = requests.get(api_url).json()
    weather = json.dumps(weather["currently"], indent = 2)

    #when the user enters the page, get the comment info.
    if session.get("notes") is None:
        session["notes"] = []
    try:
        note = request.form["note"]
        session["notes"].append(note)
    except:
        session["notes"] = []

    #when the user enters the page, get the check_in info.
    try:
        check_in = request.form["check_in"]
        if check_in == 1 and session["check_in"] == 0:
            location.check_ins += 1
            session["check_in"] += 1
            db.execute("UPDATE zip_codes SET check_ins = :location.check_ins WHERE zipcode = :location.zipcode",
            {"location.check_ins": location.check_ins, "location.zipcode": location.zipcode})
            db.commit()
    except:
        session["check_in"] = 0

    return render_template("location.html", location = location, weather = weather, notes=session["notes"])


@app.route('/api/<string:zipcode>')
def api(zipcode):
    location = db.execute("SELECT * FROM zip_codes WHERE zipcode = :zipcode",
    {"zipcode": zipcode}).fetchone()

    # Make sure location exists.
    if location is None:
        return jsonify({"error": "Invalid zipcode"}), 404

    # Get all the info.
    return render_template('api_call.html', location=location)

