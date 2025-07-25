from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import User
from schemas import UserSchema

ns = Namespace('users', description='User related operations')

user_model = ns.model('User', {
    'name': fields.String(required=True),
    'address': fields.String,
    'email': fields.String(required=True),
})

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@ns.route('/')
class UserList(Resource):
    def get(self):
        users = User.query.all()
        return users_schema.dump(users)
    
    @ns.expect(user_model)
    def post(self):
        data = request.json
        user = User(
            name=data['name'],
            address=data.get('address'),
            email=data['email']
        )
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201

@ns.route('/<int:id>')
class UserDetail(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return user_schema.dump(user)
    
    @ns.expect(user_model)
    def put(self, id):
        user = User.query.get_or_404(id)
        data = request.json
        user.name = data.get('name', user.name)
        user.address = data.get('address', user.address)
        user.email = data.get('email', user.email)
        db.session.commit()
        return user_schema.dump(user)
    
    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 204
