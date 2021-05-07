from db import db
from sqlalchemy import and_

class ScoreModel(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel')
    regret = db.Column(db.Float)
    temporalRegret = db.Column(db.Float)

    def __init__(self, userID, categoryTypeID, regret=0, temporalRegret=0):
        self.userID = userID
        self.categoryTypeID = categoryTypeID
        self.regret = regret
        self.temporalRegret = temporalRegret
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def json(self):
        return {
            'id' : self,id,
            'categoryTypeID' : self.categoryTypeID,
            'regret' : float(self.regret),
            'temporalRegret' : float(self.temporalRegret)
        }
    
    @classmethod
    def find_by_categoryType(cls, categoryTypeID):
        return cls.query.filter_by(categoryTypeID=categoryTypeID).all()
    
    @classmethod
    def find_by_user(cls, userID):
        return cls.query.filter_by(userID=userID).all()
    
    @classmethod
    def find_by_user_and_categoryType(cls, userID, categoryTypeID):
        return cls.query.filter(and_(cls.userID=userID, cls.categoryTypeID=categoryTypeID))