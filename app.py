# Code contributed by all.
from contextlib import closing
from flask import Flask, render_template, request, redirect, url_for
import requests
from requests_oauthlib import OAuth1
import sqlite3

# Used Junie's API credentials as she is the author of POST
# Author of this code: Junie
app = Flask(__name__)
# Twitter API credentials (replace with actual keys and tokens)
CONSUMER_KEY = "ADD_YOUR_CONSUMERKEY"
CONSUMER_SECRET = "ADD_YOUR_CONSUMER_SECRET"
ACCESS_TOKEN = "ADD_YOUR_ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ADD_YOUR_TOKEN_SECRET"

# OAuth1 setup
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


# Author of this part of code is Apoorva
# Database configuration
app.config['DATABASE'] = 'tweets.db'  # Set your database filename here

# Utility function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)
    return conn

# Initialize the database
def init_db():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tweets
                          (tweet_id TEXT PRIMARY KEY, content TEXT)''')
        conn.commit()
# Store a tweet in the database
def store_tweet(tweet_id, content):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tweets (tweet_id, content) VALUES (?, ?)", (tweet_id, content))
        conn.commit()

# This part of code is written by Rinku
# Delete a tweet from the database
def delete_tweet_from_db(tweet_id):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tweets WHERE tweet_id = ?", (tweet_id,))
        conn.commit()

# This part of code is written by Nitya
# Retrieve a specific tweet by tweet_id
def retrieve_tweet_from_db(tweet_id):
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM tweets WHERE tweet_id = ?", (tweet_id,))
        row = cursor.fetchone()
        return row[0] if row else None

# Retrieve all tweets from the database
def retrieve_all_tweets():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tweet_id, content FROM tweets")
        rows = cursor.fetchall()
        return rows

def clear_tweets():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tweets")  # This removes all tweets

# Author of this code: Junie
# Function to post a tweet
def post_tweet(content):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": content}

    try:
        response = requests.post(url, json=payload, auth=auth)

        # If tweet is successfully posted
        if response.status_code == 201:
            tweet_data = response.json()
            tweet_id = tweet_data.get("data", {}).get("id", None)

            if tweet_id:
                # Store the tweet ID and content in the database
                store_tweet(tweet_id, content)

            return response

        else:
            # Log the error message from Twitter API
            error_message = response.json().get('detail', 'Unknown error')
            print(f"Failed to post tweet: {error_message}")
            return None

    except Exception as e:
        # Catch any unexpected exceptions
        print(f"Exception occurred while posting tweet: {e}")
        return None

# Author of this code: Rinku
# Function to delete a tweet
def delete_tweet(tweet_id):
    # First check if the tweet exists in the database
    existing_tweet = retrieve_tweet_from_db(tweet_id)
    if existing_tweet is None:
        return None  # Tweet does not exist in the database

    # Proceed to delete the tweet from Twitter
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    response = requests.delete(url, auth=auth)

    if response.status_code == 200:
        delete_tweet_from_db(tweet_id)
        return True  # Successfully deleted
    return False  # Deletion failed

# This part of code is written by Apoorva
@app.route('/')
def index():
    return render_template('index.html')

# This part of code is written by Junie
@app.route('/post', methods=['POST'])
def post():
    content = request.form['content']

    # Check if the content has already been posted
    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM tweets WHERE content = ?", (content,))
        tweet = cursor.fetchone()

        if tweet:
            # If duplicate tweet found, send a message to the UI
            message = "Duplicate tweet content found, not posting."
            return render_template('index.html', message=message)

    # Try to post the tweet
    response = post_tweet(content)
    if response is None or response.status_code != 201:
        message = "Failed to post the tweet. Please try again."
        return render_template('index.html', message=message)

    return redirect(url_for('index'))

# This part of code is written by Rinku
@app.route('/delete', methods=['POST'])
def delete():
    tweet_id = request.form['tweet_id']
    response = delete_tweet(tweet_id)
    if response is None:
        error_message = "Invalid tweet ID: Tweet not found."
        return render_template('index.html', error=error_message)
    elif response is False:
        error_message = "Failed to delete the tweet."
        return render_template('index.html', error=error_message)
    delete_tweet_from_db(tweet_id)
    clear_tweets()
    return redirect(url_for('index'))

# This part of code is written by Nitya
@app.route('/retrieve', methods=['POST'])
def retrieve():
    tweet_id = request.form['tweet_id']
    tweet_content = retrieve_tweet_from_db(tweet_id)
    return render_template('index.html', retrieved_tweet=tweet_content if tweet_content else "Tweet not found.")

# New route to display all stored tweets
@app.route('/display', methods=['GET'])
def display():
    all_tweets = retrieve_all_tweets()
    return render_template('index.html', all_tweets=all_tweets)

# This part of code is written by Apoorva
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
