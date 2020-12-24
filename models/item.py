from db import db
import datetime

class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel')
    imageLink1 = db.Column(db.String(200))
    imageLink2 = db.Column(db.String(200))
    imageLink3 = db.Column(db.String(200))
    imageLink4 = db.Column(db.String(200))
    imageLink5 = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    description = db.Column(db.String(400))
    expiryDate = db.Column(db.Date)
    dateReceived = db.Column(db.Date)

    def __init__(self, userID, categoryTypeID, quantity, description, description, expiryDate,
    dateReceived=datetime.datetime.now().date(),
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
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_category_type(cls, categoryTypeID):
        return cls.query.filter_by(categoryTypeID=categoryTypeID).all()

class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    
class ItemTagModel(db.Model):
    itemID = db.Column(db.Integer, primary_key=True, db.ForeignKey('items.id'))
    tagID = db.Column(db.Integer, primary_key=True, db.ForeignKey('tags.id'))

    def __init__(self, itemID, tagID):
        self.itemID = itemID
        self.tagID = tagID
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()