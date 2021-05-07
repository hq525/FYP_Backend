from db import db

class DeliveryModel(db.Model):
    __tablename__ = 'delivery'

    id = db.Column(db.Integer, primary_key=True)
    requestID = db.Column(db.Integer, db.ForeignKey('requests.id'))
    request = db.relationship('RequestModel', back_populates="deliveries")
    delivererID = db.Column(db.Integer, db.ForeignKey('users.id'))
    deliverer = db.relationship('UserModel', back_populates="deliveries")
    itemID = db.Column(db.Integer, db.ForeignKey('itemsTable.id'))
    item = db.relationship('ItemModel', back_populates="deliveries")
    dateTime = db.Column(db.DateTime)
    confirmationCode = db.Column(db.String(10))
    delivererAccepted = db.Column(db.Boolean)
    donorAccepted = db.Column(db.Boolean)
    beneficiaryAccepted = db.Column(db.Boolean)
    delivered = db.Column(db.Boolean)
    quantity = db.Column(db.Integer)
    collectionDateTime = db.Column(db.DateTime)
    deliveryDateTime = db.Column(db.DateTime)
    itemName = db.Column(db.String(100))

    rating = db.relationship('RatingModel', back_populates="delivery")

    def __init__(self, requestID, delivererID, itemID, dateTime, confirmationCode,
    quantity, collectionDateTime, deliveryDateTime, itemName, donorAccepted=None, 
    delivererAccepted=None, delivered=None, beneficiaryAccepted=None):
        self.requestID = requestID
        self.delivererID = delivererID
        self.itemID = itemID
        self.dateTime = dateTime
        self.confirmationCode = confirmationCode
        self.quantity = quantity
        self.collectionDateTime = collectionDateTime
        self.deliveryDateTime = deliveryDateTime
        self.donorAccepted = donorAccepted
        self.delivererAccepted = delivererAccepted
        self.delivered = delivered
        self.itemName = itemName
        self.beneficiaryAccepted = beneficiaryAccepted
    
    def json(self):
        return {
            'id': self.id,
            'requestID': self.requestID,
            'delivererID': self.delivererID,
            'itemID': self.itemID,
            'dateTime': self.dateTime.isoformat(),
            'quantity' : self.quantity,
            'donorAccepted' : self.donorAccepted,
            'delivererAccepted' : self.delivererAccepted,
            'delivered' : self.delivered,
            'collectionDateTime': self.collectionDateTime.isoformat(),
            'deliveryDateTime': self.deliveryDateTime.isoformat(),
            'itemName' : self.itemName,
            'beneficiaryAccepted' : self.beneficiaryAccepted
        }

    @classmethod
    def get_user_deliveries(cls, userID):
        return cls.query.filter_by(delivererID=userID).all()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def setDonorAccepted(self):
        self.donorAccepted = True
        db.session.commit()

    def setDelivererAccepted(self):
        self.delivererAccepted = True
        db.session.commit()
    
    def setBeneficiaryAccepted(self):
        self.beneficiaryAccepted = True
        db.session.commit()

    def setDelivered(self):
        self.delivered = True
        db.session.commit()