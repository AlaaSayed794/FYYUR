#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify,make_response
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#adding migrate import to use it to connect to the database
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database using flask migrate
migrate = Migrate(app,db)

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  #fixed locale entry based on udacity git hub issues discussion
  try:
      returnedDate = babel.dates.format_datetime(date, format, locale='en')
  except:
      returnedDate = str(date)
  return returnedDate
  
app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues Section
#  ----------------------------------------------------------------

#  Show Venues list
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #this function handles a corner case where multiple states can have a city with the same name
  #I think this could have been done using SQL
  cities_dict = {}
  data = []
  venues_list = Venue.query.all()
  
  #loop through all venues and create a dictionary of city/state as a key , venues belonging to the key as values
  for venue in venues_list:
    city_state = venue.city+'$split$'+venue.state
    if city_state in cities_dict:
      cities_dict[city_state].append(venue)
    else:
      cities_dict[city_state] = [venue]

  #loop through each city to construct an entry for the data list
  for city in cities_dict:
    entry = {}
    city_state = city.split('$split$')
    entry['city'] = city_state[0]
    entry['state'] = city_state[1]
    entry['venues'] = []
    for venue in cities_dict[city]:
      venue_dict = {}
      venue_dict['id'] = venue.id
      venue_dict['name'] = venue.name
      venue_dict['num_upcoming_shows'] = venue.num_upcoming_shows()
      entry['venues'].append(venue)
    data.append(entry)

  return render_template('pages/venues.html', areas=data)

#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  #queries venues with ilike filter on the search term then construct the required dictionary
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  response={}
  response['count'] = len(venues)
  for venue in venues:
    entry = {}
    entry['id'] = venue.id
    entry['name'] = venue.name
    entry['num_upcoming_shows'] = venue.num_upcoming_shows()
    data.append(entry)
  response['data'] =data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  try:
    venue = Venue.query.get(venue_id)
    data = venue.to_data()
    return render_template('pages/show_venue.html', venue=data)
  except:
    render_template('errors/404.html')

 
  

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    try:
      if(request.form['seeking_talent'] == 'y'):
        venue.seeking_talent = True
      else:
        venue.seeking_talent = False
    except:
        venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' +request.form['name'] + ' Could not be listed.', 'error')
  else:
    flash('Venue ' + request.form['name'] +' was successfully listed.')

  return(redirect(url_for('index')))

#  Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  form = VenueForm()

  return render_template('forms/edit_venue.html', form=form , venue = venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    try:
      if(request.form['seeking_talent'] == 'y'):
        venue.seeking_talent = True
      else:
        venue.seeking_talent = False
    except:
        venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' +request.form['name'] + ' Could not be edited.', 'error')
  else:
    flash('Venue ' + request.form['name'] +' was successfully edited.')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/Delete', methods=['DELETE'])
def delete_venue(venue_id):
  error = False 
  try:  
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:

    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Venue ' +str(venue_id) + ' Could not be listed.', 'error')
    #abort(400)
    return(make_response(jsonify({"error": "Collection not found"}), 404))
  else:
    flash('Venue ' + str(venue_id) +' was successfully deleted.')
    #return render_template('pages/venues.html')
    return(make_response(jsonify({}), 200))

#  Artists Section
#  ----------------------------------------------------------------

#  Show Artists list
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists_list = Artist.query.all()
  data=[]
  for artist in artists_list:
    entry = {'id':artist.id ,'name':artist.name }
    data.append(entry)
  return render_template('pages/artists.html', artists=data)

#  Search Artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  response={}
  response['count'] = len(artists)
  for artist in artists:
    entry = {}
    entry['id'] = artist.id
    entry['name'] = artist.name
    entry['num_upcoming_shows'] = artist.num_upcoming_shows()
    data.append(entry)
  response['data'] =data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given venue_id
  try:
    artist = Artist.query.get(artist_id)
    data = artist.to_data()
    return render_template('pages/show_artist.html', artist=data)
  except:
    render_template('errors/404.html')
  

#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
 
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    try:
      if(request.form['seeking_venues'] == 'y'):
        artist.seeking_venues = True
      else:
        artist.seeking_venues = False
    except:
        artist.seeking_venues = False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. artist ' +request.form['name'] + ' Could not be edited.', 'error')
  else:
    flash('Artist ' + request.form['name'] +' was successfully edited.')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    try:
      if(request.form['seeking_venues'] == 'y'):
        artist.seeking_venues = True
      else:
        artist.seeking_venues = False
    except:
        artist.seeking_venues = False
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. artist ' +request.form['name'] + ' Could not be listed.', 'error')
  else:
    flash('Artist ' + request.form['name'] +' was successfully listed.')
  return(redirect(url_for('index')))

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>/Delete', methods=['DELETE'])
def delete_artist(artist_id):
  error = False 
  try:  
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
  except:

    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Artist ' +str(artist_id) + ' Could not be listed.', 'error')
    #abort(400)
    return(make_response(jsonify({"error": "Collection not found"}), 404))
  else:
    flash('Artist ' + str(artist_id) +' was successfully deleted.')
    #return render_template('pages/venues.html')
    return(make_response(jsonify({}), 200))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[]
  shows = Show.query.order_by(db.desc(Show.start_time)).all()
  for show in shows:
    data.append(
      {
        "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
      }
    )

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  artists_ids = [(artist.id,artist.name+' (id:'+str(artist.id)+')') for artist in Artist.query.all()]
  venues_ids = [(venue.id,venue.name+' (id:'+str(venue.id)+')') for venue in Venue.query.all()]
  form = ShowForm()
  form.venue_id.choices = venues_ids
  form.artist_id.choices = artists_ids
  return render_template('forms/new_show.html', form=form , data={'artists_ids':artists_ids,'venues_ids':venues_ids})

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    show = Show()
    show.start_time = request.form['start_time']
    show.venue_id = request.form['venue_id']
    show.artist_id = request.form['artist_id']
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. show starting at ' +request.form['start_time'] + ' Could not be listed.', 'error')
  else:
    flash('Show starting at' + request.form['start_time'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
