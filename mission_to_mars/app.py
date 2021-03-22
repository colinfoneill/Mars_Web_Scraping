#import dependencies
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

#create an instance of Flask
app = Flask(__name__)

# Use pymongo to establish Mongo connection
app.config['MONGO_URI'] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

#home route with index.hml format
@app.route("/")
def home():

    #assign mongo data to variable
    mars = mongo.db.mars.find_one()
    
    #return tamplate and data
    return render_template("index.html", mars=mars)

# Route to call function from mission_to_mars.py
@app.route("/scrape")
def scrape():
    
    #run the scrape function and assign it to a variable
    mars_data = scrape_mars.scrape()
    
    #update the mongo database using update and upsert=True
    mongo.db.mars.update({}, mars_data, upsert=True)

    #redirect back to the home page
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
