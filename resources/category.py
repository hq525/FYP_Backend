from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.category import CategoryModel, CategoryTypeModel

class Category(Resource):
    @jwt_required
    def get(self):
        categories = CategoryModel.get_all()
        return { "categories" : [category.json() for category in categories] }, 200

    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('name',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('urgency',type=int,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        category = CategoryModel.find_by_name(data['name'])
        if category:
            return {"message": "Category with name already exists"}, 400
        
        category = CategoryModel(name=data['name'],urgency=data['urgency'])
        category.save_to_db()

        return {"message" : "Category created successfully", "category" : category.json()}, 201

    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        category = CategoryModel.find_by_id(data["id"])
        if len(category.categoryTypes) > 0:
            return {"message" : "Category cannot be deleted as there are category types associated with it"}
        if category:
            category.delete_from_db()
        return {"message": "Category successfully deleted"}, 200

class GetCategory(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        category = CategoryModel.find_by_id(data["id"])
        if not category:
            return {"message": "Category not found"}, 400
        else:
            return {"category" : category.json()}, 200


class GetCategoryType(Resource):
    @jwt_required
    def get(self, categoryID):
        category = CategoryModel.find_by_id(categoryID)
        if not category:
            return {"message" : "Category not found"}, 400
        categoryTypes = CategoryTypeModel.find_by_categoryID(categoryID)
        return { "categoryTypes" : [categoryType.json() for categoryType in categoryTypes]}, 200

class CategoryType(Resource): 
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('categoryID',type=int,required=True,help="This field cannot be blank.")
        _parser.add_argument('name',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('price',type=float,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        category = CategoryModel.find_by_id(data['categoryID'])
        if not category:
            return {"message" : "Category not found"}, 400
        categoryType = CategoryTypeModel.find_by_categoryID_name(categoryID=data['categoryID'],name=data['name'])
        if categoryType:
            return {"message" : "Category type with specified category and name already exists"}, 200
        categoryType = CategoryTypeModel(name=data['name'],categoryID=data['categoryID'],price=float(data['price']))
        categoryType.save_to_db()
        return {"message" : "Category type saved", "categoryType" : categoryType.json()}, 200
    
    @jwt_required
    def put(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        _parser.add_argument('name',type=str)
        _parser.add_argument('price',type=float)
        data = _parser.parse_args()
        categoryType = CategoryTypeModel.find_by_name(data['name'])
        if categoryType:
            return {"message" : "Category type with name provided already exists"}, 400
        categoryType = CategoryTypeModel.find_by_id(data['id'])
        if not categoryType:
            return {"message" : "Category type not found"}, 404
        if data['name']:
            categoryType.name = data['name']
        if data['price']:
            categoryType.price = data['price']
        categoryType.save_to_db()
        return {"message" : "Category type successfully updated"}, 200

    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        categoryType = CategoryTypeModel.find_by_id(data["id"])
        if len(categoryType.items) > 0:
            return {"message" : "Category type cannot be deleted as there are items associated with it"}, 400
        if len(categoryType.requests) > 0:
            return {"message" : "Category type cannot be deleted as there are requests associated with it"}, 400
        if categoryType:
            categoryType.delete_from_db()
        return {"message" : "Category type deleted"}, 200

class GetCategoryInformation(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('categoryTypeIDs',type=list,required=True,location='json',help="This field cannot be blank.")
        data = _parser.parse_args()
        information = {}
        for id in data['categoryTypeIDs']:
            categoryType = CategoryTypeModel.find_by_id(id)
            if not categoryType:
                return {"message" : "Invalid Category Type ID"}, 400
            category = CategoryModel.find_by_id(categoryType.categoryID)
            if not category:
                return {"message" : "Cannot find category for" + str(id)}, 400
            information[id] = {"categoryType" : categoryType.name, "category" : category.name, "urgency" : category.urgency}
        return { "information" : information }, 200