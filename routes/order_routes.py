from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import Order, Product, User
from schemas import OrderSchema

ns = Namespace('orders', description='Order related operations')

order_model = ns.model('Order', {
    'user_id': fields.Integer(required=True),
    'order_date': fields.DateTime(required=False, description="ISO format datetime string, optional"),
})

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@ns.route('/')
class OrderList(Resource):
    def get(self):
        orders = Order.query.all()
        return orders_schema.dump(orders)
    
    @ns.expect(order_model)
    def post(self):
        data = request.json
        user = User.query.get(data['user_id'])
        if not user:
            return {"message": "User not found"}, 404
        
        from datetime import datetime
        order_date = data.get('order_date')
        if order_date:
            try:
                order_date = datetime.fromisoformat(order_date)
            except Exception:
                return {"message": "Invalid date format, use ISO format."}, 400
        else:
            order_date = None
        
        order = Order(user_id=user.id, order_date=order_date)
        db.session.add(order)
        db.session.commit()
        return order_schema.dump(order), 201

@ns.route('/<int:order_id>/add_product/<int:product_id>')
class AddProduct(Resource):
    def put(self, order_id, product_id):
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        if product in order.products:
            return {"message": "Product already added to order."}, 400
        order.products.append(product)
        db.session.commit()
        return order_schema.dump(order)

@ns.route('/<int:order_id>/remove_product/<int:product_id>')
class RemoveProduct(Resource):
    def delete(self, order_id, product_id):
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        if product not in order.products:
            return {"message": "Product not in order."}, 404
        order.products.remove(product)
        db.session.commit()
        return {"message": "Product removed from order."}, 204

@ns.route('/user/<int:user_id>')
class OrdersByUser(Resource):
    def get(self, user_id):
        orders = Order.query.filter_by(user_id=user_id).all()
        return orders_schema.dump(orders)

@ns.route('/<int:order_id>/products')
class ProductsByOrder(Resource):
    def get(self, order_id):
        order = Order.query.get_or_404(order_id)
        return OrderSchema().dump(order)['products']
