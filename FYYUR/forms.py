from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField, SelectField, SelectMultipleField, DateTimeField,TextAreaField,BooleanField
from wtforms.validators import DataRequired, URL,ValidationError
from wtforms.widgets.html5 import NumberInput,DateTimeLocalInput,TelInput,URLInput
from wtforms.fields.html5 import TelField
from choices import state_choices , genre_choices

def validate_phone(form,phone):
    if(len(str(phone.data))):
        try:
            number = str(phone.data).replace('-','')
            check = int(number)
            if (len(number)!=10):
                raise ValidationError('Invalid phone number length should be 10 digits separated by "-" (also accepts blanks)')
        except:
            raise ValidationError('Invalid phone number length should be 10 digits separated by "-" (also accepts blanks)')

class ShowForm(FlaskForm):
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
    phone = StringField(
        'phone',validators=[validate_phone]
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
        

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],choices=state_choices
    )
    phone = StringField(
        'phone',validators=[validate_phone]
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

