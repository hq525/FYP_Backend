from db import db

class RatingModel(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    raterID = db.Column(db.Integer, db.ForeignKey('users.id'))
    rater = db.relationship('UserModel', back_populates="ratingsGiven", foreign_keys=[raterID])
    rateeID = db.Column(db.Integer, db.ForeignKey('users.id'))
    ratee = db.relationship('UserModel', back_populates="ratingsReceived", foreign_keys=[rateeID])
    deliveryID = db.Column(db.Integer, db.ForeignKey('delivery.id'))
    delivery = db.relationship('DeliveryModel', back_populates="rating")
    rating = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    feedback = db.Column(db.String(300))

    def __init__(self, raterID, rateeID, deliveryID, rating, date, feedback):
        self.raterID = raterID
        self.rateeID = rateeID
        self.deliveryID = deliveryID
        self.rating = rating
        self.date = date
        self.feedback = feedback
    
    def json(self):
        return {
            'id' : self.id,
            'raterID' : self.raterID,
            'rateeID' : self.rateeID,
            'deliveryID' : self.deliveryID,
            'rating' : self.rating,
            'date' : self.date.isoformat(),
            'feedback' : self.feedback
        }

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_delivery_id(cls, _deliveryID):
        return cls.query.filter_by(deliveryID=_deliveryID).first()
    
    @classmethod
    def get_ratee_ratings(cls, _rateeID):
        return cls.query.filter_by(rateeID=_rateeID).all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
