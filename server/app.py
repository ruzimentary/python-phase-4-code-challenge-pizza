#!/usr/bin/env python3
import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

# Base directory and database setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Routes
@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{"address": r.address, "id": r.id, "name": r.name} for r in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    return jsonify({
        "address": restaurant.address,
        "id": restaurant.id,
        "name": restaurant.name,
        "restaurant_pizzas": [{
            "id": rp.id,
            "pizza": {
                "id": rp.pizza.id,
                "ingredients": rp.pizza.ingredients,
                "name": rp.pizza.name
            },
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id
        } for rp in restaurant.restaurant_pizzas]
    })

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({"message": "Restaurant deleted successfully"}), 204

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{"id": p.id, "ingredients": p.ingredients, "name": p.name} for p in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizza():
    data = request.get_json()
    restaurant = Restaurant.query.get(data.get('restaurant_id'))
    pizza = Pizza.query.get(data.get('pizza_id'))
    if not restaurant or not pizza:
        return jsonify({"errors": ["validation errors"]}), 400
    new_restaurant_pizza = RestaurantPizza(price=data['price'], pizza_id=pizza.id, restaurant_id=restaurant.id)
    db.session.add(new_restaurant_pizza)
    db.session.commit()
    return jsonify({
        "id": new_restaurant_pizza.id,
        "pizza": {"id": pizza.id, "ingredients": pizza.ingredients, "name": pizza.name},
        "pizza_id": pizza.id,
        "price": new_restaurant_pizza.price,
        "restaurant": {"address": restaurant.address, "id": restaurant.id, "name": restaurant.name},
        "restaurant_id": restaurant.id
    }), 201

# Run the application
if __name__ == "__main__":
    app.run(port=5555, debug=True)
