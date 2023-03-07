import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

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
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    prvs_yr = dt.date(2017,8,23)-dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prvs_yr).all()
    session.close()
    
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(stations))
    return jsonify(stations=stations)
@app.route("/api/v1.0/tobs")
def temps():
    
    # date 1 year ago from last date in database
    prvs_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # all tobs last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prvs_yr).all()
    session.close()
    temps = list(np.ravel(results))
    # Return the results
    return jsonify(temps=temps)
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_data(start=None, end=None):
    
    # Select statement
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*select).\
            filter(Measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)
   
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    #list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
if __name__ == '__main__':
    app.run()









