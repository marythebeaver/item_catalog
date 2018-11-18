from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)




#fake data
category = {'id': '1', 'name': 'Independent Watchmaker'}
categories = [{'id': '1', 'name': 'Independent Watchmaker'}, {
    'id': '2', 'name': 'Manufactor Watch Brand'}]
items = [{'cat_id': '1', 'id': '1', 'brand': 'Akrivia', 'description': 'Founded by Reshep'}, {
    'cat_id': '1', 'id': '2', 'brand': 'Kari Voutilainen', 'description': 'Founded by Kari'}, {
    'cat_id': '2', 'id': '1', 'brand': 'Patek Philippe', 'description': 'Founded by Antoni Patek and Adrien Philippe'}, {
    'cat_id': '2', 'id': '2', 'brand': 'Rolex', 'description': 'Founded by Hans Wilsdorf'}]

#show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
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



if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
