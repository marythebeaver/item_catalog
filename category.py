from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Branditem, User

# IMPORT FOR google login
from flask import session as login_session
import random
import string

# import for Gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# declare my client ID by referencing this client secrets file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "WatchItems"


# Connect to Database and create database session
engine = create_engine('sqlite:///category.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login path
@app.route('/login')
def showLogin():
    # state create 32 characters ramdom code mixed witih uppercase and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# google connect
# Gconnect our serverside function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token, request.arg.token used to examine the state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code (the onetime code)
    code = request.data

    # use the authorization code to exchang it
    # for a object includes access token for my server
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    # if there's erro along the way
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # after having access token, Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # stored_access_token = login_session.get('credentials')
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If all above statements are true, Store
    # The access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Sent request to google  with token to get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = str(data.get('name', 'Unknown'))
    login_session['picture'] = data.get('picture', False)
    login_session['gid'] = data.get('id', False)

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['gid'])

    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Write output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1></br></br>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print "done!"
    print "done!"
    return output


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], gid=login_session[
                   'gid'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(gid=login_session['gid']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(gid):
    try:
        user = session.query(User).filter_by(gid=gid).one()
        return user.id
    except:
        return None


# google disconnect
# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                        json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %\
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['gid']
        del login_session['picture']
        print "user loged out"
        flash("you are successfully logged out")
        return redirect(url_for('showCategories'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('categories_public.html', categories=categories)
    user_id = getUserID(login_session['gid'])
    return render_template('categories.html',
                           categories=categories, user_id=user_id)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        if request.form['name']:
            newCategory = Category(name=request.form['name'],
                                   user_id=login_session['user_id'])
            session.add(newCategory)
            flash('New Category %s Successfully Created' % newCategory.name)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            flash('Name cannot be empty, please enter name')
            return redirect(url_for('newCategory'))
    else:
        return render_template('newCategory.html')


# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        message = "Sorry, the Category can only be edited by the owner"
        return message
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    user_id = getUserID(login_session['gid'])
    # authorization
    if editedCategory.user_id != user_id:
        message = "Sorry, the Category can only be edited by the owner"
        return message
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category is Successfully Edited: %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('editCategory.html', category=editedCategory)
    else:
        return render_template('editCategory.html', category=editedCategory)


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        message = "Sorry, the Category can only be deleted by the owner"
        return message
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    user_id = getUserID(login_session['gid'])

    # authorization
    if categoryToDelete.user_id != user_id:
        message = "Sorry, the Category can only be edited by the owner"
        return message

    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s is Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories'))

    else:
        return render_template(
                    'deleteCategory.html', category=categoryToDelete)


# Show a category's brands
@app.route('/category/<int:category_id>/')
def showBrands(category_id):
    categorytobeshow = session.query(Category).filter_by(id=category_id).one()
    brands = session.query(Branditem).filter_by(cat_id=category_id).all()
    creator = getUserInfo(categorytobeshow.user_id)

    if 'username' not in login_session:
        return render_template('brands_public.html', brands=brands,
                               category=categorytobeshow, creator=creator)
    user_id = getUserID(login_session['gid'])

    if categorytobeshow.user_id != user_id:
        return render_template('brands_public.html', brands=brands,
                               category=categorytobeshow, creator=creator)
    return render_template('brands.html', brands=brands,
                           category=categorytobeshow, creator=creator)


# Add a new brand
@app.route('/category/<int:category_id>/new/', methods=['GET', 'POST'])
def newBrand(category_id):
    CategoryToBeAdd = session.query(Category).filter_by(id=category_id).one()
    # ask user to login to add new brands
    if 'username' not in login_session:
        return "Please login first"
    user_id = getUserID(login_session['gid'])

    # authorization
    if CategoryToBeAdd.user_id != user_id:
        message = "Sorry you are not the owner, you cannot edit this category"
        return message

    if request.method == 'POST':
        newBrand = Branditem(brand=request.form['brand'],
                             description=request.form['description'],
                             cat_id=category_id)
        session.add(newBrand)
        session.commit()
        flash('Brand %s is Successfully Added' % (newBrand.brand))
        return redirect(url_for('showBrands', category_id=category_id))
    else:
        return render_template('newBrand.html', category_id=category_id,
                               category=CategoryToBeAdd)


# Edit a brand
@app.route('/category/<int:category_id>/<int:brand_id>/edit/',
           methods=['GET', 'POST'])
def editBrand(category_id, brand_id):
    editedBrand = session.query(Branditem).filter_by(id=brand_id).one()
    categoryIncludeBrand = session.query(Category).\
        filter_by(id=category_id).one()
    if 'username' not in login_session:
        return "Please login first"

    user_id = getUserID(login_session['gid'])
    # authorization
    if categoryIncludeBrand.user_id != user_id:
        message = "Sorry you are not the owner, you cannot edit the item"
        return message

    if request.method == 'POST':
        if request.form['brand']:
            editedBrand.brand = request.form['brand']
        if request.form['description']:
            editedBrand.description = request.form['description']
        session.add(editedBrand)
        session.commit()
        flash('Brand is Successfully Edited')
        return redirect(url_for('showBrands', category_id=category_id))


    else:
        return render_template('editBrand.html', category_id=category_id,
                               brand_id=brand_id, brand=editedBrand)


# Delete a brand
@app.route('/category/<int:category_id>/<int:brand_id>/delete/',
           methods=['GET', 'POST'])
def deleteBrand(category_id, brand_id):
    BrandToBeDelete = session.query(Branditem).filter_by(id=brand_id).one()
    categoryIncludeBrand = session.query(Category).\
        filter_by(id=category_id).one()

    # authorization
    if 'username' not in login_session:
        return "Please login first"
    user_id = getUserID(login_session['gid'])
    if categoryIncludeBrand.user_id != user_id:
        message = "Sorry you are not the owner, you cannot delete the item"
        return message

    if request.method == 'POST':
        session.delete(BrandToBeDelete)
        session.commit()
        flash('Brand is Successfully Deleted')
        return redirect(url_for('showBrands', category_id=category_id))

    else:
        return render_template('deleteBrand.html', category_id=category_id,
                               brand_id=brand_id, brand=BrandToBeDelete)


# JSON APIs to view Information
@app.route('/categories/JSON')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/category/<int:category_id>/JSON')
def showCategoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    brands = session.query(Branditem).filter_by(cat_id=category_id).all()
    return jsonify(brands=[i.serialize for i in brands])


@app.route('/category/<int:category_id>/<int:brand_id>/JSON')
def menuItemJSON(category_id, brand_id):
    brands = session.query(Branditem).filter_by(cat_id=category_id).all()
    brand = [i for i in brands if i.id == brand_id]
    return jsonify(brand=[i.serialize for i in brand])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
