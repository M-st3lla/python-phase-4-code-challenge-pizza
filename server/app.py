#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# retrieve all the restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]), 200
    except Exception as e:
        app.logger.error(f"Error fetching restaurants: {e}")
        return {"error": "An error occurred while fetching restaurants"}, 500

# retrieve or delete a particular restaurant by unique identifier(ID)
@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def handle_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        if request.method == "GET":
            return jsonify(restaurant.to_dict(only=('id', 'name', 'address'))), 200
        
        if request.method == "DELETE":
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
    except Exception as e:
        app.logger.error(f"Error handling restaurant with id {id}: {e}")
        return {"error": "An error occurred while handling the restaurant"}, 500

# retrieve all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]), 200
    except Exception as e:
        app.logger.error(f"Error fetching pizzas: {e}")
        return {"error": "An error occurred while fetching pizzas"}, 500

# create a new restaurant-pizza link
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError as ve:
        app.logger.error(f"Validation error: {ve}")
        return {"errors": ["validation errors"]}, 400
    except Exception as e:
        app.logger.error(f"Error creating restaurant pizza: {e}")
        return {"errors": ["internal server error"]}, 500

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
