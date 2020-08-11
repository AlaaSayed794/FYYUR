from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField, SelectField, SelectMultipleField, DateTimeField,TextAreaField,BooleanField
from wtforms.validators import DataRequired, AnyOf, URL,NumberRange,ValidationError,InputRequired
from wtforms.widgets.html5 import NumberInput,DateTimeLocalInput,TelInput,URLInput
from wtforms.fields.html5 import TelField
from choices import state_choices , genre_choices
import phonenumbers

def validate_phone(form,phone):
    if(len(phone.data)):
        try:
            number = phonenumbers.parse(phone.data, None)
            print('validation : ')
            print(phonenumbers.is_valid_number(number))
            if(not phonenumbers.is_valid_number(number)):
                print('Im called1')
                raise ValidationError('Please enter a valid phone number')
        except:
            print('Im called2')
            raise ValidationError('Please enter a valid phone number')

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
        'phone',validators=[validate_phone],widget=TelInput()
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

