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
    ##
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
    ## 
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

##
class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.String, nullable=False)

    #def __repr__(self):
    #    return '<Post %r>' % self.title
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

#
#  Venues
#  ----------------------------------------------------------------
def output_format(input_list, venAr):
  return_list = []
  
  for elem in input_list:
    elem_show_format = {}
    elem_show_format['id'] = elem.id
    elem_show_format['name'] = elem.name
    start_time = now_string()
    if venAr:
      elem_show_format['num_upcoming_shows'] = Shows.query.filter(Shows.venue_id==elem.id, Shows.start_time>start_time ).count()
    else:
      elem_show_format['num_upcoming_shows'] = Shows.query.filter(Shows.artist_id==elem.id, Shows.start_time>start_time ).count()
    return_list.append(elem_show_format)

  return return_list


@app.route('/venues')
def venues():  #TODO: check if the orginal webpage looked any different
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


@app.route('/venues/<int:venue_id>') ## debug and make it work in a better way 
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
  error = None
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    data = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link)
    dataG = request.form['genres']
    #print ("genre_data",dataG)
    db.session.add(data)
    db.session.flush()
    genre_data = Genres(genre=dataG, venue_id=data.id) ##  need to know how to add multiple genres
    db.session.add(genre_data)
    db.session.commit()
    db.session.close()
  except:
    error = 'ERROR: Venue ' + request.form['name'] + ' was not successfully'
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error==None:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html', error=error)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    objDel = Venue.query.filter_by(id=venue_id).first() 
    db.session.delete(objDel)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  return error #render_template('pages/home.html', error=error)

    
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = None
  try:
    data = Venue.query.get(venue_id)
    data.name = request.form['name']
    data.city = request.form['city']
    data.state = request.form['state']
    data.address = request.form['address']
    data.phone = request.form['phone']
    data.facebook_link = request.form['facebook_link']
    #data.seeking_talent = request.form['seeking_talent']
    #data.seeking_description = request.form['seeking_description']
    #data.website = request.form['website']
    #data.image_link = request.form['image_link']
    db.session.commit()
    db.session.close()
  except:
    error = 'ERROR: Venue ' + request.form['name'] + ' was not successfully updated'
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error==None:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
  form = VenueForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = None
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    #address = request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    data = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link)# , address=address)
    db.session.add(data)
    db.session.commit()
    db.session.close()
  except:
    error = 'ERROR: Artist ' + request.form['name'] + ' was not successfully'
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error==None:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html', error=error)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = None
  try:
    data = Artist.query.get(artist_id)
    data.name = request.form['name']
    data.city = request.form['city']
    data.state = request.form['state']
    #data.address = request.form['address']
    data.phone = request.form['phone']
    data.facebook_link = request.form['facebook_link']
    #data.seeking_talent = request.form['seeking_talent']
    #data.seeking_description = request.form['seeking_description']
    #data.website = request.form['website']
    #data.image_link = request.form['image_link']
    db.session.commit()
    db.session.close()
  except:
    error = 'ERROR: Artist ' + request.form['name'] + ' was not successfully updated'
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error==None:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  try:
    objDel = Artist.query.filter_by(id=artist_id).first() 
    db.session.delete(objDel)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  return error #render_template('pages/home.html', error=error)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
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
