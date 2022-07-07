from models.ad import Ad
from typing import List 

def textToHash(text):
    import hashlib
    hash_function = hashlib.sha256()
    x = bytes(str(text), "utf-8")
    hash_function.update(x)
    hash = hash_function.hexdigest()
    return hash

def format_ads_reduced_to_json(ads):
    """
    Format reduced version of ads data to json.
    """
    output = list()
    for ad in ads: 
        ad_data = {}

        # Ad data.
        ad_data["id_ad"] = ad.id_ad
        ad_data["language"] = ad.language
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 

        # Location data.
        ad_data["country"] = ad.country
        ad_data["city"] = ad.city

        # Website.
        ad_data["external_website"] = ad.external_website
        output.append(ad_data)

    return output

def format_ads_to_json(ads: List[Ad], secure = False):
    """
    Format Ads Data to json.
    """
    last_id = 0
    output = list()

    for ad in ads: 
        ad_data = {}

        # Ad data.
        ad_data["id_ad"] = ad.id_ad
        ad_data["data_version"] = ad.data_version
        ad_data["author"] = ad.author
        ad_data["language"] = ad.language
        ad_data["link"] = textToHash(ad.link) if (not secure and ad.link != None) else ad.link
        ad_data["id_page"] = ad.id_page
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 
        ad_data["first_post_date"] = ad.first_post_date
        ad_data["extract_date"] = ad.extract_date 
        ad_data["website"] = ad.website 

        # Ethnicity data.
        ad_data["ethnicity"] = ad.ethnicity

        # Phone data.
        ad_data["phone"] = textToHash(ad.phone) if (not secure and ad.phone != None) else ad.phone

        # Location data.
        ad_data["country"] = ad.country
        ad_data["region"] = ad.region
        ad_data["city"] = ad.city
        ad_data["place"] = ad.place
        ad_data["latitude"] = ad.latitude
        ad_data["longitude"] = ad.longitude
        ad_data["zoom"] = ad.zoom
        ad_data["email"] = textToHash(ad.email) if (not secure and ad.email != None) else ad.email
        ad_data["verified_ad"] = ad.verified_ad
        ad_data["prepayment"] = ad.prepayment 
        ad_data["promoted_ad"] = ad.promoted_ad 
        ad_data["external_website"] = textToHash(ad.external_website) if (not secure and ad.external_website != None) else ad.external_website
        ad_data["reviews_website"] = textToHash(ad.reviews_website) if (not secure and ad.reviews_website != None) else ad.reviews_website
        ad_data["nationality"] = ad.nationality
        ad_data["age"] = ad.age
        ad_data["score_risk"] = ad.score_risk

        last_id = ad.id_ad
        output.append(ad_data)

    return output, last_id