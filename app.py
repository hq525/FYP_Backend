from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from models.user import UserModel
from resources.user import UserRegister, User, UserLogin, TokenRefresh, PinLogin, EditUser#, UserLogout
from resources.availability import NewAvailability, Availability, GetDates, UserAvailability
from resources.category import Category, CategoryType, GetCategoryType, GetCategory, GetCategoryInformation
from resources.tag import Tag
from resources.item import Item, UserItem, Excess
from resources.request import Request, RequestInformation, UserRequest, Unmet
from resources.delivery import MapInformation, Delivery, DeliveryDetails, DeliveryItem, DeliveryRequest
from resources.rating import Rating
import random
from datetime import datetime, timedelta
from flask_cors import CORS

from db import db

app = Flask(__name__)
CORS(app)
app.config.from_object("config.Config")
api = Api(app)
mail = Mail(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

# @jwt.user_claims_loader
# def add_claims_to_jwt(identity):  
#     if identity == 1:   
#         return {'is_admin': True}
#     return {'is_admin': False}

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
# @jwt.token_in_blacklist_loader
# def check_if_token_in_blacklist(decrypted_token):
#     return decrypted_token['jti'] in BLACKLIST  # Here we blacklist particular JWTs that have been created in the past.

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):  
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401

class ForgetPassword(Resource):
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('email',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
        data = _parser.parse_args()
        user = UserModel.find_by_email(data['email'])
        if not user:
            return {'message': 'User Not Found'}, 404
        pin = ""
        for i in range(4):
            pin += str(random.randrange(9))
        user.pin = pin
        user.pinExpiry = datetime.now() + timedelta(hours=2)
        user.save_to_db()
        msg = Message('Forget Password', sender = 'fypapp2021@gmail.com', recipients = [data['email']])
        msg.body = 'Pin: {p}'.format(p=pin)
        mail.send(msg)
        return {"message": "Email sent"}, 200

api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(ForgetPassword, '/forget/password')
api.add_resource(PinLogin, '/pin/login')
# api.add_resource(UserLogout, '/logout')
api.add_resource(EditUser, '/edit/user')

# User Availability
api.add_resource(NewAvailability, '/availability/new')
api.add_resource(Availability, '/availability')
api.add_resource(UserAvailability, '/availability/user')
api.add_resource(GetDates, '/availability/get')

# Tags
api.add_resource(Tag, '/tag')

# Categories
api.add_resource(GetCategory, '/category/get')
api.add_resource(Category, '/category')
api.add_resource(GetCategoryType, '/category/type/<string:categoryID>')
api.add_resource(CategoryType, '/category/type')
api.add_resource(GetCategoryInformation, '/category/information')

# Items
api.add_resource(Item, '/item')
api.add_resource(UserItem, '/item/<string:userID>')
api.add_resource(Excess, '/excess')

# Requests
api.add_resource(Request, '/request')
api.add_resource(UserRequest, '/request/<string:userID>')
api.add_resource(RequestInformation, '/request/information/<string:requestID>')
api.add_resource(Unmet, '/unmet')

# Map Information
api.add_resource(MapInformation, '/map/information')
api.add_resource(Delivery, '/delivery')
api.add_resource(DeliveryItem, '/delivery/item')
api.add_resource(DeliveryRequest, '/delivery/request')
api.add_resource(DeliveryDetails, '/delivery/<string:deliveryID>')

# Rating
api.add_resource(Rating, '/rating')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)