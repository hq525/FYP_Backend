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
from models.credit import CreditModel
import datetime, http.client, urllib.parse, json
import math

_login_parser = reqparse.RequestParser()
_login_parser.add_argument('email',type=str,required=True,help="This field cannot be blank.")
_login_parser.add_argument('password',type=str,required=True,help="This field cannot be blank.")

_register_parser = reqparse.RequestParser()
_register_parser.add_argument('email',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('password',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('firstName',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('lastName',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('birthday',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('income',type=float,required=True,help="This field cannot be blank.")
_register_parser.add_argument('picture',type=str,required=False)
_register_parser.add_argument('householdType',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('addressLine1',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('addressLine2',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('addressPostalCode',type=str,required=True,help="This field cannot be blank.")
_register_parser.add_argument('householdCount',type=int,required=True,help="This field cannot be blank.")

class UserRegister(Resource):
    def post(self):
        data = _register_parser.parse_args()

        if UserModel.find_by_email(data['email']):
            return {"message": "Email already registered"}, 400
        
        # Determine if address given is valid or not
        conn = http.client.HTTPConnection('api.positionstack.com')
        address = '{}, {}, Singapore {}'.format(data['addressLine1'], data['addressLine2'], data['addressPostalCode'])
        params = urllib.parse.urlencode({
            'access_key': 'bc0e165286c05e84509479ea679117eb',
            'query': address,
            'region': 'Singapore',
            'limit': 1,
            })
        conn.request('GET', '/v1/forward?{}'.format(params))
        res = conn.getresponse()
        returnData = res.read()
        response = json.loads(returnData.decode('utf-8'))
        if len(response['data']) == 0:
            return {"message": "Invalid Address"}, 400
        user = UserModel(lat=response['data'][0]['latitude'], lng=response['data'][0]['longitude'], **data)
        user.save_to_db()
        birthday = datetime.datetime.strptime(data['birthday'], '%Y-%m-%d')
        today = datetime.date.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        credits = calculateSignUpCredits(age, data['income'], data['householdCount'], data['householdType'])
        credit = CreditModel(userID=user.id, credits=credits)
        credit.save_to_db()
        return {"message": "User created successfully."}, 201

householdTypes = {
    'Condominium' : 1000,
    'HDB' : 2000,
    'Terrace House' : 500,
    'Bungalow' : 0,
    'Semi-Detached' : 250
}

def calculateSignUpCredits(age, income, householdCount, householdType):
    credits = age * 100
    credits += math.exp(income/1000/householdCount)
    credits += householdTypes[householdType]
    return credits

class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @classmethod
    @jwt_required
    def get(cls):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if not user:
            return {'message': 'User Not Found'}, 404
        return {'user': user.json()}, 200


class UserLogin(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if user:
            access_token = create_access_token(identity=user.id, fresh=True) 
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {"message": "Invalid Credentials!"}, 401
    
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
        _parser.add_argument('email',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('pin',type=str,required=True,help="This field cannot be blank.")
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

class EditUser(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('email',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('firstName',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('lastName',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('birthday',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('income',type=float,required=True,help="This field cannot be blank.")
        _parser.add_argument('picture',type=str,required=False)
        _parser.add_argument('householdType',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('addressLine1',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('addressLine2',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('addressPostalCode',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        # Determine if address given is valid or not
        conn = http.client.HTTPConnection('api.positionstack.com')
        address = '{}, {}, Singapore {}'.format(data['addressLine1'], data['addressLine2'], data['addressPostalCode'])
        params = urllib.parse.urlencode({
            'access_key': 'bc0e165286c05e84509479ea679117eb',
            'query': address,
            'region': 'Singapore',
            'limit': 1,
            })
        conn.request('GET', '/v1/forward?{}'.format(params))
        res = conn.getresponse()
        returnData = res.read()
        response = json.loads(returnData.decode('utf-8'))
        if len(response['data']) == 0:
            return {"message": "Invalid Address"}, 400
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        user.email = data['email']
        user.lat = response['data'][0]['latitude']
        user.lng = response['data'][0]['longitude']
        user.firstName = data['firstName']
        user.lastName = data['lastName']
        user.birthday = data['birthday']
        user.income = data['income']
        if data['picture']:
            user.picture = data['picture']
        user.householdType = data['householdType']
        user.addressLine1 = data['addressLine1']
        user.addressLine2 = data['addressLine2']
        user.addressPostalCode = data['addressPostalCode']
        user.save_to_db()
        return {"message": "Profile updated"}, 200
    
    @jwt_required
    def put(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('oldPassword',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('newPassword',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if user and safe_str_cmp(user.password, data['oldPassword']):
            user.password = data['newPassword']
            user.save_to_db()
            return {'message': 'Password Updated'}, 200

        return {"message": "Invalid Credentials!"}, 401