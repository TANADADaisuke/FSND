#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database -> DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate -> DONE

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate -> DONE

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. -> DONE

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. -> DONE
  data = []
  # select state
  state_list = []
  venues = Venue.query.all()
  for venue in venues:
    state = venue.state
    if state in state_list:
      continue
    else:
      state_list.append(state)
  # for each state, list cities and venues inside it.
  for state in state_list:
    venues = Venue.query.filter(Venue.state == state)
    # select city
    city_list = []
    for venue in venues:
      city = venue.city
      if city in city_list:
        continue
      else:
        city_list.append(city)
    # list all venues in each city
    for city in city_list:
      data_item = {}
      data_item['city'] = city
      data_item['state'] = state
      venues = Venue.query.filter(Venue.city == city)
      venues_in_city = []
      for venue in venues:
        venue_item = {}
        venue_item['id'] = venue.id
        venue_item['name'] = venue.name
        shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.time >= datetime.utcnow())
        # shows = Show.query.filter(Show.venue_id == id).filter(Show.time >= '2020-05-06 12:00:00')
        venue_item['num_upcoming_shows'] = shows.count()
        venues_in_city.append(venue_item)
      data_item['venues'] = venues_in_city
      data.append(data_item)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # -> DONE
  response = {}
  response_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%' + response_term + '%'))
  count = venues.count()
  response['count'] = count
  data = []
  for venue in venues:
    venue_item = {}
    id = venue.id
    name = venue.name
    venue_item['id'] = id
    venue_item['name'] = name
    shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.time >= datetime.utcnow())
    venue_item['num_upcoming_shows'] = shows.count()
    data.append(venue_item)
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id -> DONE.
  venue = Venue.query.get(venue_id)
  # query venue data
  data = {}
  id = venue.id
  name = venue.name
  genres = venue.genres
  address = venue.address
  city = venue.city
  state = venue.state
  phone = venue.phone
  website = venue.website
  facebook_link = venue.facebook_link
  data['id'] = id
  data['name'] = name
  data['genres'] = genres
  data['city'] = city
  data['state'] = state
  data['phone'] = phone
  data['website'] = website
  data['facebook_link'] = facebook_link
  seeking_talent = venue.seeking_talent
  data['seeking_talent'] = seeking_talent
  if seeking_talent:
    seeking_description = venue.seeking_description
    data['seeking_description'] = seeking_description
  image_link = venue.image_link
  data['image_link'] = image_link
  # query shows data
  shows = Show.query.join(Show.artist).filter(Show.venue_id == venue_id)
  past_show_list = []
  upcoming_show_list = []
  past_shows = shows.filter(Show.time < datetime.utcnow())
  past_shows_count = past_shows.count()
  # print(type(past_shows), len(past_shows))
  upcoming_shows = shows.filter(Show.time >= datetime.utcnow())
  upcoming_shows_count = upcoming_shows.count()
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count
  for past_show in past_shows:
    past_show_item = {}
    artist_id = past_show.artist_id
    artist_name = past_show.artist.name
    artist_image_link = past_show.artist.image_link
    start_time = past_show.time
    past_show_item['artist_id'] = artist_id
    past_show_item['artist_name'] = artist_name
    past_show_item['artist_image_link'] = artist_image_link
    past_show_item['start_time'] = str(start_time)
    past_show_list.append(past_show_item)
  data['past_shows'] = past_show_list
  for upcoming_show in upcoming_shows:
    upcoming_show_item = {}
    artist_id = upcoming_show.artist_id
    artist_name = upcoming_show.artist.name
    artist_image_link = upcoming_show.artist.image_link
    start_time = upcoming_show.time
    upcoming_show_item['artist_id'] = artist_id
    upcoming_show_item['artist_name'] = artist_name
    upcoming_show_item['artist_image_link'] = artist_image_link
    upcoming_show_item['start_time'] = str(start_time)
    upcoming_show_list.append(upcoming_show_item)
  data['upcoming_shows'] = upcoming_show_list

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead -> DONE
  # TODO: modify data to be the data object returned from db insertion -> DONE
  error = False
  # initialize data dectionally
  try:
    new_venue = VenueForm(request.form)
    name = new_venue.name.data
    city = new_venue.city.data
    state = new_venue.state.data
    address = new_venue.address.data
    phone = new_venue.phone.data
    genres = new_venue.genres.data
    facebook_link = new_venue.facebook_link.data

    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      facebook_link=facebook_link,
      genres=genres
    )
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead. -> DONE
    flash('An error occurred. Venue ' + new_venue.name.data + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database -> DONE
  data = []
  artists = Artist.query.all()
  # list artist id and name
  for artist in artists:
    data_item = {}
    data_item['id'] = artist.id
    data_item['name'] = artist.name
    data.append(data_item)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # -> DONE.
  response_term = request.form.get('search_term')
  response = {}
  artists = Artist.query.filter(Artist.name.ilike('%' + response_term + '%'))
  count = artists.count()
  response['count'] = count
  data = []
  for artist in artists:
    artist_item = {}
    id = artist.id
    name = artist.name
    artist_item['id'] = id
    artist_item['name'] = name
    shows = Show.query.filter(Show.artist_id == artist.id).filter(Show.time >= datetime.utcnow())
    artist_item['num_upcoming_shows'] = shows.count()
    data.append(artist_item)
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id -> DONE.
  data = {}
  artist = Artist.query.get(artist_id)
  # artist query
  id = artist.id
  name = artist.name
  genres = artist.genres
  city = artist.city
  state = artist.state
  phone = artist.phone
  website = artist.website
  facebook_link = artist.facebook_link
  seeking_venue = artist.seeking_venue
  data['id'] = id
  data['name'] = name
  data['genres'] = genres
  data['city'] = city
  data['state'] = state
  data['phone'] = phone
  data['website'] = website
  data['facebook_link'] = facebook_link
  data['seeking_venue'] = seeking_venue
  if seeking_venue:
    seeking_description = artist.seeking_description
    data['seeking_description'] = seeking_description
  image_link = artist.image_link
  data['image_link'] = image_link
  # shows query
  shows = Show.query.join(Show.venue).filter(Show.artist_id == artist_id)
  past_shows = shows.filter(Show.time < datetime.utcnow())
  upcoming_shows = shows.filter(Show.time >= datetime.utcnow())
  data['past_shows_count'] = past_shows.count()
  data['upcoming_shows_count'] = upcoming_shows.count()
  past_show_list = []
  upcoming_show_list = []
  for past_show in past_shows:
    past_show_item = {}
    venue_id = past_show.venue_id
    venue_name = past_show.venue.name
    venue_image_link = past_show.venue.image_link
    start_time = past_show.time
    past_show_item['venue_id'] = venue_id
    past_show_item['venue_name'] = venue_name
    past_show_item['venue_image_link'] = venue_image_link
    past_show_item['start_time'] = str(start_time)
    past_show_list.append(past_show_item)
  data['past_shows'] = past_show_list
  for upcoming_show in upcoming_shows:
    upcoming_show_item = {}
    venue_id = upcoming_show.venue_id
    venue_name = upcoming_show.venue.name
    venue_image_link = upcoming_show.venue.image_link
    start_time = upcoming_show.time
    upcoming_show_item['venue_id'] = venue_id
    upcoming_show_item['venue_name'] = venue_name
    upcoming_show_item['venue_image_link'] = venue_image_link
    upcoming_show_item['start_time'] = str(start_time)
    upcoming_show_list.append(upcoming_show_item)
  data['upcoming_shows'] = upcoming_show_list

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  # TODO: populate form with fields from artist with ID <artist_id> -> DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  # TODO: populate form with values from venue with ID <venue_id> -> DONE
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # -> DONE
  error = False
  # get submission data from Venue form
  try:
    submission_data = VenueForm(request.form)
    name = submission_data.name.data
    city = submission_data.city.data
    state = submission_data.state.data
    address = submission_data.address.data
    phone = submission_data.phone.data
    genres = submission_data.genres.data
    facebook_link = submission_data.facebook_link.data
    print('name:', name)
    print('city:', city)
    print('state:', state)
    print('address:', address)
    print('phone:', phone)
    print('genres:', genres)
    print('facebook_link:', facebook_link)
    # update venue values
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead -> DONE
  # TODO: modify data to be the data object returned from db insertion -> DONE
  error = False
  # initialize data dectionally
  try:
    new_artist = ArtistForm(request.form)
    name = new_artist.name.data
    city = new_artist.city.data
    state = new_artist.state.data
    phone = new_artist.phone.data
    genres = new_artist.genres.data
    facebook_link = new_artist.facebook_link.data

    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      facebook_link=facebook_link,
      genres=genres
    )
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_artist.name.data + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. ->DONE.
  data = []
  shows = Show.query.all()
  venues = Venue.query.all()
  artists = Artist.query.all()
  # list venue_id, venue_name, artist_id, artist_name, atrist_image_link, start_time for each show
  for show in shows:
    data_item = {}
    # venue data
    venue_id = show.venue_id
    venue_name = Venue.query.get(venue_id).name
    data_item['venue_id'] = venue_id
    data_item['venue_name'] = venue_name
    # artist data
    artist_id = show.artist_id
    artist = Artist.query.get(artist_id)
    artist_name = artist.name
    artist_image_link = artist.image_link
    data_item['artist_id'] = artist_id
    data_item['artist_name'] = artist_name
    data_item['artist_image_link'] = artist_image_link
    # show data
    start_time = str(show.time)
    data_item['start_time'] = start_time
    data.append(data_item)
  print(data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead -> DONE
  error = False
  try:
    new_show = ShowForm(request.form)
    artist_id = new_show.artist_id.data
    venue_id = new_show.venue_id.data
    start_time = new_show.start_time.data

    show = Show(time = start_time)
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    show.artist = artist
    show.venue = venue
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
