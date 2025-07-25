from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import Product
from schemas import ProductSchema

ns = Namespace('products', description='Product related operations')

product_model = ns.model('Product', {
    'product_name': fields.String(required=True, description='Name of the product'),
    'price': fields.Float(required=True, description='Price of the product'),
})

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@ns.route('/')
class ProductList(Resource):
    @ns.marshal_list_with(product_model)
    def get(self):
        """List all products"""
        products = Product.query.all()
        return products_schema.dump(products)

    @ns.expect(product_model, validate=True)
    @ns.marshal_with(product_model, code=201)
    def post(self):
        """Create a new product"""
        data = request.json
        product = Product(
            product_name=data['product_name'],
            price=data['price']
        )
        db.session.add(product)
        db.session.commit()
        return product_schema.dump(product), 201

@ns.route('/<int:id>')
@ns.param('id', 'The product identifier')
@ns.response(404, 'Product not found')
class ProductDetail(Resource):
    @ns.marshal_with(product_model)
    def get(self, id):
        """Get product by ID"""
        product = Product.query.get_or_404(id)
        return product_schema.dump(product)

    @ns.expect(product_model, validate=True)
    @ns.marshal_with(product_model)
    def put(self, id):
        """Update product details"""
        product = Product.query.get_or_404(id)
        data = request.json
        product.product_name = data.get('product_name', product.product_name)
        product.price = data.get('price', product.price)
        db.session.commit()
        return product_schema.dump(product)

    @ns.response(204, 'Product deleted')
    def delete(self, id):
        """Delete a product"""
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return '', 204
