from server import db
class User(db.Model):
    """
    Define User Model
    """
    __tablename__ = "user"
    id_user = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(100))
    permission = db.Column(db.String(10))

    def __init__(self, name, email, password, permission):
        self.name = name
        self.email = email
        self.password = password
        self.permission = permission