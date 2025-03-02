import os
from os import environ as env
import json
import requests
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
from dotenv import find_dotenv, load_dotenv

# Load .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Configure application
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Configure authlib to handle authentication with Auth0
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cardtrading.db")

# Obtain management API access token. Code from CS50 DDB
api_token_response = requests.post("https://dev-ver8yn2dssrffqv6.uk.auth0.com/oauth/token", {
        'client_id': env.get("AUTH0_CLIENT_ID"),
        'client_secret': env.get("AUTH0_CLIENT_SECRET"),
        'audience': 'https://dev-ver8yn2dssrffqv6.uk.auth0.com/api/v2/',
        'grant_type': 'client_credentials'
    })
management_token = api_token_response.json().get('access_token')

def get_user_info(auth0_id):
    domain = 'dev-ver8yn2dssrffqv6.uk.auth0.com'

    headers = {
        'Authorization': f'Bearer {management_token}'
    }

    response = requests.get(f'https://{domain}/api/v2/users/{auth0_id}', headers=headers)
    user_info = response.json()
    return user_info

@app.route("/")
def index():
    return render_template(
        "index.html", session=session.get("user"), random_card=session.get('random_card')
    )

@app.route("/login")
def login():
    session.clear()
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    session["jwt_token"] = token["access_token"]

    # Fetch the user information from Auth0
    auth0_id = token['userinfo']['sub']
    user_info = get_user_info(auth0_id)

    # Fetch user info from db
    user = db.execute("SELECT * FROM users WHERE auth0_id = ?", auth0_id)
    # Create user if first login
    if not user:
        db.execute("""
                   INSERT INTO users (auth0_id, email, username, metadata)
                   VALUES (?, ?, ?, ?)
                   """, auth0_id, user_info['email'], user_info.get('username', ''), str(user_info.get('user_metadata', {})))
        user = db.execute("SELECT * FROM users WHERE auth0_id = ?", auth0_id)

    # Store user info into session
    session['user']['user_info'] = {
        'id': user[0]['id'],
        'auth0_id': user[0]['auth0_id'],
        'username': user[0]['username'],
        'email': user[0]['email'],
        'gems': user[0]['gems'],
        'metadata': user[0]['metadata']
    }
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/account")
def account():
    url = "https://dev-ver8yn2dssrffqv6.uk.auth0.com/userinfo"
    headers = {
        "Authorization": f"Bearer {session['jwt_token']}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to fetch user info", response.status_code
    user_info = response.json()
    return render_template("account.html", user_info=user_info, session=session.get("user"))

@app.route("/update", methods=["POST"])
def update():
   new_username = request.form.get("username")

   headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/json"
    }
   user_id = session["user"]["user_info"]["auth0_id"]
   update_response = requests.patch(f"https://dev-ver8yn2dssrffqv6.uk.auth0.com/api/v2/users/{user_id}",headers=headers, json={'username': new_username})
   print(user_id)
   if update_response.status_code == 200:
       # Update db
       db.execute("UPDATE users SET username = ? WHERE auth0_id = ?", new_username, user_id)
       # Update session
       session['user']['user_info']['username'] = new_username
       flash("Username updated successfully")
       return redirect(url_for('account'))
   elif update_response.status_code == 400 and "operation_not_supported" in update_response.text:
       # Update local db only
       db.execute("UPDATE users SET username = ? WHERE auth0_id = ?", new_username, user_id)
       # Update session
       session['user']['user_info']['username'] = new_username
       flash("Username updated locally")
       return redirect(url_for('account'))
   else:
       return "Failed to update username", update_response.status_code

@app.route("/passwordreset", methods=["POST"])
def passwordreset():
    email = session['user']['user_info']['email']
    url = "https://dev-ver8yn2dssrffqv6.uk.auth0.com/dbconnections/change_password"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "client_id": "rdkk8xvAGIFGPi9dd3XN7wKFUWP8jCkD",
        "email": email,
        "connection": "Username-Password-Authentication"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.text, response.status_code

@app.route("/collection")
def collection():
    user = session['user']['user_info']
    user_cards = db.execute('''
               SELECT cards.name, cards.cost, cards.image_path, usercards.quantity
               FROM cards
               JOIN usercards
               ON cards.id = usercards.card_id
               WHERE usercards.user_id = ?
               ''', user['id'])
    return render_template("collection.html", user_cards=user_cards)

@app.route("/trade")
def trade():
    return render_template("trade.html")

@app.route("/buy", methods=["GET","POST"])
def buy():
    user = session['user']['user_info']
    gems = user['gems']

    # import trade db and exlcude users cards currently on sale
    cards_on_sale = db.execute('''
                               SELECT trade.*, cards.image_path, cards.name, cards.cost
                               FROM trade
                               JOIN cards
                               ON trade.card_id = cards.id
                               WHERE seller_id != ?
                               ''', user['id'])
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve JSON data
        data = request.get_json()
        sale_ids = [int(card['sale_id']) for card in data['selectedCards']]
        print(sale_ids)

        # Filter cards_on_sale based on sales
        sales = [sale for sale in cards_on_sale if sale['sale_id'] in sale_ids]

        try:
            print(len(sales))
            print(sales)
            # Update users cards
            for sale in sales:
                print(sale)
                # Check if user has card
                user_card = db.execute('''
                                       SELECT quantity
                                       FROM usercards
                                       WHERE user_id = ?
                                       AND card_id = ?
                                       ''', user['id'], sale['card_id'])
                if user_card:
                    db.execute('''
                               UPDATE usercards
                               SET quantity = quantity + 1
                               WHERE user_id = ?
                               AND card_id = ?
                               ''', user['id'], sale['card_id'])
                else:
                    db.execute('''
                               INSERT INTO usercards (user_id, card_id, quantity)
                               VALUES (?, ?, 1)
                               ''', user['id'], sale['card_id'])

                # Update Seller's Gems
                db.execute('''
                           UPDATE users
                           SET gems = gems + ?
                           WHERE id = ?
                           ''', sale['price'], sale['seller_id'])

                # Remove Gems from user
                db.execute('''
                           UPDATE users
                           SET gems = gems - ?
                           WHERE id = ?
                           ''', sale['price'], user['id'])

            # Update session gems
            updated_user = db.execute("SELECT gems FROM users WHERE id = ?", user['id'])
            session['user']['user_info']['gems'] = updated_user[0]['gems']

            # Remove sales from trade table
            placeholders = ', '.join(['?'] * len(sale_ids))
            query = f'DELETE FROM trade WHERE sale_id IN ({placeholders})'
            db.execute(query, *sale_ids)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect("/buy")


        flash("Cards Bought!")
        return jsonify({"redirect": url_for('buy')})
    else:
        return render_template("buy.html", cards_on_sale=cards_on_sale, gems=gems)

@app.route("/sellpage")
def sellpage():
    user = session['user']['user_info']
    # Import cards owned by user
    user_cards = db.execute('''
                            SELECT cards.name, cards.cost, cards.id, cards.image_path, usercards.quantity
                            FROM cards
                            JOIN usercards
                            ON cards.id = usercards.card_id
                            WHERE usercards.user_id = ?
                            ORDER BY cost ASC
                            ''', user['id'])
    # Import cards currently on sale by user
    for_sale = db.execute('''
                          SELECT trade.*, cards.image_path, cards.name
                          FROM trade
                          JOIN cards
                          ON trade.card_id = cards.id
                          WHERE seller_id = ?
                          ORDER BY price DESC
                          ''', user['id'])
    return render_template("sell.html", user_cards=user_cards, for_sale=for_sale)

@app.route("/delete", methods=["POST"])
def return_card():
    # Upload selected cards to user table
    user = session['user']['user_info']
    sale_id = int(request.form.get('sale_id'))
    card = db.execute('''
                      SELECT *
                      FROM trade
                      WHERE sale_id = ?
                      ''', sale_id)
    card_id = card[0]['card_id']
    # Check if user has card already
    user_card = db.execute('''
                           SELECT *
                           FROM usercards
                           WHERE user_id = ?
                           AND card_id = ?
                           ''', user['id'], card_id)
    if user_card:
        # Update quantity
        db.execute("""
                   UPDATE usercards
                   SET quantity = quantity + 1
                   WHERE user_id = ?
                   AND card_id = ?
                   """, user['id'], card_id)
    else:
        # Add card to user
        db.execute("""
                   INSERT INTO usercards (user_id, card_id, quantity)
                   VALUES (?, ?, ?)
                   """, user['id'], card_id, 1)
    # Remove selected cards from trade
    db.execute("DELETE FROM trade WHERE sale_id = ?", sale_id)
    flash("Card Returned to Collection!")
    return redirect(url_for('sellpage'))

@app.route("/price", methods=["POST"])
def update_price():
    # Update price of selected card in trade table
    sale_id = int(request.form.get('sale_id'))
    new_price = int(request.form.get('price'))
    db.execute('''
               UPDATE trade
               SET price = ?
               WHERE sale_id = ?
               ''', new_price, sale_id)
    flash("Price Updated")
    return redirect(url_for('sellpage'))

@app.route("/sell", methods=["POST"])
def sell():
    user = session['user']['user_info']
    # Retrieve data from JS
    data = request.get_json()
    selected_cards = data['selectedCards']
    # Upload selected cards to trade table
    for card in selected_cards:
        card_id = card['card_id']
        price = card['price']
        seller_id = user['id']
        quantity = int(card['quantity'])
        # quantity = number of sales
        for i in range(quantity):
            db.execute('''
                       INSERT INTO trade (card_id, seller_id, price)
                       VALUES (?, ?, ?)
                       ''', card_id, seller_id, price)
        # Remove selected cards from user
        # Update quantity
        db.execute('''
                   UPDATE usercards
                   SET quantity = quantity - ?
                   WHERE user_id = ?
                   AND card_id = ?
                   ''', quantity, seller_id, card_id)
        # Remove card from usercards if quantity is now 0
        db.execute('''
                   DELETE FROM usercards
                   WHERE user_id = ?
                   AND card_id = ?
                   AND quantity = 0
                   ''', seller_id, card_id)
    flash("Cards up for Sale!")
    return jsonify({"redirect": url_for('sellpage')})

# Code from chatGPT
def weighted_random_card(probabilities):
    total = sum(item["weight"] for item in probabilities)
    r = random.uniform(0, total)
    upto = 0
    for item in probabilities:
        if upto + item["weight"] >= r:
            return item["value"]
        upto += item["weight"]
    assert False, "Shouldn't get here"

card_probabilities = [
    {"value": 10, "weight": 0.60},
    {"value": 20, "weight": 0.26},
    {"value": 40, "weight": 0.12},
    {"value": 80, "weight": 0.02}
]

@app.route("/reveal_card", methods=["POST"])
def reveal_card():
    user = session['user']['user_info']
    gems = user['gems']

    if gems < 10:
        flash("Not Enough Gems!")
        return redirect("/")

    random_card_value = weighted_random_card(card_probabilities)

    # Remove 10 gems from user
    db.execute("UPDATE users SET gems = gems - 10 WHERE id = ?", user['id'])
    updated_user = db.execute("SELECT gems FROM users WHERE id = ?", user['id'])
    session['user']['user_info']['gems'] = updated_user[0]['gems']

    # Get card
    random_card = db.execute("""
                             SELECT *
                             FROM cards
                             WHERE cost = ?
                             ORDER BY RANDOM()
                             LIMIT 1
                             """, random_card_value)

    card_id = random_card[0]['id']

    # Check if user has card already
    user_card = db.execute('''
                           SELECT *
                           FROM usercards
                           WHERE user_id = ?
                           AND card_id = ?
                           ''', user['id'], card_id)
    if user_card:
        # Update quantity
        db.execute("""
                   UPDATE usercards
                   SET quantity = quantity + 1
                   WHERE user_id = ?
                   AND card_id = ?
                   """, user['id'], card_id)
    else:
        # Add card to user
        db.execute("""
                   INSERT INTO usercards (user_id, card_id, quantity)
                   VALUES (?, ?, ?)
                   """, user['id'], card_id, 1)

    session['random_card'] = random_card[0]
    flash(random_card[0])

    return redirect("/")
