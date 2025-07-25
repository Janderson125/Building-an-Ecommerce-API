from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from models import User
from schemas import UserSchema

ns = Namespace('users', description='User related operations')

user_model = ns.model('User', {
    'name': fields.String(required=True, description='User full name'),
    'address': fields.String(description='User address'),
    'email': fields.String(required=True, description='User email address'),
})

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@ns.route('/')
class UserList(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        users = User.query.all()
        return users_schema.dump(users)

    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
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
@ns.param('id', 'The user identifier')
@ns.response(404, 'User not found')
class UserDetail(Resource):
    @ns.marshal_with(user_model)
    def get(self, id):
        """Get user by ID"""
        user = User.query.get_or_404(id)
        return user_schema.dump(user)

    @ns.expect(user_model, validate=True)
    @ns.marshal_with(user_model)
    def put(self, id):
        """Update user details"""
        user = User.query.get_or_404(id)
        data = request.json
        user.name = data.get('name', user.name)
        user.address = data.get('address', user.address)
        user.email = data.get('email', user.email)
        db.session.commit()
        return user_schema.dump(user)

    @ns.response(204, 'User deleted')
    def delete(self, id):
        """Delete user"""
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
