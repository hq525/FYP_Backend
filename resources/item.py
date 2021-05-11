from flask_restful import Resource, reqparse
from datetime import datetime
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.item import ItemModel, ItemTagModel, TagModel, ExcessModel
from models.credit import CreditModel
from models.category import CategoryTypeModel
import math

class Excess(Resource):
    @jwt_required
    def get(self):
        excess = ExcessModel.find_all()
        items = []
        for i in excess:
            categoryType = i.item.categoryType
            items.append({
                'id' : item.id,
                'itemID' : item.itemID,
                'quantity' : item.quantity,
                'name' : categoryType.name,
                'price' : categoryType.price
            })
        return {"items" : items}, 200

    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('itemID',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        excess = ExcessModel.find_by_item(data['itemID'])
        items = []
        for i in excess:
            categoryType = i.item.categoryType
            items.append({
                'id' : item.id,
                'itemID' : item.itemID,
                'quantity' : item.quantity,
                'name' : categoryType.name,
                'price' : categoryType.price
            })
        return {"items" : items}, 200

class UserItem(Resource):
    @jwt_required
    def get(self, userID):
        items = ItemModel.get_user_items(userID)
        return {"items" : [item.json() for item in items]}, 200

class Item(Resource):
    @jwt_required
    def get(self):
        userID = get_jwt_identity()
        items = ItemModel.get_user_items(userID)
        return {"items" : [item.json() for item in items if not item.deleted]}, 200

    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('categoryTypeID',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('imageLink1',type=str,required=False)
        _parser.add_argument('imageLink2',type=str,required=False)
        _parser.add_argument('imageLink3',type=str,required=False)
        _parser.add_argument('imageLink4',type=str,required=False)
        _parser.add_argument('imageLink5',type=str,required=False)
        _parser.add_argument('quantity',type=int,required=True,help="This field cannot be blank.")
        _parser.add_argument('description',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('expiryDate',type=str,required=False)
        _parser.add_argument('tags',type=list,required=True,location='json')
        userID = get_jwt_identity()
        data = _parser.parse_args()
        expiryDate = datetime.strptime(data['expiryDate'], '%Y-%m-%dT%H:%M:%S.%fZ') if data['expiryDate'] else None
        quantityLeft = ItemModel.get_category_type_items_quantity(data['categoryTypeID'])
        if quantityLeft == None:
            quantityLeft = 0
        categoryType = CategoryTypeModel.find_by_id(data['categoryTypeID'])
        credits = calculateDonationCredits(quantityLeft,categoryType.price,data['quantity'])
        credit = CreditModel.find_by_user_id(userID)
        credit.credits += credits
        credit.save_to_db()
        # See if user has already donated an item for that categoryTypeID
        item = ItemModel(userID=userID,categoryTypeID=data['categoryTypeID'],imageLink1=data['imageLink1'],
        imageLink2=data['imageLink2'],imageLink3=data['imageLink3'],imageLink4=data['imageLink4'],
        imageLink5=data['imageLink5'],quantity=data['quantity'],description=data['description'],
        expiryDate=expiryDate)
        item.save_to_db()
        for name in data['tags']:
            tag = TagModel.find_by_name(name)
            if not tag:
                tag = TagModel(name=name)
                tag.save_to_db()
            itemTag = ItemTagModel(itemID=item.id,tagID=tag.id)
            itemTag.save_to_db()
        return {"message": "Item saved successfully"}, 201
    
    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        item = ItemModel.find_by_id(data["id"])
        for itemTag in item.itemTags:
            itemTag.delete_from_db()
        if len(item.deliveries) == 0:
            item.delete_from_db()
        else:
            allUndelivered = True
            for delivery in item.deliveries:
                if delivery.delivered == True:
                    allUndelivered = False
                    break
            if allUndelivered == True:
                for delivery in item.deliveries:
                    request = delivery.request
                    request.update_quantity(request.quantity + delivery.quantity)
                    delivery.delete_from_db()
                item.delete_from_db()
            else:
                for delivery in item.deliveries:
                    if not delivery.delivered:
                        request = delivery.request
                        request.update_quantity(request.quantity + delivery.quantity)
                        delivery.delete_from_db()
                item.deleted = True
                item.save_to_db()
        return {"message": "Item deleted"}, 200

def calculateDonationCredits(quantityLeft, price, quantity):
    credits = price*quantity
    credits *= math.exp(-1 * quantityLeft)
    return credits