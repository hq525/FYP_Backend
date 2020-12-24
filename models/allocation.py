from db import db

class AllocationModel(db.Model):
    __tablename__ = 'allocations'

    id = db.Column(db.Integer, primary_key=True)
    requestID = db.Column(db.Integer, db.ForeignKey('requests.id'))
    request = db.relationship('RequestModel')
    delivererID = db.Column(db.Integer, db.ForeignKey('users.id'))
    deliverer = db.relationship('UserModel')
    itemID = db.Column(db.Integer, db.ForeignKey('items.id'))
    item = db.relationship('ItemModel')
    dateTime = db.Column(db.DateTime)
    confirmationCode = db.Column(db.String(10))
    status = db.Column(db.String(80))
    collectionDateTime = db.Column(db.DateTime)
    deliveryDateTime = db.Column(db.DateTime)

    def __init__(self, requestID, delivererID, itemID, dateTime, confirmationCode,
    status, collectionDateTime, deliveryDateTime):
        self.requestID = requestID
        self.delivererID = delivererID
        self.itemID = itemID
        self.dateTime = dateTime
        self.confirmationCode = confirmationCode
        self.status = status
        self.collectionDateTime = collectionDateTime
        self.deliveryDateTime = deliveryDateTime
    
    def json(self):
        return {
            'id': self.id,
            'requestID': self.requestID,
            'delivererID': self.delivererID,
            'itemID': self.itemID,
            'dateTime': self.dateTime,
            'confirmationCode': self.confirmationCode,
            'status': self.status,
            'collectionDateTime': self.collectionDateTime,
            'deliveryDateTime': self.deliveryDateTime
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
