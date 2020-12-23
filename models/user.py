from db import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    password = db.Column(db.String(80))
    email = db.Column(db.String(200))
    birthday = db.Column(db.String(20))
    income = db.Column(db.Float)
    picture = db.Column(db.String(200))
    householdType = db.Column(db.String(100))
    addressBlockHouseNo = db.Column(db.String(10))
    addressStreetName = db.Column(db.String(200))
    addressLevel = db.Column(db.String(10))
    addressUnitNo = db.Column(db.String(10))
    addressBuildingName = db.Column(db.String(200))
    addressPostalCode = db.Column(db.String(10))
    pin = db.Column(db.String(10))
    pinExpiry = db.Column(db.DateTime)

    def __init__(self, 
    firstName, lastName, password, email, birthday, income, \
    householdType, addressBlockHouseNo, addressStreetName, \
    addressLevel, addressUnitNo, addressPostalCode, addressBuildingName=None, \
    picture=None, pin=None, pinExpiry=None):
        self.firstName = firstName
        self.lastName = lastName
        self.password = password
        self.email = email
        self.birthday = birthday
        self.income = income
        self.picture = picture
        self.householdType = householdType
        self.addressBlockHouseNo = addressBlockHouseNo
        self.addressStreetName = addressStreetName
        self.addressLevel = addressLevel
        self.addressUnitNo = addressUnitNo
        self.addressBuildingName = addressBuildingName
        self.addressPostalCode = addressPostalCode
        self.pin = pin
        self.pinExpiry = pinExpiry

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
            'addressBlockHouseNo': self.addressBlockHouseNo,
            'addressStreetName': self.addressStreetName,
            'addressLevel': self.addressLevel,
            'addressUnitNo': self.addressUnitNo,
            'addressBuildingName': self.addressBuildingName,
            'addressPostalCode': self.addressPostalCode
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