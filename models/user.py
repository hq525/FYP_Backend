from db import db
import datetime
from sqlalchemy import and_, or_
from models.rating import RatingModel
from models.recommendation import RecommendationModel

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    password = db.Column(db.String(80))
    email = db.Column(db.String(200))
    birthday = db.Column(db.String(20))
    income = db.Column(db.Integer)
    picture = db.Column(db.String(200))
    householdType = db.Column(db.String(100))
    householdCount = db.Column(db.Integer)
    addressLine1 = db.Column(db.String(200))
    addressLine2 = db.Column(db.String(200))
    addressPostalCode = db.Column(db.String(10))
    lat = db.Column(db.DECIMAL(9, 6))
    lng = db.Column(db.DECIMAL(9, 6))
    pin = db.Column(db.String(10))
    pinExpiry = db.Column(db.DateTime)
    totalRating = db.Column(db.Integer)
    noOfRatings = db.Column(db.Integer)

    items = db.relationship("ItemModel", back_populates="user", cascade="all, delete", passive_deletes=True)
    availabilities = db.relationship("UserAvailabilityModel", back_populates="user", cascade="all, delete", passive_deletes=True)
    requests = db.relationship("RequestModel", back_populates="user")
    ratingsGiven = db.relationship("RatingModel", back_populates="rater", foreign_keys=[RatingModel.raterID])
    ratingsReceived = db.relationship("RatingModel", back_populates="ratee", foreign_keys=[RatingModel.rateeID])
    credit = db.relationship("CreditModel", back_populates="user")
    queueItems = db.relationship("QueueItemModel", back_populates="user")
    deliveries = db.relationship("DeliveryModel", back_populates="deliverer")

    def __init__(self, 
    firstName, lastName, password, email, birthday, income, \
    householdType, addressLine1, addressLine2, addressPostalCode, householdCount, lat, lng, \
    picture=None, pin=None, pinExpiry=None, averageRating=0, noOfRatings=0):
        self.firstName = firstName
        self.lastName = lastName
        self.password = password
        self.email = email
        self.birthday = birthday
        self.income = income
        self.picture = picture
        self.householdType = householdType
        self.householdCount = householdCount
        self.addressLine1 = addressLine1
        self.addressLine2 = addressLine2
        self.addressPostalCode = addressPostalCode
        self.lat = lat
        self.lng = lng
        self.pin = pin
        self.pinExpiry = pinExpiry
        self.averageRating = averageRating
        self.noOfRatings = noOfRatings

    def json(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'birthday': self.birthday,
            'income': self.income,
            'picture': self.picture,
            'householdType': self.householdType,
            'householdCount' : self.householdCount,
            'addressLine1': self.addressLine1,
            'addressLine2': self.addressLine2,
            'addressPostalCode': self.addressPostalCode,
            'lat': str(self.lat),
            'lng': str(self.lng)
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

class UserAvailabilityModel(db.Model):
    __tablename__ = 'user_availability'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    user = db.relationship('UserModel', back_populates="availabilities")
    startDateTime = db.Column(db.DateTime)
    endDateTime = db.Column(db.DateTime)

    def __init__(self, userID, startDateTime, endDateTime):
        self.userID = userID
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
    
    def json(self):
        return {
            'id': self.id,
            'userID': self.userID,
            'startDateTime' : self.startDateTime.isoformat(),
            'endDateTime' : self.endDateTime.isoformat()
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
    def find_all_in_range(cls, startDateTime, endDateTime):
        return cls.query.filter(or_(and_(cls.startDateTime >= startDateTime, cls.startDateTime <= endDateTime),and_(cls.endDateTime >= startDateTime, cls.endDateTime <= endDateTime),and_(cls.startDateTime <= startDateTime, cls.endDateTime >= endDateTime))).all()

    @classmethod
    def find_in_range(cls, userID, startDateTime, endDateTime):
        return cls.query.filter(and_(cls.userID == userID, or_(and_(cls.startDateTime >= startDateTime, cls.startDateTime <= endDateTime),and_(cls.endDateTime >= startDateTime, cls.endDateTime <= endDateTime),and_(cls.startDateTime <= startDateTime, cls.endDateTime >= endDateTime)))).all()

    @classmethod
    def find_in_range_first(cls, userID, startDateTime, endDateTime):
        return cls.query.filter(and_(cls.userID == userID, or_(and_(cls.startDateTime >= startDateTime, cls.startDateTime <= endDateTime),and_(cls.endDateTime >= startDateTime, cls.endDateTime <= endDateTime),and_(cls.startDateTime <= startDateTime, cls.endDateTime >= endDateTime)))).limit(1).all()

    @classmethod
    def find_exact_range(cls, userID, startDateTime, endDateTime):
        return cls.query.filter(and_(cls.userID == userID, and_(cls.startDateTime == startDateTime, cls.endDateTime == endDateTime))).first()