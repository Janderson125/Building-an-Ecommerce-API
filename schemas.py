from app import ma
from models import User, Product, Order

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_relationships = True
        load_instance = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True  # Important to expose user_id
        include_relationships = True
        load_instance = True
    
    products = ma.Nested(ProductSchema, many=True)
    user = ma.Nested(UserSchema)
