from db import db
from sqlalchemy import func, and_
import datetime

class ExcessModel(db.Model):
    __tablename__ = 'excessItems'
    id = db.Column(db.Integer, primary_key=True)
    itemID = db.Column(db.Integer, db.ForeignKey('itemsTable.id'))
    item = db.relationship('ItemModel', back_populates="excessItems")
    quantity = db.Column(db.Integer)

    def __init__(self, itemID, quantity, price):
        self.itemID = itemID
        self.quantity = quantity
    
    def json(self):
        return {
            'id' : self.id,
            'itemID' : self.itemID,
            'quantity' : self.quantity
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_item(cls, _itemID):
        return cls.query.filter_by(itemID=_itemID).first()
    
    @classmethod
    def clear(cls):
        cls.query.delete()
        db.session.commit()
        return None
    
    @classmethod
    def clear_by_item(cls, _itemID):
        cls.query.filter(itemID=_itemID).delete()
        db.session.commit()
        return None

class ItemModel(db.Model):
    __tablename__ = 'itemsTable'
    itemTags = db.relationship("ItemTagModel", back_populates="item", cascade="all, delete", passive_deletes=True)
    deliveries = db.relationship('DeliveryModel', back_populates="item")
    recommendations = db.relationship('RecommendationModel', back_populates="item")
    excessItems = db.relationship('ExcessModel', back_populates="item")

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates="items")
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel', back_populates="items")
    imageLink1 = db.Column(db.String(200))
    imageLink2 = db.Column(db.String(200))
    imageLink3 = db.Column(db.String(200))
    imageLink4 = db.Column(db.String(200))
    imageLink5 = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    description = db.Column(db.String(400))
    expiryDate = db.Column(db.Date)
    dateReceived = db.Column(db.Date)
    deleted = db.Column(db.Boolean)

    def __init__(self, userID, categoryTypeID, quantity, description, expiryDate=None,
    dateReceived=datetime.datetime.now(),
    imageLink1=None, imageLink2=None, imageLink3=None, imageLink4=None, imageLink5=None):
        self.userID = userID
        self.categoryTypeID = categoryTypeID
        self.imageLink1 = imageLink1
        self.imageLink2 = imageLink2
        self.imageLink3 = imageLink3
        self.imageLink4 = imageLink4
        self.imageLink5 = imageLink5
        self.quantity = quantity
        self.description = description
        self.expiryDate = expiryDate
        self.dateReceived = dateReceived
    
    def json(self):
        return {
            'id' : self.id,
            'userID' : self.userID,
            'categoryTypeID' : self.categoryTypeID,
            'imageLink1' : self.imageLink1,
            'imageLink2' : self.imageLink2,
            'imageLink3' : self.imageLink3,
            'imageLink4' : self.imageLink4,
            'imageLink5' : self.imageLink5,
            'quantity' : self.quantity,
            'description' : self.description,
            'expiryDate' : self.expiryDate.isoformat() if self.expiryDate else None,
            'dateReceived' : self.dateReceived.isoformat()
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def update_quantity(self, newQuantity):
        self.quantity = newQuantity
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_category_type(cls, categoryTypeID):
        return cls.query.filter_by(categoryTypeID=categoryTypeID).all()
    
    @classmethod
    def find_by_category_type_and_user(cls, categoryTypeID, userID):
        return cls.filter(and_(cls.categoryTypeID==categoryTypeID, cls.userID==userID)).first()
    
    @classmethod
    def get_user_items(cls, userID):
        return cls.query.filter_by(userID=userID).all()

    @classmethod
    def get_available_items_by_category_type(cls, categoryTypeID):
        return cls.query.filter(and_(cls.userID==userID, cls.quantity > 0)).all()
    
    @classmethod
    def get_category_type_items_quantity(cls, categoryTypeID):
        return db.session.query(func.sum(cls.quantity).label("summ")).filter_by(categoryTypeID=categoryTypeID).first().summ


class ItemTagModel(db.Model):
    __tablename__ = "itemTagsTable"
    itemID = db.Column(db.Integer, db.ForeignKey('itemsTable.id', ondelete="CASCADE"), primary_key=True)
    tagID = db.Column(db.Integer, db.ForeignKey('tagsTable.id', ondelete="CASCADE"), primary_key=True)
    tag = db.relationship("TagModel", back_populates="itemTags")
    item = db.relationship("ItemModel", back_populates="itemTags")


    def __init__(self, itemID, tagID):
        self.itemID = itemID
        self.tagID = tagID
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def find_by_itemID(self, itemID):
        return cls.query.filter_by(itemID=itemID).all()

class TagModel(db.Model):
    __tablename__ = "tagsTable"
    itemTags = db.relationship("ItemTagModel", back_populates="tag")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name
    
    def json(self):
        return {
            'id' : self.id,
            'name' : self.name
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    