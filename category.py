from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Branditem, User

#IMPORT FOR google login
from flask import session as login_session
import random, string

#import for Gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)



#Connect to Database and create database session
engine = create_engine('sqlite:///category.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#fake data
category = {'id': '1', 'name': 'Independent Watchmaker'}
categories = [{'id': '1', 'name': 'Independent Watchmaker'}, {
    'id': '2', 'name': 'Manufactor Watch Brand'}]
items = [{'cat_id': '1', 'id': '1', 'brand': 'Akrivia', 'description': 'Founded by Reshep'}, {
    'cat_id': '1', 'id': '2', 'brand': 'Kari Voutilainen', 'description': 'Founded by Kari'}, {
    'cat_id': '2', 'id': '3', 'brand': 'Patek Philippe', 'description': 'Founded by Antoni Patek and Adrien Philippe'}, {
    'cat_id': '2', 'id': '4', 'brand': 'Rolex', 'description': 'Founded by Hans Wilsdorf'}]
item = {'cat_id': '1', 'id': '1', 'brand': 'Akrivia', 'description': 'Founded by Reshep'}

#show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('categories.html', categories = categories)


#Create a new category
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():

  if request.method == 'POST':
      return "will add a new"
  else:
      return render_template('newCategory.html')

#Edit a category
@app.route('/category/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
  editedCategory = category
  if request.method == 'POST':
    return "this will allow you to edit category"
  else:
    return render_template('editCategory.html', category = editedCategory)

#Delete a category
@app.route('/category/<int:category_id>/delete/', methods = ['GET','POST'])
def deleteCategory(category_id):
  categoryToDelete = category

  if request.method == 'POST':
    return "this will allow you to delete category"
  else:
    return render_template('deleteCategory.html',category = categoryToDelete)

#Show a category's brands
@app.route('/category/<int:category_id>/')
def showBrands(category_id):
    brands = items
    categorytobeshow = category
    return render_template('brands.html', brands = items, category = categorytobeshow)

#Add a new brand
@app.route('/category/<int:category_id>/new/',methods=['GET','POST'])
def newBrand(category_id):
  CategoryToBeAdd = category

  if request.method == 'POST':
     return "this will allow you to add new brand"
  else:
     return render_template('newBrand.html', category_id = category_id, category=CategoryToBeAdd)

#Edit a brand
@app.route('/category/<int:category_id>/<int:brand_id>/edit/', methods=['GET','POST'])
def editBrand(category_id, brand_id):

    editedBrand = item
    categoryIncludeBrand = category


    if request.method == 'POST':
        return "this will allow you to edit this brand"
    else:
        return render_template('editBrand.html', category_id = category_id, brand_id = brand_id, brand = editedBrand)


#Delete a brand
@app.route('/category/<int:category_id>/<int:brand_id>/delete/', methods = ['GET','POST'])
def deleteBrand(category_id,brand_id):

    editedBrand = item
    categoryIncludeBrand = category

    if request.method == 'POST':
        return "this will allow you to delete this brand"
    else:
        return render_template('deleteBrand.html', category_id = category_id, brand_id = brand_id, brand = editedBrand)


if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
