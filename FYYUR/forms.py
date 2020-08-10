from datetime import datetime
from flask_wtf import Form,FlaskForm
from wtforms import StringField,IntegerField, SelectField, SelectMultipleField, DateTimeField,TextAreaField,BooleanField
from wtforms.validators import DataRequired, AnyOf, URL,NumberRange,ValidationError
from wtforms.widgets.html5 import NumberInput,DateTimeLocalInput,TelInput,URLInput
from wtforms.fields.html5 import TelField
from choices import state_choices , genre_choices
class ShowForm(Form):
    artist_id = SelectField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = SelectField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],format=('%y/%m/%d %H:%M'), widget=DateTimeLocalInput()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = TelField(
        'phone',widget=TelInput()
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()] , widget=URLInput()
    )
    website = StringField(
        'website', validators=[URL()] , widget=URLInput()
    )
    image_link = StringField(
        'image_link', validators=[URL()] , widget=URLInput()
    )
    seeking_talent = BooleanField('seeking_talent')
    seeking_description = TextAreaField('seeking_description')
    def validate_name(self,name):
        raise ValidationError('That username is taken. Please choose another.')

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],choices=state_choices
    )
    phone = TelField(
        
        'phone',widget=TelInput(input_type='tel')
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()] , widget=URLInput()
    )
    website = StringField(
        'website', validators=[URL()] , widget=URLInput()
    )
    image_link = StringField(
        'image_link', validators=[URL()] , widget=URLInput()
    )
    seeking_venues = BooleanField('seeking_venues')
    seeking_description = TextAreaField('seeking_description')
