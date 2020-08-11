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
from choices import state_choices,genre_choices
#adding migrate import to use it to connect to the database
from flask_migrate import Migrate
from models import Venue, Show, Artist, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# connect to a local postgresql database using flask migrate
migrate = Migrate(app,db)
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

def format_phone(phone):
  phone=phone.replace('-','')
  if(len(phone)==10):
    phone = phone[:3] +'-' +phone[3:6]+'-'+phone[6:]
  return phone

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  #used to populate two tables for recently added artists/venues
  artists = Artist.query.order_by(db.desc(Artist.created_at)).limit(10)
  venues = Venue.query.order_by(db.desc(Venue.created_at)).limit(10)
  
  return render_template('pages/home.html',venues=venues, artists=artists)


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
  form = VenueForm()
  
  
  error = False
  try:
    name = form.name.data
    if(db.session.query(Venue.name).filter_by(name=name).scalar() is not None):
      flash('The venue : "'+ name+'" already exists', 'error')
      return render_template('forms/new_venue.html', form=form)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/new_venue.html', form=form)
    venue = Venue()
    venue.name = name
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = format_phone(form.phone.data)
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
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
  }
  form = VenueForm()
  #populate the form with the venue's data so that the user doesn't have to re enter everything to edit a field
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data =venue.state
  form.state.choices=state_choices
  form.genres.choices.clear()
  form.genres.data = venue.genres
  form.genres.choices = genre_choices
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.image_link.data = venue.image_link
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent

  return render_template('forms/edit_venue.html', form=form , venue = venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  
  form = VenueForm()
  
  venue = Venue.query.get(venue_id)
  try:
    
    name = form.name.data
    if((db.session.query(Venue.name).filter_by(name=name).scalar() is not None)and(venue.name!=name )):
      flash('The venue : "'+ name+'" already exists', 'error')
      return render_template('forms/edit_venue.html', form=form,venue=venue)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/edit_venue.html', form=form,venue=venue)
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = format_phone(form.phone.data)
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    print('seeking talent : ')
    print(form.seeking_talent.data)
    db.session.commit()
  except Exception as e:
    error = True
    print(e)
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
    return(make_response(jsonify({"error": "Object not found"}), 404))
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
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm()
  try:
    name = form.name.data
    if(db.session.query(Artist.name).filter_by(name=name).scalar() is not None):
      flash('The artist : "'+ name+'" already exists', 'error')
      return render_template('forms/new_artist.html', form=form)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/new_artist.html', form=form)
    artist = Artist()
    artist.name = name
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = format_phone(form.phone.data)
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data
    artist.seeking_venues = form.seeking_venues.data
    artist.seeking_description = form.seeking_description.data
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
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data =artist.state
  form.state.choices=state_choices
  form.genres.choices.clear()
  form.genres.data = artist.genres
  form.genres.choices = genre_choices
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.image_link.data = artist.image_link
  form.seeking_description.data = artist.seeking_description
  form.seeking_venues.data = artist.seeking_venues
  
 
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm()
  name = form.name.data
  try:
    artist = Artist.query.get(artist_id)
    if((db.session.query(Artist.name).filter_by(name=name).scalar() is not None)and(artist.name!=name)):
      flash('The artist : "'+ name+'" already exists', 'error')
      return render_template('forms/edit_artist.html', form=form,artist=artist)
    form.validate()
    if(len(form.phone.errors)>0):
      flash(','.join(form.phone.errors))
      return render_template('forms/edit_artist.html', form=form,artist=artist)
    artist.name = name
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = format_phone(form.phone.data)
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website.data
    artist.image_link = form.image_link.data
    artist.seeking_venues = form.seeking_venues.data
    artist.seeking_description = form.seeking_description.data
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
    return(make_response(jsonify({"error": "Object not found"}), 404))
  else:
    flash('Artist ' + str(artist_id) +' was successfully deleted.')
    #return render_template('pages/venues.html')
    return(make_response(jsonify({}), 200))

#  Shows
#  ----------------------------------------------------------------

#  Display Shows
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

#  Create a show
#  ----------------------------------------------------------------
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
  return(redirect(url_for('index')))

#  Cancel a show
#  ----------------------------------------------------------------
@app.route('/shows/<show_id>/Delete', methods=['DELETE'])
def delete_show(show_id):
  print('show delete function')
  error = False 
  try:  
    show = Show.query.get(show_id)
    db.session.delete(show)
    db.session.commit()
  except:

    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occured. Show ' +str(show_id) + ' Could not be deleted.', 'error')
    return(make_response(jsonify({"error": "Object not found"}), 404))
  else:
    flash('Show ' + str(show_id) +' was successfully deleted.')
    return(make_response(jsonify({}), 200))

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
