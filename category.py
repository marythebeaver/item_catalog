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





if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
