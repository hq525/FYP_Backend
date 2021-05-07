from db import db
from sqlalchemy import and_

class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    urgency = db.Column(db.Integer)
    categoryTypes = db.relationship("CategoryTypeModel", back_populates="category")

    def __init__(self, name, urgency):
        self.name = name
        self.urgency = urgency
    
    def json(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'urgency' : self.urgency
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

class CategoryTypeModel(db.Model):
    __tablename__ = 'categoryTypes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    categoryID = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('CategoryModel', back_populates="categoryTypes")
    price = db.Column(db.Float)

    items = db.relationship("ItemModel", back_populates="categoryType")
    requests = db.relationship("RequestModel", back_populates="categoryType")
    queueItems = db.relationship("QueueItemModel", back_populates="categoryType")
    recommendations = db.relationship("RecommendationModel", back_populates="categoryType")

    def __init__(self, name, categoryID, price):
        self.name = name
        self.categoryID = categoryID
        self.price = price
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'categoryID' : self.categoryID,
            'price' : float(self.price)
        }
    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def find_by_categoryID(cls, categoryID):
        return cls.query.filter_by(categoryID=categoryID).all()
    
    @classmethod
    def find_by_categoryID_name(cls, categoryID, name):
        return cls.query.filter(and_(cls.categoryID==categoryID, cls.name==name)).all()