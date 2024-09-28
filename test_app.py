# Code contributed by all.
import os
import sqlite3
import pytest
from app import app, init_db, store_tweet, clear_tweets

# This part of code is written by Apoorva
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_tweets.db'  # Use a separate database for testing
    with app.test_client() as client:
        with app.app_context():
            init_db()  # Initialize the test database
            clear_tweets()
        yield client

    # Cleanup after tests
    with app.app_context():
        if os.path.exists(app.config['DATABASE']):
            os.remove(app.config['DATABASE'])  # Remove the test database after tests are done

# This part of code is written by Junie
def test_post_tweet(client):
    response = client.post('/post', data={'content': 'This is a test tweet.'})
    assert response.status_code == 302  # Expecting a redirect after posting

    # Verify the tweet is stored in the database
    with app.app_context():
        cursor = sqlite3.connect(app.config['DATABASE']).cursor()  # Use the test database
        cursor.execute("SELECT tweet_id, content FROM tweets WHERE content = ?", ('This is a test tweet.',))
        tweet = cursor.fetchone()
        assert tweet is not None
        assert tweet[1] == 'This is a test tweet.'  # Check the content matches

# This part of code is written by Rinku
def test_delete_tweet(client):
    # Store a tweet first
    store_tweet('12345', 'This tweet will be deleted.')

    # Now, delete the tweet
    response = client.post('/delete', data={'tweet_id': '12345'})
    assert response.status_code == 302  # Expecting a redirect after deletion

    # Check if the tweet is deleted from the database
    with app.app_context():
        cursor = sqlite3.connect(app.config['DATABASE']).cursor()  # Use the test database
        cursor.execute("SELECT content FROM tweets WHERE tweet_id = ?", ('12345',))
        tweet = cursor.fetchone()
        assert tweet is None  # Tweet should not be found
# This part of code is written by Rinku
def test_delete_invalid_tweet(client):
    response = client.post('/delete', data={'tweet_id': 'invalid_id'})
    assert response.status_code == 200  # Expecting to render the index page
    assert b'Invalid tweet ID: Tweet not found.' in response.data  # Check for the error message

# This part of code is written by Nitya
def test_retrieve_tweet(client):
    store_tweet('67890', 'Retrieve this tweet.')
    response = client.post('/retrieve', data={'tweet_id': '67890'})
    assert response.status_code == 200
    assert b'Retrieve this tweet.' in response.data  # Ensure the tweet content is in the response

# This part of code is written by Nitya
def test_display_tweets(client):
    store_tweet('11111', 'First tweet.')
    store_tweet('22222', 'Second tweet.')

    response = client.get('/display')
    assert response.status_code == 200
    assert b'First tweet.' in response.data  # Ensure first tweet is displayed
    assert b'Second tweet.' in response.data  # Ensure second tweet is displayed
