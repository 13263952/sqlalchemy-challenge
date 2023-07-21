# Libraries and Modules
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Connecting the SQLte database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Database tables into classes
Base = automap_base()
Base.prepare(autoload_with=engine)

#Classes into variables
Measurement = Base.classes.measurement
Station = Base.classes.station

#Starting the interacting with the database
session = Session(engine)

#The Flask app is born
app = Flask(__name__)


#Homepage route with welcome options
@app.route("/")
def homepage():
    return (
        f"Welcome!<br/>"
        f"This is the Hawaii Climate Analysis API!<br/><br/>"
        f"Available Routes:<br/>"
        f"base api route: &nbsp;/api/v1.0<br/>"
        f"<ul style='list-style-type: none;'>"
        f"<li>/precipitation</li>"
        f"<li>/stations</li>"
        f"<li>/tobs</li>"
        f"<li>/temp/start</li>"
        f"<li>/temp/start/end</li>"
        f"</ul>"
        
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )
# Route to precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Calculation, the date one year ago from the last date in the database
    prvs_yr = dt.date(2017,8,23)-dt.timedelta(days=365)

    #Query to get the date and precipitation for each day
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prvs_yr).all()
    session.close()
    
    #Query results into a dictionary where the date is the key and precipitation is the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#route to get a list of all stations in the database
@app.route("/api/v1.0/stations")
def stations():
    #List of station names
    stations = session.query(Station.station).all()
    session.close()
    #Flatten the query results into a list using numpy.ravel
    stations = list(np.ravel(stations))
    return jsonify(stations=stations)

#Route to get temperature observations for the most active station in the last year
@app.route("/api/v1.0/tobs")
def temps():
    
    #Date 1 year ago from last date in database
    prvs_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query the database to get the temperature observations for the most active station in the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prvs_yr).all()
    session.close()

    #Flatten the query results into a list using numpy.ravel
    temps = list(np.ravel(results))
    # Return the results
    return jsonify(temps=temps)

#Define the route to get temperature statistics for a given date range
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_data(start=None, end=None):
    
    #Define the select statement to get minimum, average, and maximum temperatures
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        #If only the start date is provided, query the database for temperature statistics from the start date to the latest date
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*select).\
            filter(Measurement.date >= start).all()
        session.close()

         #Flatten the query results into a list using numpy.ravel
        temps = list(np.ravel(results))
        return jsonify(temps)
    #If both start and end dates are provided, query the database for temperature statistics within the given date range
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    #Flatten the query results into a list using numpy.ravel
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
#Starts the Flask app if this script is executed directly
if __name__ == '__main__':
    app.run()









