from flask import Flask
from flask import render_template, redirect, request, session, url_for, send_file, make_response, g
import os
import json
import sqlite3
from os import urandom
from bs4 import BeautifulSoup
import requests

# from os import environ as env 
# from urllib.parse import quote_plus, urlencode

# from authlib.integrations.flask_client import OAuth
# from dotenv import find_dotenv, load_dotenv

# ENV_FILE = find_dotenv()
# if ENV_FILE:
#     load_dotenv(ENV_FILE)

app = Flask(__name__, template_folder="templates")
app.secret_key= urandom(24)
# app.secret_key = env.get("APP_SECRET_KEY")

# oauth = OAuth(app)

# oauth.register(
#     "auth0",
#     client_id=env.get("AUTH0_CLIENT_ID"),
#     client_secret=env.get("AUTH0_CLIENT_SECRET"),
#     client_kwargs={
#         "scope": "openid profile email",
#     },
#     server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
# )

DATABASE = 'keepup.db'
app.config['DATABASE'] = DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/") #means the first page application opens to
def home():
    return render_template("home.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")  
        # print(email)
        # print(password)
        db = get_db()
        cursor = db.cursor()

        # Retrieve the user's record from the database based on email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("error.html")

        if user["password"] == password:  
            # Store user information in the session
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            return render_template("error.html")

    return render_template("login.html")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        if (
             not request.form.get("firstname")
            or not request.form.get("lastname")
            or not request.form.get("email")
            or not request.form.get("password")
        ):
            return render_template("error.html")

        email = request.form.get("email")
        passw = request.form.get("password")
        first_name = request.form.get("firstname")
        first_name = first_name[0].upper() + first_name[1:]
        last_name = request.form.get("lastname")
        last_name = last_name[0].upper() + last_name[1:]

        db = get_db()
        cursor = db.cursor()

        # Check if email already exists in the database
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("error.html")

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, passw) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, passw),
        )
        db.commit()

        # Store user information in the session
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        session["user_id"] = user["id"]

        return redirect(url_for("profile"))

    return render_template("signup.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

url = str("https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/")
htmlPage = requests.get(url)
htmlGuts = BeautifulSoup(htmlPage.text)

for link in htmlGuts.find_all('a'):
    print(link.get('href'))

# @app.route("/login")
# def login():
#     return oauth.auth0.authorize_redirect(
#         redirect_uri=url_for("callback", _external=True)
#     )
#     # return render_template("login.html")

# @app.route("/callback", methods=["GET", "POST"])
# def callback():
#     token = oauth.auth0.authorize_access_token()
#     session["user"] = token
#     return redirect("/dashboard")

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(
#         "https://" + env.get("AUTH0_DOMAIN")
#         + "/v2/logout?"
#         + urlencode(
#             {
#                 "returnTo": url_for("home", _external=True),
#                 "client_id": env.get("AUTH0_CLIENT_ID"),
#             },
#             quote_via=quote_plus,
#         )
#     )

# @app.route("/signup")
# def signup():
#     return render_template("signup.html")

# @app.route("/dashboard")
# def dashboard():
#     return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

init_db()

if __name__ == "__main__":
    app.run(debug=True)
