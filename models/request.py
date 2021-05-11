from db import db
import datetime

class RequestModel(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates="requests")
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel')
    quantity = db.Column(db.Integer)
    dateRequested = db.Column(db.Date)
    comments = db.Column(db.String(200))

    deliveries = db.relationship('DeliveryModel', back_populates="request")
    queueItem = db.relationship('QueueItemModel', back_populates="request")
    unmetRequests = db.relationship('UnmetModel', back_populates="request")

    def __init__(self, userID, categoryTypeID, quantity, 
    comments=None, dateRequested=datetime.datetime.now().date()):
        self.userID = userID
        self.categoryTypeID = categoryTypeID
        self.quantity = quantity
        self.comments = comments
        self.dateRequested = dateRequested
    
    def json(self):
        return {
            'id': self.id,
            'userID': self.userID,
            'categoryTypeID': self.categoryTypeID,
            'quantity': self.quantity,
            'dateRequested': self.dateRequested.isoformat(),
            'comments' : self.comments
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
    def get_all_user_requests(cls, userID):
        return cls.query.filter_by(userID=userID).all()
    

class UnmetModel(db.Model):
    __tablename__ = 'unmetRequests'

    id = db.Column(db.Integer, primary_key=True)
    requestID = db.Column(db.Integer, db.ForeignKey('requests.id'))
    request = db.relationship('RequestModel', back_populates="unmetRequests")
    quantity = db.Column(db.Integer)

    def __init__(self, requestID, quantity):
        self.requestID = requestID
        self.quantity = quantity
    
    def json(self):
        return {
            'id' : self.id,
            'requestID' : self.requestID,
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
    def find_by_request(cls, _requestID):
        return cls.query.filter_by(requestID=_requestID).first()
    
    @classmethod
    def clear(cls):
        cls.query.delete()
        return None
    
    @classmethod
    def clear_by_request(cls, _requestID):
        cls.query.filter(requestID=_requestID).delete()
        db.session.commit()
        return None
    