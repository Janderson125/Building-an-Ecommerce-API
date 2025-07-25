from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import Product
from schemas import ProductSchema

ns = Namespace('products', description='Product related operations')

product_model = ns.model('Product', {
    'product_name': fields.String(required=True),
    'price': fields.Float(required=True),
})

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@ns.route('/')
class ProductList(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)
    
    @ns.expect(product_model)
    def post(self):
        data = request.json
        product = Product(
            product_name=data['product_name'],
            price=data['price']
        )
        db.session.add(product)
        db.session.commit()
        return product_schema.dump(product), 201

@ns.route('/<int:id>')
class ProductDetail(Resource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product_schema.dump(product)
    
    @ns.expect(product_model)
    def put(self, id):
        product = Product.query.get_or_404(id)
        data = request.json
        product.product_name = data.get('product_name', product.product_name)
        product.price = data.get('price', product.price)
        db.session.commit()
        return product_schema.dump(product)
    
    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted"}, 204
