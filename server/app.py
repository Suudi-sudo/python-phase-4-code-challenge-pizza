#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"


# Routes
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    response = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants]
    return make_response(jsonify(response), 200)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)  
    if restaurant:
        response = restaurant.to_dict(rules=("-restaurant_pizzas.restaurant", "restaurant_pizzas.pizza"))
        return make_response(jsonify(response), 200)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]
    return make_response(jsonify(response), 200)


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]

        # Validation
        if price < 1 or price > 30:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)  

        # Checking if pizza and restaurant exist
        pizza = db.session.get(Pizza, pizza_id)  
        restaurant = db.session.get(Restaurant, restaurant_id)  
        if not pizza or not restaurant:
            return make_response(jsonify({"errors": ["Pizza or Restaurant not found"]}), 400)

        # Creating the RestaurantPizza
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        response = restaurant_pizza.to_dict(rules=("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas"))
        return make_response(jsonify(response), 201)

    except KeyError:
        return make_response(jsonify({"errors": ["Missing required fields"]}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
