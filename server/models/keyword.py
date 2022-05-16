from server import db
class Keyword(db.Model):
    """
    Define Keyword Model
    """
    __tablename__ = "keyword"
    id_keyword = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20))
    keyword = db.Column(db.String(30))
    english_translation = db.Column(db.String(30))
    meaning = db.Column(db.String(1000))
    age_flag = db.Column(db.Boolean())
    trafficking_flag = db.Column(db.Boolean())
    movement_flag = db.Column(db.Boolean())