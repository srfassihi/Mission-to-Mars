from flask import Flask, render_template, redirect, url_for              # Render template and redirect to another url and create url
from flask_pymongo import PyMongo                               # Use PyMongo to interact with MongoDB
import scraping                                                 # Use scraping.py file

# Setup flask
app = Flask(__name__)

# Use flask_pymongo to setup mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Define route for HTML page
@app.route("/")
def index():
   mars = mongo.db.mars.find_one()
   return render_template("index.html", mars=mars)

# Add route to scrape data and insert into DB (if doesnt exist)
@app.route("/scrape")
def scrape():
   mars = mongo.db.mars
   # Run scrape script
   mars_data = scraping.scrape_all()
   # Update MongoDB using scraped data
   mars.update_one({}, {"$set":mars_data}, upsert=True)
   return redirect('/', code=302)

# Instruct Flask to run app
if __name__ == "__main__":
   app.run(debug=True)