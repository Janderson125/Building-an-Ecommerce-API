from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import Order, Product, User
from schemas import OrderSchema

ns = Namespace('orders', description='Order related operations')

order_model = ns.model('Order', {
    'user_id': fields.Integer(required=True, description='ID of the user placing the order'),
    'order_date': fields.DateTime(required=False, description="ISO format datetime string, optional"),
})

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@ns.route('/')
class OrderList(Resource):
    @ns.marshal_list_with(order_model)
    def get(self):
        """List all orders"""
        orders = Order.query.all()
        return orders_schema.dump(orders)

    @ns.expect(order_model, validate=True)
    @ns.marshal_with(order_model, code=201)
    def post(self):
        """Create a new order"""
        data = request.json
        user = User.query.get(data['user_id'])
        if not user:
            ns.abort(404, "User not found")
        
        from datetime import datetime
        order_date = data.get('order_date')
        if order_date:
            try:
                order_date = datetime.fromisoformat(order_date)
            except Exception:
                ns.abort(400, "Invalid date format, use ISO format.")
        else:
            order_date = None
        
        order = Order(user_id=user.id, order_date=order_date)
        db.session.add(order)
        db.session.commit()
        return order_schema.dump(order), 201

@ns.route('/<int:order_id>/add_product/<int:product_id>')
@ns.param('order_id', 'The order identifier')
@ns.param('product_id', 'The product identifier')
@ns.response(404, 'Order or Product not found')
class AddProduct(Resource):
    @ns.marshal_with(order_model)
    def put(self, order_id, product_id):
        """Add a product to an order"""
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        if product in order.products:
            ns.abort(400, "Product already added to order.")
        order.products.append(product)
        db.session.commit()
        return order_schema.dump(order)

@ns.route('/<int:order_id>/remove_product/<int:product_id>')
@ns.param('order_id', 'The order identifier')
@ns.param('product_id', 'The product identifier')
@ns.response(404, 'Order or Product not found')
class RemoveProduct(Resource):
    @ns.response(204, 'Product removed from order')
    def delete(self, order_id, product_id):
        """Remove a product from an order"""
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        if product not in order.products:
            ns.abort(404, "Product not in order.")
        order.products.remove(product)
        db.session.commit()
        return '', 204

@ns.route('/user/<int:user_id>')
@ns.param('user_id', 'The user identifier')
class OrdersByUser(Resource):
    @ns.marshal_list_with(order_model)
    def get(self, user_id):
        """Get all orders by a user"""
        orders = Order.query.filter_by(user_id=user_id).all()
        return orders_schema.dump(orders)

@ns.route('/<int:order_id>/products')
@ns.param('order_id', 'The order identifier')
@ns.response(404, 'Order not found')
class ProductsByOrder(Resource):
    def get(self, order_id):
        """Get products in an order"""
        order = Order.query.get_or_404(order_id)
        # Return list of products using product schema
        return [product for product in order.products]
