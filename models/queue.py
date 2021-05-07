from db import db
import datetime

class QueueItemModel(db.Model):
    __tablename__ = 'queueitems'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates="queueItems")
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel', back_populates="queueItems")
    requestID = db.Column(db.Integer, db.ForeignKey('requests.id'))
    request = db.relationship('RequestModel', back_populates="queueItem")
    timeRequested = db.Column(db.Date)
    allocation = db.Column(db.Integer)

    recommendations = db.relationship('RecommendationModel', back_populates="queueItem")

    def __init__(self, userID, categoryTypeID, requestID, timeRequested=datetime.datetime.now().date(), points=0, allocation=0):
        self.userID = userID
        self.categoryTypeID = categoryTypeID
        self.requestID = requestID
        self.timeRequested = timeRequested
        self.allocation = allocation
    
    def json(self):
        return {
            'id' : self.id,
            'userID' : self.userID,
            'categoryTypeID' : self.categoryTypeID,
            'requestID' : self.requestID,
            'timeRequested' : self.timeRequested.isoformat(),
            'allocation' : self.allocation
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
    
    @classmethod
    def find_by_user(cls, _userID):
        return cls.query.filter_by(userID=_userID).order_by(cls.timeRequested).all()
    
    @classmethod
    def find_by_categoryTypeID(cls, categoryTypeID):
        return cls.query.filter_by(categoryTypeID=categoryTypeID).all()