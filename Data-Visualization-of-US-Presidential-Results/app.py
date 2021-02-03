# import necessary libraries
#from app import db

#from models import create_classes
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd
import numpy as np

import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

import json

import scrape_2016_data
import api_2020_data
#################################################
# Mac
#################################################
# Set Executable Path & Initialize Chrome Browser

#def init_browser():
    #executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    #return Browser("chrome", **executable_path, headless=False)

#################################################
# Windows
#################################################
# Set Executable Path & Initialize Chrome Browser

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

#################################################
# Database Setup
#################################################

#from flask_sqlalchemy import SQLAlchemy
import warnings
warnings.filterwarnings('ignore')

import os, csv
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, load_only
from sqlalchemy import create_engine, func, inspect, distinct

# Imports the methods needed to abstract classes into tables
from sqlalchemy.ext.declarative import declarative_base

# Allow us to declare column types
from sqlalchemy import Column, Integer, String, Float

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db.sqlite"

# Sets an object to utilize the default declarative base in SQL Alchemy
#Base = declarative_base()

#class us_election_results(Base):
#    __tablename__ = 'us_election_results'
#    id = Column(Float, primary_key=True)
#    year = Column(Integer)
#    state_name = Column(String(255))
#    state_abbr = Column(String(255))
#    combined_fips = Column(Integer)
#    county_name = Column(String(255))
#    county_fips = Column(Integer)
#    votes_dem = Column(Integer)
#    votes_gop = Column(Integer)
#    total_votes = Column(Integer)
#    diff = Column(Integer)
#    per_dem = Column(Float)
#    per_gop = Column(Float)
#    per_point_diff = Column(Float)


# Create a Specific Instance of the Dog and Cat classes
# ----------------------------------

# Calls the Pet Constructors to create "Dog" and "Cat" objects
#dog = Dog(name='Rex', color='Brown', age=4)
#cat = Cat(name="Felix", color="Gray", age=7)

# Create Database Connection
# ----------------------------------
# Creates a connection to our DB
#database_path = "db.sqlite"
#engine = create_engine(f"sqlite:///{database_path}?check_same_thread=False")
#conn = engine.connect()

# Remove tracking modifications
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create a "Metadata" Layer That Abstracts our SQL Database

# Use this to clear out the db
# ----------------------------------
#Base.metadata.drop_all(engine)

# ----------------------------------
# Create (if not already in existence) the tables associated with our classes.
#Base.metadata.create_all(engine)

# Create a Session Object to Connect to DB
# ----------------------------------
# Session is a temporary binding to our DB
#session = Session(bind=engine)

# Add Records to the Appropriate DB
# ----------------------------------
# Use the SQL ALchemy methods to run simple "INSERT" statements using the classes and objects  
#try:
#    session.add(dog)
#    session.add(cat)
#    session.commit()   
#except:
#    session.rollback()
#    raise
#finally:
    # Query the Tables
    # ----------------------------------
    # Perform a simple query of the database
#    dog_list = session.query(Dog)
#    for doggy in dog_list:
#        print(doggy.name)

#    cat_list = session.query(Cat)
    
#    for kitty in cat_list:
#        print(kitty.name)    
    
    #session.close()

# Create the inspector and connect it to the engine
#inspector = inspect(engine)

# Collect the names of tables within the database
#inspector.get_table_names()

# Display the column names of pets
#columns = inspector.get_columns('us_election_results')
#for column in columns:
#    print(column["name"], column["type"])

# Use `engine.execute` to select and display the first 10 rows from the measurement table
#print(engine.execute('SELECT * FROM us_election_results LIMIT 10').fetchall())

# Display the column names of measurement
# columns = inspector.get_columns('us_election_results')
# for column in columns:
#    print(column["name"], column["type"])

# Reflect an existing database into a new model
#Base = automap_base()

# Reflect the tables
#Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
#print(Base.classes.keys())

# Save reference to the table
#Pet = Base.classes.pets
#UsElectionResult = Base.classes.us_election_results

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#db = SQLAlchemy(app)

#Pets = create_classes(session)

# create route that renders index.html template
@app.route("/")
def index():
    return render_template("index.html")

# Scrape Data for 2016 and API data for 2020
@app.route("/scrape")
def data():

    try:
        api_2020_data.api_2020()
        print("2020 data preparation successful")
    except:
        print("2020 data preparation unsuccessful")

    try:
        scrape_2016_data.scrape_2016()
        print("2016 data preparation successful")
    except:
        print("2016 data preparation unsuccessful")

    # Create the inspector and connect it to the engine
    #inspector = inspect(engine)

    # Collect the names of tables within the database
    #inspector.get_table_names()

    # Display the column names of pets
    #columns = inspector.get_columns('us_election_results')
    #for column in columns:
    #    print(column["name"], column["type"])

    # Use `engine.execute` to select and display the first 10 rows from the measurement table
    #print(engine.execute('SELECT * FROM us_election_results LIMIT 10').fetchall())

    # Display the column names of measurement
    # columns = inspector.get_columns('us_election_results')
    # for column in columns:
    #    print(column["name"], column["type"])

    # Reflect an existing database into a new model
    #Base = automap_base()

    # Reflect the tables
    #Base.prepare(engine, reflect=True)

    # We can view all of the classes that automap found
    #print(Base.classes.keys())
    # Use this to clear out the db
    # ----------------------------------
    #Base.metadata.drop_all(engine)

    # ----------------------------------
    # Create (if not already in existence) the tables associated with our classes.
    #Base.metadata.create_all(engine)
    
    # Load 2016 data
    #insert_query = "INSERT INTO us_election_results (id,year,state_name,county_fips,county_name,votes_gop,votes_dem,total_votes,diff,per_gop,per_dem,per_point_diff) VALUES (:id,:year,:state_name,:county_fips,:county_name,:votes_gop,:votes_dem,:total_votes,:diff,:per_gop,:per_dem,:per_point_diff)"
    #print(insert_query)

    #with open('static/Resources/2016_US_County_Level_Presidential_Results_sql.csv', 'r', encoding="utf-8") as csvfile:
    #    csv_reader = csv.reader(csvfile, delimiter=',')
    #    next(csv_reader)
    #    engine.execute(
    #        insert_query,
    #        [{"id": row[0], "year": 2016, "state_name": row[1], "county_fips": row[2], "county_name": row[3], "votes_gop": row[4], "votes_dem": row[5], "total_votes": row[6], "diff": row[7], "per_gop": row[8], "per_dem": row[9], "per_point_diff": row[10]}
    #            for row in csv_reader]
    #    )
        # Create our session (link) from Python to the DB
        #session = Session(engine)

    #sel = [UsElectionResult.id, UsElectionResult.year, UsElectionResult.state_name, UsElectionResult.county_fips, UsElectionResult.county_name, UsElectionResult.votes_gop,\
    #    UsElectionResult.votes_dem, UsElectionResult.votes_dem, UsElectionResult.total_votes, UsElectionResult.diff ]

    #data_2016_db = session.query(*sel).\
    #                    filter(UsElectionResult.year == 2016).order_by(UsElectionResult.total_votes.desc()).all()
    # Save the query results as a Pandas DataFrame
    #data_2016_df = pd.DataFrame( data_2016_db )

    #print(data_2016_df.head())

    # Load 2020 data
    #insert_query = "INSERT INTO us_election_results (id,year,state_name,county_fips,county_name,votes_gop,votes_dem,total_votes,diff,per_gop,per_dem,per_point_diff) VALUES (:id,:year,:state_name,:county_fips,:county_name,:votes_gop,:votes_dem,:total_votes,:diff,:per_gop,:per_dem,:per_point_diff)"
    #print(insert_query)

    #with open('static/Resources/2020_US_County_Level_Presidential_Results_sql.csv', 'r', encoding="utf-8") as csvfile:
    #    csv_reader = csv.reader(csvfile, delimiter=',')
    #    next(csv_reader)
    #    engine.execute(
    #        insert_query,
    #        [{"id": row[0], "year": 2020, "state_name": row[1], "county_fips": row[2], "county_name": row[3], "votes_gop": row[4], "votes_dem": row[5], "total_votes": row[6], "diff": row[7], "per_gop": row[8], "per_dem": row[9], "per_point_diff": row[10]}
    #            for row in csv_reader]
    #    )
        # Create our session (link) from Python to the DB
        #session = Session(engine)

    #sel = [UsElectionResult.id, UsElectionResult.year, UsElectionResult.state_name, UsElectionResult.county_fips, UsElectionResult.county_name, UsElectionResult.votes_gop,\
    #    UsElectionResult.votes_dem, UsElectionResult.votes_dem, UsElectionResult.total_votes, UsElectionResult.diff ]

    #data_2020_db = session.query(*sel).\
    #                    filter(UsElectionResult.year == 2020).order_by(UsElectionResult.total_votes.desc()).all()
    # Save the query results as a Pandas DataFrame
    #data_2020_df = pd.DataFrame( data_2020_db )

    #print(data_2020_df.head())

    return redirect("/", code=302)

    #return render_template("index.html")

@app.route("/election_results")
def election_results():
    return render_template("election_results.html")

@app.route("/demographics")
def demographics():
    print(os.getcwd())
    #demographic_datapath = {'path': '/static/assets/data/data.csv'}
    return render_template("demographics.html")

@app.route("/swing")
def swing():
    return render_template("swing.html")

@app.route("/voter_turnouts")
def voter_turnouts():
    return render_template("voter_turnouts.html")

if __name__ == "__main__":
    app.run(debug=True)
