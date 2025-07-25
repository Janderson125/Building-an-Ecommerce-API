from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    # Replace YOUR_PASSWORD with your actual MySQL root password
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Austin78702!@localhost/ecommerce_api'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)

    api = Api(app, version='1.0', title='E-Commerce API',
              description='An API for managing Users, Products, and Orders',
              doc='/')  # Swagger UI at /

    # Import your namespaces from route files
    from routes.user_routes import ns as user_ns
    from routes.product_routes import ns as product_ns
    from routes.order_routes import ns as order_ns

    # Register namespaces with URL prefixes
    api.add_namespace(user_ns, path='/users')
    api.add_namespace(product_ns, path='/products')
    api.add_namespace(order_ns, path='/orders')

    @app.route('/health')
    def health():
        return jsonify({"message": "API is running!"})

    with app.app_context():
        db.create_all()  # Creates tables if they don't exist

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
