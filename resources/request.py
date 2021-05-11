from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.request import RequestModel, UnmetModel
from models.queue import QueueItemModel
from datetime import datetime

class RequestInformation(Resource):
    @jwt_required
    def get(cls, requestID: str):
        request = RequestModel.find_by_id(requestID)
        if not request:
            return {'message': 'Request Not Found'}, 404
        return {'request' : request.json()}, 200

class UserRequest(Resource):
    @jwt_required
    def get(cls, userID):
        requests = RequestModel.get_all_user_requests(userID)
        return {'requests' : [request.json() for request in requests]}, 200

class Unmet(Resource):
    @jwt_required
    def get(cls):
        unmetRequests = UnmetModel.find_all()
        requests = []
        for r in unmetRequests:
            request = r.request
            categoryType = request.categoryType
            category = categoryType.category
            requests.append({
                "dateRequested" : request.dateRequested,
                "category" : category.name,
                "categoryType" : categoryType.name,
                "quantity" : r.quantity,
                "comments" : request.comments,
                "id" : r.id
            })
        return {"requests" : requests}, 200

class Request(Resource):
    @jwt_required
    def post(cls):
        _parser = reqparse.RequestParser()
        _parser.add_argument('categoryTypeID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('quantity',type=int,required=True,help="This field cannot be blank.")
        _parser.add_argument('comments',type=str,required=False)
        userID = get_jwt_identity()
        data = _parser.parse_args()
        request = RequestModel(userID=userID,categoryTypeID=data['categoryTypeID'],quantity=data['quantity'],comments=data['comments'])
        request.save_to_db()
        #Add request to queue
        queueItem = QueueItemModel(userID=userID, categoryTypeID=data['categoryTypeID'], requestID=request.id)
        queueItem.save_to_db()
        return {"message": "Request created successfully"}, 201
    
    @jwt_required
    def get(cls):
        userID = get_jwt_identity()
        requests = RequestModel.get_all_user_requests(userID)
        return {'requests' : [request.json() for request in requests if request.quantity > 0]}, 200
    
    @jwt_required
    def delete(cls):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        userID = get_jwt_identity()
        request = RequestModel.find_by_id(data['id'])
        if not request:
            return {'message': 'Request Not Found'}, 404
        if request.userID != userID:
            return {'message' : 'Invalid User'}, 400
        if (len(request.deliveries) > 0):
            return {'message' : 'This request has deliveries associated with it and hence, cannot be deleted'}, 400
        request.delete_from_db()
        return {'message': 'Request deleted.'}, 200
        