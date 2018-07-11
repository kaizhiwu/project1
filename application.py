import os

from flask import Flask, session, request, render_template, redirect, url_for, escape
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
        return render_template("index.html", message = message)
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
        return render_template("error.html", message="Wrong password, try again")

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

    # display the success message,and log the user in
    session['username'] = username
    message = "You are registered as %s" % escape(session['username'])
    return render_template("index.html", message = message)

