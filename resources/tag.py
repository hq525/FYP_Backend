from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.item import TagModel

class Tag(Resource):
    @jwt_required
    def get(self):
        tags = TagModel.get_all()
        return {"tags" : [tag.json() for tag in tags]}, 200

    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('name',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        tag = TagModel.find_by_name(data['name'])
        if tag:
            return {"message": "Tag with name already exists"}, 400
        
        tag = TagModel(name=data["name"])
        tag.save_to_db()

        return {"message" : "Tag created successfully", "tag" : tag.json()}, 201
    
    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id',type=str,required=True,help="This field cannot be blank.")
        data = _parser.parse_args()
        tag = TagModel.find_by_id(data['id'])
        if not tag:
            return {"message": "Tag with name does not exist"}, 400
        for itemTag in tag.itemTag:
            itemTag.delete_from_db()
        tag.delete_from_db()
        return {"message": "Tag deleted successfully"}, 200