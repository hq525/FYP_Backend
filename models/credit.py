from db import db

class CreditModel(db.Model):
    __tablename__ = 'credittable'

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates="credit")
    credits = db.Column(db.Integer)

    def __init__(self, userID, credits=0):
        self.userID = userID
        self.credits = credits
    
    def json(self):
        return {
            'id' : self.id,
            'userID' : self.userID,
            'credits' : self.credits
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
    def find_by_user_id(cls, _userID):
        return cls.query.filter_by(userID=_userID).first()