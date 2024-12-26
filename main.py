from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from scraper import run_scraper
from bson.objectid import ObjectId

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
def scrape():
    try:

        # get the latest scraped data from the database
        latest_data = collection.find_one(sort=[('_id', -1)])

        # # delete the _id field from the data
        if '_id' in latest_data:
            del latest_data['_id']

        if latest_data and (datetime.now() - datetime.strptime(latest_data['datetime'], '%Y-%m-%d %H:%M:%S')) < timedelta(minutes=10):
            return jsonify(latest_data)

        # Run the scraper script
        result = run_scraper()

        # delete the _id field from the data
        if '_id' in result:
            del result['_id']

        # result is a dictionary, convert it to json and return it
        return jsonify(result)

    except Exception as e:
        return render_template('error.html', error=f"An error occurred: {e}")


if __name__ == '__main__':
    app.run(debug=True)
