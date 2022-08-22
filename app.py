#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from sqlalchemy import desc
import  sys
from operator import ge
from os import abort
import dateutil.parser
import datetime
import babel
from flask import render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from sqlalchemy.dialects.postgresql import JSON
from models import *
import phonenumbers

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html',
  venues= Venue.query.order_by(desc(Venue.id)).limit(10).all(),
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  )


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', 
  areas= Area.query.all()
  )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  item = "%{}%".format(search_term)
  response = Venue.query.filter(Venue.name.ilike(item)).all()
  count = Venue.query.filter(Venue.name.ilike(item)).count()
  return render_template('pages/search_venues.html', 
  results= response,
  count = count,
  query = search_term
  )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id'
  today = datetime.now()
  currentDate = today.strftime("%Y-%m-%d")
  return render_template('pages/show_venue.html', 
  venue= Venue.query.get(venue_id),
  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < currentDate).all(),
  past_shows_count = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < currentDate).count(),
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > currentDate).all(),
  upcoming_shows_count = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > currentDate).count()
  )


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  newForm = VenueForm()
  error = False

  #Function to validate phone number
  def validatePhone(phone):
    phone_number = phonenumbers.parse(phone)
    print(phonenumbers.is_possible_number(phone_number))
    if phonenumbers.is_possible_number(phone_number) == False:
        return False
    return True

  try:
    venue = Venue(
      name = newForm.name.data,
      city = newForm.city.data,
      state = newForm.state.data,
      address =newForm.address.data,
      phone = newForm.phone.data,
      image_link =newForm.image_link.data,
      genres = newForm.genres.data,
      facebook_link = newForm.facebook_link.data,
      seeking_description = newForm.seeking_description.data,
      seeking_talent = newForm.seeking_talent.data,
      website = newForm.website_link.data
    )  
    phone = newForm.phone.data
    if validatePhone(phone) == True:

      db.session.add(venue) 
      db.session.commit()
      
      # AREA LOGIC #
      city = newForm.city.data
      state = newForm.state.data
      venueIds = []

      for venue in Venue.query.all():
        venueIds.append(venue.id)
    
      venueNum = len(venueIds)
      currentVenueId = venueIds[venueNum - 1]
      currentVenue = Venue.query.get(currentVenueId)

      #Check if area already exists in db
      for area in Area.query.all():
        if area.city == city and area.state == state:
              venue_query = Venue.query.filter_by(id = currentVenueId)
              data_to_update = dict(
                area = area.id
              )
              venue_query.update(data_to_update)
              db.session.commit()
              break

      #Check if no area was found in the db matching the area user entered
      if currentVenue.area == None:
        #Create new area
        area = Area(
          city = city,
          state = state
        )
        db.session.add(area)
        db.session.commit()
      
        #Fetch latest area Id
        AreaIds = []

        for area in Area.query.all():
          AreaIds.append(area.id)
      
        areaNum = len(AreaIds)
        currentAreaId = AreaIds[areaNum - 1]

        #Give new area id to venue
        venue_query = Venue.query.filter_by(id = currentVenueId)  
        data_to_update = dict(
        area = currentAreaId
        )
        venue_query.update(data_to_update)
        db.session.commit()
    
      flash('The Venue ' + newForm.name.data + ' has successfully been listed')
    else:
      error  = True
  except:
    if error == True:
      flash('The phone number you entered was invalid')
      
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Venue ' + newForm.name.data + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html',
  venues= Venue.query.order_by(desc(Venue.id)).limit(10).all(),
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  )
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
    flash('The venue was successfully deleted')
  except:
    print(sys.exc_info()) 
    db.session.rollback()
    flash('The venue failed to be deleted')
  finally:
    db.session.close()
  return render_template('pages/home.html',
  venues= Venue.query.order_by(desc(Venue.id)).limit(10).all(),
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  )
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', 
  artists=Artist.query.all()
  )

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.newForm.get('search_term', '')
  item = "%{}%".format(search_term)
  response = Artist.query.filter(Artist.name.ilike(item)).all()
  count = Artist.query.filter(Artist.name.ilike(item)).count()
  return render_template('pages/search_artists.html', 
  results= response,
  count = count,
  query = search_term
  )

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  today = datetime.now()
  currentDate = today.strftime("%Y-%m-%d")
  return render_template('pages/show_artist.html', 
  artist=Artist.query.get(artist_id),
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < currentDate).all(),
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < currentDate).count(),
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > currentDate).all(),
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > currentDate).count()
  )

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    artist_query = Artist.query.filter_by(id= artist_id)
    data_to_update = dict(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
    )

    phone = form.phone.data
      #Function to validate phone number
    def validatePhone(phone):
      phone_number = phonenumbers.parse(phone)
      print(phonenumbers.is_possible_number(phone_number))
      if phonenumbers.is_possible_number(phone_number) == False:
          return False
      return True

    if validatePhone(phone) == True:

      artist_query.update(data_to_update)
      
      db.session.commit()

      flash('Artist was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()
    venue_query = Venue.query.filter_by(id= venue_id)
    data_to_update = dict(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
    )
    phone = form.phone.data
      #Function to validate phone number
    def validatePhone(phone):
      phone_number = phonenumbers.parse(phone)
      print(phonenumbers.is_possible_number(phone_number))
      if phonenumbers.is_possible_number(phone_number) == False:
          return False
      return True

    if validatePhone(phone) == True:
      venue_query.update(data_to_update)
      
      db.session.commit()

      flash('Venue was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue  could not be updated.')
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  newForm = ArtistForm()

  try:
    artist = Artist(
      name = newForm.name.data,
      city = newForm.city.data,
      state = newForm.state.data,
      phone = newForm.phone.data,
      image_link =newForm.image_link.data,
      genres = newForm.genres.data,
      facebook_link = newForm.facebook_link.data,
      seeking_description = newForm.seeking_description.data,
      seeking_venue = newForm.seeking_venue.data,
      website = newForm.website_link.data
      ) 
    phone = newForm.phone.data
      #Function to validate phone number
    def validatePhone(phone):
      phone_number = phonenumbers.parse(phone)
      print(phonenumbers.is_possible_number(phone_number))
      if phonenumbers.is_possible_number(phone_number) == False:
          return False
      return True

    if validatePhone(phone) == True:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + newForm.name.data + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html',
  venues= Venue.query.order_by(desc(Venue.id)).limit(10).all(),
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  )


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders newForm. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
  form = ShowForm()
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data

    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html',
  venues= Venue.query.order_by(desc(Venue.id)).limit(10).all(),
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  )

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
