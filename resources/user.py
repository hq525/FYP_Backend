from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_mail import Mail, Message
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.user import UserModel
import datetime

_login_parser = reqparse.RequestParser()
_login_parser.add_argument('email',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_login_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

_register_parser = reqparse.RequestParser()
_register_parser.add_argument('email',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('firstName',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('lastName',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('birthday',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('income',
                          type=float,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('picture',
                          type=str,
                          required=False
                          )
_register_parser.add_argument('householdType',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('addressBlockHouseNo',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('addressStreetName',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('addressLevel',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('addressUnitNo',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_register_parser.add_argument('addressBuildingName',
                          type=str,
                          required=False
                          )
_register_parser.add_argument('addressPostalCode',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

class UserRegister(Resource):
    def post(self):
        data = _register_parser.parse_args()

        if UserModel.find_by_email(data['email']):
            return {"message": "Email already registered"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @classmethod
    @jwt_required
    def get(cls, email: str):
        user = UserModel.find_by_email(email)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @classmethod
    @jwt_required
    def delete(cls, email: str):
        user = UserModel.find_by_email(email)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    def post(self):
        data = _login_parser.parse_args()

        user = UserModel.find_by_email(data['email'])

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, data['password']):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True) 
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401

class PinLogin(Resource):
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('email',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
        _parser.add_argument('pin',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
        data = _parser.parse_args()
        user = UserModel.find_by_email(data['email'])
        if not user:
            return {'message': 'User Not Found'}, 404
        if user.pinExpiry < datetime.datetime.now():
            return {'message': 'Pin expired'}, 400
        if data["pin"] != user.pin:
            return {'message': 'Incorrect pin'}, 400
        access_token = create_access_token(identity=user.id, fresh=True) 
        refresh_token = create_refresh_token(user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200
        

# class UserLogout(Resource):
#     @jwt_required
#     def post(self):
#         jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a JWT.
#         BLACKLIST.add(jti)
#         return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.
        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200


        