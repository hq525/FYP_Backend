from db import db

class RecommendationModel(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    queueItemID = db.Column(db.Integer, db.ForeignKey('queueitems.id'))
    queueItem = db.relationship('QueueItemModel', back_populates="recommendations")
    itemID = db.Column(db.Integer, db.ForeignKey('itemsTable.id'))
    item = db.relationship('ItemModel', back_populates="recommendations")
    categoryTypeID = db.Column(db.Integer, db.ForeignKey('categoryTypes.id'))
    categoryType = db.relationship('CategoryTypeModel', back_populates="recommendations")
    quantity = db.Column(db.Integer)

    def __init__(self, queueItemID, itemID, categoryTypeID, quantity):
        self.queueItemID = queueItemID
        self.itemID = itemID
        self.categoryTypeID = categoryTypeID
        self.quantity = quantity

    def json(self):
        return {
            'id' : self.id,
            'queueItemID' : self.queueItemID,
            'itemID' : self.itemID,
            'categoryTypeID' : self.categoryTypeID,
            'quantity' : self.quantity
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
    def clear(cls):
        cls.query.delete()
        return None