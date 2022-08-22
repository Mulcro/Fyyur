from email.policy import default
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
db = SQLAlchemy(app)
moment = Moment(app)
app.config.from_object('config')  
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    genres = db.Column(JSON)
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(1000))
    seeking_talent = db.Column(db.Boolean, default=False)
    upcoming_shows_count = db.Column(db.String(120))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    website = db.Column(db.String(500))
    area = db.Column(db.Integer,  db.ForeignKey('area.id'), nullable=True)
    show = db.relationship('Show', backref='venue', lazy=True)
    upcomingShows = db.relationship('UpcomingShow', backref='venue',lazy=True)
    pastShows = db.relationship('PastShow', backref='venue',lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(10000))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(JSON)
    seeking_description = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    seeking_venue = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist',lazy=True)
    upcomingShows = db.relationship('UpcomingShow', backref='artist',lazy=True)
    pastShows = db.relationship('PastShow', backref='artist',lazy=True)

class Area(db.Model):
  __tablename__ = 'area'
  id = db.Column(db.Integer, primary_key=True)
  venues = db.relationship('Venue', backref='venue_area', lazy=True)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))

class Show(db.Model):
  __tablename__ = 'shows'
  show_id = db.Column(db.Integer, primary_key = True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable = False)
  start_time = db.Column(db.String)


  