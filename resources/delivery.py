from flask_restful import Resource, reqparse, inputs
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from models.delivery import DeliveryModel
from models.user import UserAvailabilityModel, UserModel
from models.request import RequestModel
from models.item import ItemModel
from models.credit import CreditModel
from datetime import datetime
from random import randint
import math

class MapInformation(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('startDateTime')
        _parser.add_argument('endDateTime')
        data = _parser.parse_args()
        startDateTime = datetime.strptime(data['startDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        endDateTime = datetime.strptime(data['endDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        availabilities = UserAvailabilityModel.find_all_in_range(startDateTime, endDateTime)
        users = {}
        for availability in availabilities:
            if availability.userID not in users:
                user = UserModel.find_by_id(availability.userID)
                users[availability.userID] = {'user': user.json(), 'availabilities': [{'id': availability.id, 'startDateTime': availability.startDateTime.isoformat(), 'endDateTime': availability.endDateTime.isoformat()}]}
            else:
                users[availability.userID]['availabilities'].append({'id': availability.id, 'startDateTime': availability.startDateTime.isoformat(), 'endDateTime': availability.endDateTime.isoformat()})
        return {'users' : users}, 200

class DeliveryRequest(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if not user:
            return {'message' : 'User not found'}, 404
        deliveries = []
        for request in user.requests:
            for delivery in request.deliveries:
                donor = delivery.item.user
                deliverer = delivery.deliverer
                rating = delivery.rating
                deliveries.append({
                    'id' : delivery.id,
                    'donorFirstName' : donor.firstName,
                    'donorLastName' : donor.lastName,
                    'delivererFirstName' : deliverer.firstName,
                    'delivererLastName' : deliverer.lastName,
                    'delivererID' : deliverer.id,
                    'deliveryDateTime' : delivery.deliveryDateTime.isoformat(),
                    'itemName' : delivery.itemName,
                    'quantity' : delivery.quantity,
                    'donorAccepted' : delivery.donorAccepted,
                    'delivererAccepted' : delivery.delivererAccepted,
                    'beneficiaryAccepted' : delivery.beneficiaryAccepted,
                    'delivered' : delivery.delivered,
                    'confirmationCode' : delivery.confirmationCode,
                    'ratingGiven' : True if rating else False
                })
        return {'deliveries' : deliveries}, 200

class DeliveryItem(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        user = UserModel.find_by_id(userID)
        if not user:
            return {'message' : 'User not found'}, 404
        deliveries = []
        for item in user.items:
            for delivery in item.deliveries:
                beneficiary = delivery.request.user
                deliveries.append({
                    'id' : delivery.id,
                    'beneficiaryFirstName' : beneficiary.firstName,
                    'beneficiaryLastName' : beneficiary.lastName,
                    'collectionDateTime' : delivery.collectionDateTime.isoformat(),
                    'itemName' : delivery.itemName,
                    'quantity' : delivery.quantity,
                    'donorAccepted' : delivery.donorAccepted,
                    'delivererAccepted' : delivery.delivererAccepted,
                    'beneficiaryAccepted' : delivery.beneficiaryAccepted,
                    'delivered' : delivery.delivered
                })
        return {'deliveries' : deliveries}, 200
        

class DeliveryDetails(Resource):
    @jwt_required
    def get(self, deliveryID):
        delivery = DeliveryModel.find_by_id(deliveryID)
        if not delivery:
            return {'message' : 'Delivery not found'}, 404
        donor = delivery.item.user
        beneficiary = delivery.request.user
        return {
            'delivery' : {
                'id' : delivery.id,
                'donorFirstName' : donor.firstName,
                'donorLastName' : donor.lastName,
                'donorLat' : str(donor.lat),
                'donorLng' : str(donor.lng),
                'beneficiaryFirstName' : beneficiary.firstName,
                'beneficiaryLastName' : beneficiary.lastName,
                'beneficiaryLat' : str(beneficiary.lat),
                'beneficiaryLng' : str(beneficiary.lng),
                'collectionDateTime' : delivery.collectionDateTime.isoformat(),
                'deliveryDateTime' : delivery.deliveryDateTime.isoformat(),
                'itemName' : delivery.itemName,
                'quantity' : delivery.quantity,
                'comments' : delivery.request.comments,
                'donorAccepted' : delivery.donorAccepted,
                'delivererAccepted' : delivery.delivererAccepted,
                'beneficiaryAccepted' : delivery.beneficiaryAccepted,
                'delivered' : delivery.delivered
            }
        }, 200
    
    @jwt_required
    def post(self,deliveryID):
        delivery = DeliveryModel.find_by_id(deliveryID)
        if not delivery:
            return {'message' : 'Delivery not found'}, 404
        _parser = reqparse.RequestParser()
        _parser.add_argument('confirmationCode',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        if data['confirmationCode'] != delivery.confirmationCode:
            return {'message' : 'Incorrect confirmation code'}, 400
        delivery.setDelivered()
        credits = calculateDeliveryCredits(delivery.deliveryDateTime, datetime.now())
        credit = CreditModel.find_by_user_id(delivery.delivererID)
        credit.credits = credit.credits + credits
        credit.save_to_db()
        item = delivery.item
        categoryType = item.categoryType
        quantityLeft = ItemModel.get_category_type_items_quantity(item.categoryTypeID)
        creditsToSubstract = calculateCreditsSpentOnDelivery(quantityLeft, float(categoryType.price), delivery.quantity)
        beneficiaryCredit = delivery.request.user.credit[0]
        beneficiaryCredit.credits -= creditsToSubstract
        beneficiaryCredit.save_to_db()
        return {'message' : 'Delivery updated successfully'}, 200

def calculateCreditsSpentOnDelivery(quantityLeft, price, quantity):
    creditsToSubstract = price * quantity
    creditsToSubstract *= math.exp(-1 * quantityLeft)
    return creditsToSubstract

def calculateDeliveryCredits(deliveryDateTime, actualDeliveryDateTime):
    if actualDeliveryDateTime > deliveryDateTime:
        return 0
    else:
        return 50

class Delivery(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        deliveries = DeliveryModel.get_user_deliveries(userID)
        temp = []
        for delivery in deliveries:
            tempDict = {}
            for key, value in delivery.json().items():
                tempDict[key] = value
            tempDict['collectionAddressLine1'] = delivery.item.user.addressLine1
            tempDict['collectionAddressLine2'] = delivery.item.user.addressLine2
            tempDict['collectionAddressPostalCode'] = delivery.item.user.addressPostalCode
            tempDict['deliveryAddressLine1'] = delivery.request.user.addressLine1
            tempDict['deliveryAddressLine2'] = delivery.request.user.addressLine2
            tempDict['deliveryAddressPostalCode'] = delivery.request.user.addressPostalCode
            temp.append(tempDict)
        return {'deliveries' : temp}, 200

    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('requestID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('delivererID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('itemID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('quantity',type=int,required=True,help="This field cannot be blank.")
        _parser.add_argument('collectionDateTime')
        _parser.add_argument('deliveryDateTime')
        _parser.add_argument('dateTime')
        _parser.add_argument('itemName',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        request = RequestModel.find_by_id(data['requestID'])
        if not request:
            return {'message': 'Request Not Found'}, 404
        deliverer = UserModel.find_by_id(data['delivererID'])
        if not deliverer:
            return {'message': 'Deliverer not found'}, 404
        item = ItemModel.find_by_id(data['itemID'])
        if not item:
            return {'message': 'Item not found'}, 404
        if data['quantity'] <= 0:
            return {'message' : 'Invalied quantity selected'}, 400
        if request.quantity <= 0:
            return {'message', 'No more items requested'}, 400
        if data['quantity'] > request.quantity:
            return {'message' : 'Quantity selected is more than requested'}, 400
        if item.quantity <= 0:
            return {'message': 'No more items to be donated'}, 400
        if data['quantity'] > item.quantity:
            return {'message' : 'Quantity selected is more than donated'}, 400
        collectionDateTime = datetime.strptime(data['collectionDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        deliveryDateTime = datetime.strptime(data['deliveryDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        dateTime = datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if (deliveryDateTime <= collectionDateTime):
            return {'message' : 'Delivery time should be later than the collection time'}, 400
        if (collectionDateTime <= dateTime):
            return {'message' : 'Collection time should be later than the current time'}, 400
        if (deliveryDateTime <= dateTime):
            return {'message' : 'Collection time should be later than the current time'}, 400
        confirmationCode = ""
        for i in range(6):
            confirmationCode += str(randint(1,9))
        delivery = DeliveryModel(requestID=data['requestID'],delivererID=data['delivererID'],itemID=data['itemID'],dateTime=dateTime,confirmationCode=confirmationCode,quantity=data['quantity'],collectionDateTime=collectionDateTime,deliveryDateTime=deliveryDateTime, itemName=data['itemName'])
        delivery.save_to_db()
        item.update_quantity(item.quantity - data['quantity'])
        request.update_quantity(request.quantity - data['quantity'])
        return {"message": "Delivery details saved successfully"}, 201
    
    @jwt_required
    def put(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('deliveryID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('donorAccepted', type=inputs.boolean)
        _parser.add_argument('delivererAccepted', type=inputs.boolean)
        _parser.add_argument('beneficiaryAccepted', type=inputs.boolean)
        data = _parser.parse_args()
        delivery = DeliveryModel.find_by_id(data['deliveryID'])
        if not delivery:
            return {'message' : 'Delivery not found'}, 404
        if data['donorAccepted'] == True:
            delivery.setDonorAccepted()
        if data['delivererAccepted'] == True:
            delivery.setDelivererAccepted()
        if data['beneficiaryAccepted'] == True:
            delivery.setBeneficiaryAccepted()
        return {'message' : 'Delivery updated'}, 200            
    
    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('deliveryID',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        delivery = DeliveryModel.find_by_id(data['deliveryID'])
        if not delivery:
            return {'message' : 'Delivery not found'}, 404
        if delivery.delivered == True:
            return {'message' : 'Delivery cannot be removed as item already delivered'}, 404
        item = delivery.item
        if item and not item.deleted:
            item.update_quantity(item.quantity + delivery.quantity)
        request = delivery.request
        request.update_quantity(request.quantity + delivery.quantity)
        delivery.delete_from_db()
        return {"message" : "Delivery deleted successfully"}
        