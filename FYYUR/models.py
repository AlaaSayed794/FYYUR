from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    #changed table name to reflect the many to many relationships
    __tablename__ = 'venues'

    #Model attributes : 
    #(added missing variables and rearranged existing based
    #  on sample data order offered in starter code)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String, nullable=False)
    address = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False , default=True)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ##########################################################################################################
    #Relationships:
    #venues is linked to artists using shows class,lazy join is used 
    shows = db.relationship('Show', backref='venue', lazy=True,cascade="all, delete")

    #returns a dictionary of upcoming and past shows compared to datetime.now()
    def showsDictionary(self):
      upcoming_shows = []
      past_shows = []
      time_now = datetime.now()
      for show in self.shows:
        entry = {}
        entry['id'] = show.id
        entry['artist_id'] = show.artist.id
        entry['artist_name'] = show.artist.name
        entry['artist_image_link'] = show.artist.image_link
        entry['start_time'] = str(show.start_time)
        if (show.start_time > time_now):
          upcoming_shows.append(entry)
        else:
          past_shows.append(entry)
      shows_dict = {}
      shows_dict['upcoming_shows'] = upcoming_shows
      shows_dict['past_shows'] = past_shows
      return(shows_dict)

    #returns number of upcoming shows
    def num_upcoming_shows(self):
      num_upcoming = 0 
      time_now = datetime.now()
      
      for show in self.shows:
        if (show.start_time > time_now):
          num_upcoming=num_upcoming+1
      return(num_upcoming)
    #converts venue object to data dictionary required for the view
    def to_data(self):
      data = {}
      data['id'] = self.id
      data['name'] = self.name
      data['genres'] = self.genres.split(',')
      data['address'] = self.address
      data['city'] = self.city
      data['state'] = self.state
      data['phone'] = self.phone
      data['website'] = self.website
      data['facebook_link'] = self.facebook_link
      data['seeking_talent'] = self.seeking_talent
      data['seeking_description'] = self.seeking_description
      data['image_link'] = self.image_link
      shows = self.showsDictionary()
      data['past_shows']  = shows['past_shows']
      data['upcoming_shows'] = shows['upcoming_shows']
      data['past_shows_count']  = len(shows['past_shows'])
      data['upcoming_shows_count'] = len(shows['upcoming_shows']) 
      return(data)

class Artist(db.Model):
    #changed table name to reflect the many to many relationships
    __tablename__ = 'artists'
    #Model attributes : 
    #(added missing variables and rearranged existing based
    #  on sample data order offered in starter code)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean(), nullable=False , default=True)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #Relationships:
    #artists is linked to venues using shows class,lazy join is used 
    shows = db.relationship('Show', backref='artist', lazy=True,cascade="all, delete")
    #returns number of upcoming shows
    def num_upcoming_shows(self):
      num_upcoming = 0 
      time_now = datetime.now()
      
      for show in self.shows:
        if (show.start_time > time_now):
          num_upcoming=num_upcoming+1
      return(num_upcoming)
    #returns a dictionary of upcoming and past shows compared to datetime.now()
    def showsDictionary(self):
      upcoming_shows = []
      past_shows = []
      time_now = datetime.now()
      for show in self.shows:
        entry = {}
        entry['id'] = show.id
        entry['venue_id'] = show.venue.id
        entry['venue_name'] = show.venue.name
        entry['venue_image_link'] = show.venue.image_link
        entry['start_time'] = str(show.start_time)
        if (show.start_time > time_now):
          upcoming_shows.append(entry)
        else:
          past_shows.append(entry)
      shows_dict = {}
      shows_dict['upcoming_shows'] = upcoming_shows
      shows_dict['past_shows'] = past_shows
      return(shows_dict)
    def to_data(self):
      data = {}
      data['id'] = self.id
      data['name'] = self.name
      data['genres'] = self.genres.split(',')
      data['city'] = self.city
      data['state'] = self.state
      data['phone'] = self.phone
      data['website'] = self.website
      data['facebook_link'] = self.facebook_link
      data['seeking_venue'] = self.seeking_venues
      data['seeking_description'] = self.seeking_description
      data['image_link'] = self.image_link
      shows = self.showsDictionary()
      data['past_shows']  = shows['past_shows']
      data['upcoming_shows'] = shows['upcoming_shows']
      data['past_shows_count']  = len(shows['past_shows'])
      data['upcoming_shows_count'] = len(shows['upcoming_shows']) 
      return(data)
    

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
