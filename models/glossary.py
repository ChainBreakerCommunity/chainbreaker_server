
from utils.db import db

class Glossary(db.Model):
    """
    Define Glossary Model
    """
    __tablename__ = "glossary"
    id_term = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(20))
    term = db.Column(db.String(30))
    definition = db.Column(db.String(1000))
