#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('Genres', backref='e_venue', cascade="all, delete-orphan", lazy=True)

class Genres(db.Model):
  __tablename__ = 'Genres'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  genre = db.Column(db.String)
  def __repr__(self):
    return '%r' % self.genre

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120)) 
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('Artist_Genres', backref='e_artist', cascade="all, delete-orphan", lazy=True)

class Artist_Genres(db.Model):
  __tablename__ = 'Artist_Genres'

  id = db.Column(db.Integer,primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  genre = db.Column(db.String)
  def __repr__(self):
    return '%r' % self.genre

class Shows(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='SET NULL'), nullable=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='SET NULL'), nullable=True)
  start_time = db.Column(db.String, nullable=False)


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

def now_string():
  now = datetime.now()
  return now.strftime(" %Y/%m/%d, %H:%M:%S")

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def output_format(input_list, venAr):

  return_list = []
  for elem in input_list:
    elem_show_format = {}
    elem_show_format['id'] = elem.id
    elem_show_format['name'] = elem.name
    start_time = now_string()
    if venAr==1:
      elem_show_format['num_upcoming_shows'] = Shows.query.filter(Shows.venue_id==elem.id, Shows.start_time>start_time ).count()
    elif venAr==0:
      elem_show_format['num_upcoming_shows'] = Shows.query.filter(Shows.artist_id==elem.id, Shows.start_time>start_time ).count()
    else:
      elem_show_format['start_time'] = format_datetime(elem.start_time)
    return_list.append(elem_show_format)

  return return_list


@app.route('/venues')
def venues(): 

  data = []
  city_list = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for elem in city_list:
    data_elem = {}
    data_elem['city'] = elem.city
    data_elem['state'] = elem.state
    venue_city_list = Venue.query.with_entities(Venue.id,Venue.name).filter_by( city=elem.city, state=elem.state ).all()
    venue_query =  output_format(venue_city_list,1)
    data_elem['venues'] = venue_query
    data.append(data_elem)

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():

  response = {}
  search_term = request.form.get('search_term', '')
  search_list = Venue.query.with_entities(Venue.id,Venue.name).filter( func.lower(Venue.name).like('%'+func.lower(search_term)+'%') ).all()
  response['count'] = len(search_list)
  if search_list:
    response['data'] = output_format(search_list,1)

  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):  

  data = {}
  data = vars(Venue.query.filter_by( id=venue_id ).first())
  data['genres'] = Genres.query.filter_by(venue_id = venue_id).all()
  start_time = now_string()
  data['past_shows'] = Shows.query.join(Artist, Shows.artist_id==Artist.id).with_entities(Artist.id.label('artist_id'),Shows.start_time,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link')).filter(Shows.venue_id==venue_id, Shows.start_time<=start_time ).all()
  data['upcoming_shows'] = Shows.query.join(Artist, Shows.artist_id==Artist.id).with_entities(Artist.id.label('artist_id'),Shows.start_time,Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link')).filter(Shows.venue_id==venue_id, Shows.start_time>start_time ).all()
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():

  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  try:
    data = Venue(
                name=request.form['name'], 
                city=request.form['city'], 
                state=request.form['state'], 
                address=request.form['address'], 
                phone=request.form['phone'], 
                facebook_link=request.form['facebook_link'], 
                image_link=request.form['image_link'],
                website=request.form['website'],
                seeking_description = request.form['seeking_description']
                )
    if(request.form['seeking_talent'] == 'y'):
      data.seeking_talent = True
    db.session.add(data)
    db.session.flush()
    for genre in request.form.getlist('genres'): 
      genre_data = Genres(genre=genre, venue_id=data.id)
      db.session.add(genre_data)
    db.session.commit()
    db.session.close()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('ERROR: Venue ' + request.form['name'] + ' was not successfully listed!')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    objDel = Venue.query.filter_by(id=venue_id).first() 
    db.session.delete(objDel)
    db.session.commit()
    flash("The venue was deleted successfully")
  except:
    flash("Something went wrong, the venue couldn't be deleted")
    db.session.rollback()
  finally:
    db.session.close()

  return None

    
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  try:
    data = Venue.query.get(venue_id)
    data.name = request.form['name']
    data.city = request.form['city']
    data.state = request.form['state']
    data.address = request.form['address']
    data.phone = request.form['phone']
    data.facebook_link = request.form['facebook_link']
    if(request.form['seeking_talent'] == 'y'):
      data.seeking_talent = True
    data.seeking_description = request.form['seeking_description']
    data.website = request.form['website']
    data.image_link = request.form['image_link']
    delGenres = Genres.query.filter_by(id=venue_id).all()
    db.session.delete(delGenres)
    for genre in request.form.getlist('genres'): 
      genre_data = Genres(genre=genre, venue_id=venue_id)
      db.session.add(genre_data)
    db.session.commit()
    db.session.close()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    flash('ERROR: Venue ' + request.form['name'] + ' was not successfully updated')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = Artist.query.with_entities(Artist.id,Artist.name).all()

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

  response = {}
  search_term = request.form.get('search_term', '')
  search_list = Artist.query.with_entities(Artist.id,Artist.name).filter( func.lower(Artist.name).like('%'+func.lower(search_term)+'%') ).all()
  response['count'] = len(search_list)
  if search_list:
    response['data'] = output_format(search_list,0)

  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  data = {}
  data = vars(Artist.query.filter_by( id=artist_id ).first())
  data['genres'] = Artist_Genres.query.filter_by(artist_id = artist_id).all()
  start_time = now_string()
  data['past_shows'] = Shows.query.join(Venue, Shows.venue_id==Venue.id).with_entities(Venue.id.label('venue_id'),Shows.start_time.label('start_time'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link')).filter(Shows.artist_id==artist_id, Shows.start_time<=start_time ).all()
  data['upcoming_shows'] = Shows.query.join(Venue, Shows.venue_id==Venue.id).with_entities(Venue.id.label('venue_id'),Shows.start_time.label('start_time'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link')).filter(Shows.artist_id==artist_id, Shows.start_time>start_time ).all()
  
  return render_template('pages/show_artist.html', artist=data) 


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    data = Artist(
                name=request.form['name'], 
                city=request.form['city'], 
                state=request.form['state'],  
                phone=request.form['phone'], 
                facebook_link=request.form['facebook_link'], 
                image_link=request.form['image_link'],
                website=request.form['website'],
                seeking_description = request.form['seeking_description']
                )
    if(request.form['seeking_venue'] == 'y'):
      data.seeking_venue = True
    db.session.add(data)
    db.session.flush()
    for genre in request.form.getlist('genres'): 
      print (genre)
      genre_data = Artist_Genres(genre=genre, artist_id=data.id)
      db.session.add(genre_data)
    db.session.commit()
    db.session.close()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('ERROR: Artist ' + request.form['name'] + ' was not successfully listed')
    db.session.rollback()
  finally:
    db.session.close()
    
  return render_template('pages/home.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    data = Artist.query.get(artist_id)
    data.name = request.form['name']
    data.city = request.form['city']
    data.state = request.form['state']
    data.phone = request.form['phone']
    data.facebook_link = request.form['facebook_link']
    if(request.form['seeking_venue'] == 'y'):
      data.seeking_venue = True
    data.seeking_description = request.form['seeking_description']
    data.website = request.form['website']
    data.image_link = request.form['image_link']
    delGenres = Artist_Genres.query.filter_by(id=artist_id).all()
    db.session.delete(delGenres)
    for genre in request.form.getlist('genres'): 
      genre_data = Artist_Genres(genre=genre, artist_id=artist_id)
      db.session.add(genre_data)
    db.session.commit()
    db.session.close()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    flash('ERROR: Artist ' + request.form['name'] + ' was not successfully updated')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    objDel = Artist.query.filter_by(id=artist_id).first() 
    db.session.delete(objDel)
    db.session.commit()
    flash('The artist was successfully deleted')
  except:
    db.session.rollback()
    flash("Something went wrong, the artist couldn't be deleted")
  finally:
    db.session.close()
   
  return None

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  start_time = now_string()
  shows = Shows.query.filter(Shows.start_time>start_time).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    outShow = {}
    if(venue!=None):
      outShow['venue_id'] = show.venue_id
      outShow['venue_name'] = venue.name
    else:
      outShow['venue_name'] = 'The venue deleted their account'
    if(artist!=None):
      outShow['artist_id'] = show.artist_id
      outShow['artist_name'] = artist.name
      outShow['artist_image_link'] = artist.image_link
    else:
      outShow['artist_name'] = 'The artist deleted their account'
    outShow['start_time'] = show.start_time
    data.append(outShow)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    data = Shows(
             venue_id=request.form['venue_id'], 
             artist_id=request.form['artist_id'],
             start_time=request.form['start_time']
             )
    db.session.add(data)
    db.session.commit()
    db.session.close()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')


## Anusha finish this
@app.route('/shows/search', methods=['POST'])  ## change this and front end to reflect shows correctly 
def search_shows():

  response = {}
  search_term = request.form.get('search_term', '')
  start_time = now_string()
  past_shows_artist = Shows.query.join(Artist, Shows.artist_id==Artist.id).with_entities(Artist.id.label('id'),Shows.start_time.label('start_time'),Artist.name.label('name')).filter(Shows.start_time<=start_time, func.lower(Artist.name).like('%'+func.lower(search_term)+'%') ).all()
  upcoming_shows_artist = Shows.query.join(Artist, Shows.artist_id==Artist.id).with_entities(Artist.id.label('id'),Shows.start_time.label('start_time'),Artist.name.label('name')).filter(Shows.start_time>start_time, func.lower(Artist.name).like('%'+func.lower(search_term)+'%') ).all()
 
  past_shows_venue = Shows.query.join(Venue, Shows.venue_id==Venue.id).with_entities(Venue.id.label('id'),Shows.start_time.label('start_time'),Venue.name.label('name')).filter(Shows.start_time<=start_time, func.lower(Venue.name).like('%'+func.lower(search_term)+'%') ).all()
  upcoming_shows_venue = Shows.query.join(Venue, Shows.venue_id==Venue.id).with_entities(Venue.id.label('id'),Shows.start_time.label('start_time'),Venue.name.label('name')).filter(Shows.start_time>start_time, func.lower(Venue.name).like('%'+func.lower(search_term)+'%') ).all()
 
  response = {}
  if past_shows_venue:
    response['past_venue_data'] = output_format(past_shows_venue,2)
  if upcoming_shows_venue:
    response['upcoming_venue_data'] = output_format(upcoming_shows_venue,2)
  if past_shows_artist:
    response['past_artist_data'] = output_format(past_shows_artist,2)
  if upcoming_shows_artist:
    response['upcoming_artist_data'] = output_format(upcoming_shows_artist,2)
  response['past_shows_count'] = len(past_shows_venue) + len(past_shows_artist)
  response['upcoming_shows_count'] = len(upcoming_shows_artist) + len(upcoming_shows_venue)
  return render_template('pages/search_shows.html', results=response, search_term=search_term)


#------------end of shows -----------------------------------------#


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
