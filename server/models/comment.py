from server import db
class Comment(db.Model):
    """
    Define Comment Model
    """
    __tablename__ = "comment"
    id_comment = db.Column(db.Integer, primary_key = True)
    id_ad = db.Column(db.Integer)
    comment = db.Column(db.String(1000))

    def __init__(self, id_ad, comment):
        self.id_ad = id_ad
        self.comment = comment
