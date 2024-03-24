from flask import Flask
from flask import render_template, redirect, request, session, url_for, send_file, make_response, g
from flask import jsonify
import os
import json
import sqlite3
from os import urandom
from bs4 import BeautifulSoup
import requests

app = Flask(__name__, template_folder="templates")
app.secret_key= urandom(24)

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

def initialize_urls():
    # Initialize a list of tuples, each containing a URL and a manually selected title
    urls = [
        ("https://365datascience.com/career-advice/data-scientist-job-market/",
             "Data Science Jobs in 2024", "data_science_stuff.png", 
             "Our comprehensive 2023 tech layoffs study revealed that data scientists constituted merely..."),
        ("https://www.tomshardware.com/pc-components/gpus/nvidia-rtx-40-series-allegedly-getting-down-binned-gpu-updates-certain-4060-and-4070-class-cards-to-use-larger-harvested-chips", 
              "Nvidia's Newest GPU", "nvidia_gpu.png",
              "It's that time of the year again when Nvidia releases existing products with recycled or lower-binned silicon. According to hardware leaker MEGAsizeGPU..."),
        ("https://news.medtronic.com/five-healthcare-technology-trends-in-2024-newsroom", "Healthcare Technology Trends in 2024", "medtronic.png", 
            "AI can help address chronic staffing problems at hospitals. Likewise, it will continue to aid in the diagnosis of more diseases..."),
        ("https://www.hrw.org/report/2023/12/21/metas-broken-promises/systemic-censorship-palestine-content-instagram-and", "Systemic Censorship in Palestine",
         "meta.png", "Meta’s inconsistent enforcement of its own policies led to the erroneous removal of content about Palestine... "),
        # ("https://www.thezebra.com/resources/driving/future-car-design/", "Future Car Design")
        # Add more URLs and titles as needed
    ]
    return urls

def store_articles():
    urls_with_titles = initialize_urls()
    
    # Store summaries and entire articles in the database
    try:
        db = get_db()
        cursor = db.cursor()

        # Insert articles into the articles table
        for url, title, img, summary in urls_with_titles:
            cursor.execute(
                "INSERT INTO articles (title, summary, link, img) VALUES (?, ?, ?, ?)",
                (title, summary, url, img),
            )
        
        db.commit()
        return True
    except Exception as e:
        print("Error:", e)
        db.rollback()
        return False
    
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

        if user["pass"] == password:  
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
            "INSERT INTO users (email, firstname, lastname, pass) VALUES (?, ?, ?, ?)",
            (email, first_name, last_name, passw),
        )
        db.commit()

        # Store user information in the session
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        session["user_id"] = user["id"]

        return render_template("profile.html")

    return render_template("signup.html")

@app.route('/savepost', methods=['POST'])
def save_post():
    postid = request.form.get('article_id')
    user_id = session.get("user_id")  # Corrected access to session key
    link = request.form.get('link')
    try:
        if user_id is None:
            return jsonify({'success': False, 'error': 'User not logged in'})

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO saved (postid, userid, link) VALUES (?, ?, ?)", (postid, user_id, link),
        )
        db.commit()
        return redirect(url_for('explore'))
    except Exception as e:
        print("Error:", e)
        db.rollback()
        return render_template("error.html")
    

# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.json
#     user_message = data['message']

#     response = openai.Completion.create(
#         engine='gpt-3.5-turbo-instruct',
#         prompt=user_message,
#         max_tokens=50,
#         n=1,
#         stop=None,
#         temperature=0.7
#     )
#     assistant_reply = response.choices[0].text.strip()
#     return jsonify({'message': assistant_reply})

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/forme")
def forme():
    return render_template("forme.html")

@app.route("/explore")
def explore():
    store_articles()
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM articles")
        articles = cursor.fetchall()
        return render_template("explore.html", articles=articles)
    except Exception as e:
        print("Error:", e)
        return render_template("error.html")

@app.route("/logout")
def logout():
    return render_template("home.html")

# def scrape_article_content(url):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
#             # Find all text content within the <body> tag
#             body_text = soup.find('body').get_text()
#            # print("Web Scraped Content:", body_text.strip())  # Print the scraped content
#             return body_text.strip()
#         else:
#             return None
#     except Exception as e:
#         print("Error:", e)
#         return None

init_db()

if __name__ == "__main__":
    app.run(debug=True)


# url = str("https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/")
# htmlPage = requests.get(url)
# htmlGuts = BeautifulSoup(htmlPage.text)

# for link in htmlGuts.find_all('a'):
#     print(link.get('href'))

# def send_to_chat_for_summary(content):
#     try:
#         response = requests.post(
#             'http://localhost:5000/chat',  # Replace with your actual server URL
#             json={'message': '', 'scraped_content': content}
#         )
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except Exception as e:
#         print("Error:", e)
#         return None