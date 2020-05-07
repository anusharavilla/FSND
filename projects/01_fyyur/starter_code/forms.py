from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL
from enum import Enum
class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class genre_options(Enum):
  ALTERNATIVE = 'Alternative'
  BLUES = 'Blues' 
  CLASSICAL =  'Classical'
  COUNTRY = 'Country'
  ELECTRONIC = 'Electronic'
  FOLK = 'Folk'
  FUNK = 'Funk'
  HIP_HOP = 'Hip-Hop'
  HEAVY_METAL = 'Heavy Metal'
  INSTRUMENTAL = 'Instrumental'
  JAZZ = 'Jazz'
  MUSIC_THEATRE = 'Music Theatre'
  POP = 'Pop'
  PUNK = 'Punk'
  RNB = 'R&B'
  REGGAE ='Reggae'
  ROCK_N_ROLL = 'Rock n Roll'
  SOUL = 'Soul'
  OTHER = 'Other'
  
  @classmethod
  def choices(cls):
    return [(choice.value, choice.value) for choice in cls]

state_options = [ 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','MD','MA','MI','MN','MS','MO','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_options
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField('genres', choices = genre_options.choices(), validators=[DataRequired()])
        
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_options
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField('genres', choices = genre_options.choices(), validators=[DataRequired()])
    
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

