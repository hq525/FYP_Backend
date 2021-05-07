from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from models.rating import RatingModel
from models.user import UserModel
from models.delivery import DeliveryModel
from models.credit import CreditModel
from datetime import datetime

class Rating(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if not user:
            return {'message' : 'User not found'}, 404
        ratings = RatingModel.get_ratee_ratings(userID)
        temp = []
        for rating in ratings:
            rater = rating.rater
            temp.append({
                'raterFirstName' : rater.firstName,
                'raterLastName' : rater.lastName,
                'id' : rating.id,
                'rating' : rating.rating,
                'date' : rating.date.isoformat(),
                'feedback' : rating.feedback
            })
        return {
            'firstName' : user.firstName,
            'lastName' : user.lastName,
            'totalRating' : user.totalRating,
            'noOfRatings' : user.noOfRatings,
            'ratings' : temp
        }

    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('raterID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('rateeID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('deliveryID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('rating',type=int,required=True,help="This field cannot be blank.")
        _parser.add_argument('feedback',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('date')
        data = _parser.parse_args()
        d = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        delivery = DeliveryModel.find_by_id(data['deliveryID'])
        if not delivery:
            return {'message' : 'Delivery not found'}, 404
        if not delivery.delivered:
            return {'message' : 'Delivery needs to be confirmed by deliverer first'}, 400
        rating = RatingModel.find_by_delivery_id(data['deliveryID'])
        if rating:
            return {'message' : 'Delivery already rated'}, 400
        ratee = UserModel.find_by_id(data['rateeID'])
        if not ratee:
            return {'message' : 'Ratee not found'}
        rating = RatingModel(raterID=data['raterID'], rateeID=data['rateeID'], deliveryID=data['deliveryID'],rating=data['rating'],feedback=data['feedback'], date=d)
        rating.save_to_db()
        if not ratee.noOfRatings:
            ratee.totalRating = data['rating']
            ratee.noOfRatings = 1
        else:
            ratee.totalRating = ratee.totalRating + data['rating']
            ratee.noOfRatings = ratee.noOfRatings + 1
        ratee.save_to_db()
        credits = calculateFeedbackCredits(data['rating'])
        credit = CreditModel.find_by_user_id(data['rateeID'])
        credit.credits = credit.credits + credits
        credit.save_to_db()
        return {"message" : "Rating saved successfully"}, 200

def calculateFeedbackCredits(rating):
    if rating == 5:
        return 50
    elif rating == 4:
        return 40
    elif rating == 3:
        return 30
    elif rating == 2:
        return 20
    elif rating == 1:
        return 10
    else:
        return 0