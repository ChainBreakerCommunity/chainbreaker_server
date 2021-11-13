from server import db
class Ad(db.Model):
    """
    Define Ad Model
    """
    __tablename__ = "ad"
    id_ad = db.Column(db.Integer, primary_key=True)
    data_version = db.Column(db.Integer)
    author = db.Column(db.String(30))
    language = db.Column(db.String(20))
    link = db.Column(db.String(100))
    id_page = db.Column(db.Integer)
    title = db.Column(db.String(100))
    text = db.Column(db.String(10000))
    category = db.Column(db.String(20))
    first_post_date = db.Column(db.DateTime(10))
    extract_date = db.Column(db.DateTime(10))
    website = db.Column(db.String(20))

    phone = db.Column(db.Integer)

    country = db.Column(db.String(30))
    region = db.Column(db.String(30))
    city = db.Column(db.String(30))
    place = db.Column(db.String(30))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zoom = db.Column(db.Integer)

    email = db.Column(db.String(100))
    verified_ad = db.Column(db.Boolean())
    prepayment = db.Column(db.Boolean())
    promoted_ad = db.Column(db.Boolean())
    external_website = db.Column(db.String(100))
    reviews_website = db.Column(db.String(100))

    nationality = db.Column(db.String(100))
    age = db.Column(db.Integer)

    score_risk = db.Column(db.Float)

    def __init__(self, data_version, author, language, link, id_page, title, text, 
                category, first_post_date, extract_date, website, phone, country, region, 
                city, place, latitude, longitude, zoom, email = None, 
                verified_ad = None, prepayment = None, promoted_ad = None, external_website = None,
                reviews_website = None, nationality = None, age = None, score_risk = None):

        self.data_version = data_version
        self.author = author
        self.language = language
        self.link = link
        self.id_page = id_page
        self.title = title
        self.text = text
        self.category = category
        self.first_post_date = first_post_date
        self.extract_date = extract_date
        self.website = website

        self.phone = phone

        self.country = country
        self.region = region
        self.city = city
        self.place = place
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom

        self.email = email
        self.verified_ad = verified_ad
        self.prepayment = prepayment
        self.promoted_ad = promoted_ad
        self.external_website = external_website
        self.reviews_website = reviews_website

        self.nationality = nationality
        self.age = age
        self.score_risk = score_risk
