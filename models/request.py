from db import db
import datetime

class RequestModel(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel')
    quantity = db.Column(db.Integer)
    dateRequested = db.Column(db.Date)
    preferredDeliveryDateTime = db.Column(db.DateTime)
    comments = db.Column(db.String(200))

    def __init__(self, userID, categoryTypeID, quantity, preferredDeliveryDateTime,
    comments=None, dateRequested=datetime.datetime.now().date()):
        self.userID = userID
        self.categoryTypeID = categoryTypeID
        self.quantity = quantity
        self.preferredDeliveryDateTime = preferredDeliveryDateTime
        self.comments = comments
        self.dateRequested = dateRequested
    
    def json(self):
        return {
            'id': self.id,
            'userID': self.userID,
            'categoryTypeID': self.categoryTypeID,
            'quantity': self.quantity,
            'dateRequested': self.dateRequested,
            'preferredDeliveryDateTime' : self.preferredDeliveryDateTime,
            'comments' : self.comments
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    def get_all_user_requests(self):
        return cls.query.filter_by(userID=userID).all()