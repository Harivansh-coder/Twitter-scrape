from flask import Flask, render_template, jsonify, request
import subprocess
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


app = Flask(__name__)

# Set up the connection to the mongo db
# Connect to MongoDB
client = MongoClient(os.environ['MONGO_URI'])
db = client['twitter_scraper']
collection = db['trends_scraped']

# Flask route to render the index.html template


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['GET'])
def run_scraper():
    try:

        # get the latest scraped data from the database
        latest_data = collection.find_one(sort=[('_id', -1)])

        # delete the _id field from the data
        if '_id' in latest_data:
            del latest_data['_id']

        if latest_data and (datetime.now() - datetime.strptime(latest_data['datetime'], '%Y-%m-%d %H:%M:%S')) < timedelta(minutes=400):
            return jsonify(latest_data)

        # Run the scraper script
        result = subprocess.check_output(
            ['python', 'scraper.py']).decode('utf-8')

        return jsonify(json.loads(result))

    except Exception as e:
        return render_template('error.html', error=f"An error occurred: {e}")


if __name__ == '__main__':
    app.run(debug=True)
