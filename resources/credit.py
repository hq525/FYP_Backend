from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.credit import CreditModel
from models.user import UserModel

class Credit(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if not user:
            return {'message': 'User Not Found'}, 404
        credit = CreditModel.find_by_user_id(userID)
        if not credit:
            return {'message' : 'Credits not found'}, 404
        return {'credit' : credit.json()}, 200
        

    @jwt_required
    def put(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('userID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('creditsToAdd',type=int,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        user = UserModel.find_by_id(data['userID'])
        if not user:
            return {'message' : 'User not found'}, 404
        credit = CreditModel.find_by_user_id(data['userID'])
        if not credit:
            return {'message' : 'Credits not found'}, 404
        credit.credits = credit.credits + int(data['creditsToAdd'])
        credit.save_to_db()
        return {'message' : 'User credits successfully updated'}, 200