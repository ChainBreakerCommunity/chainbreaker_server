# Import libraries.
import requests

# Weak Supervision.
import spacy
nlp_en = spacy.load("en_core_web_sm")
nlp_es = spacy.load("es_core_news_sm")
nlp_dict = {}
nlp_dict["english"] = nlp_en
nlp_dict["spanish"] = nlp_es

# Import some libraries.
from typing import List

def format_string(text: str):
    text = text.lower()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    text = text.strip()
    return text

# 1. Third Person.

# Pronouns.
THIRD_PERSON_SINGULAR = {}
THIRD_PERSON_PLURAL = {}
FIRST_PLURAL_PERSON_PRONOUNS = {}

THIRD_PERSON_SINGULAR["spanish"] = ["él", "ella"]
THIRD_PERSON_PLURAL["spanish"] = ["ellos", "ellas"]
FIRST_PLURAL_PERSON_PRONOUNS["spanish"] = ["nosotros", "nosotras", "nos"]

THIRD_PERSON_SINGULAR["english"] = ["he", "him", "his", "himself", "she", "her", "hers", "herself"]
THIRD_PERSON_PLURAL["english"] = ["they", "them", "their", "theirs", "themselves"]
FIRST_PLURAL_PERSON_PRONOUNS["english"] = ["we", "us", "our", "ours", "ourselves"]

def get_third_person(language: str, text: str):

    def get_third_person_singular(language: str, text:str):
        nlp = nlp_dict[language]
        doc = nlp(text)
        #print(doc)
        for token in doc:
            #print("token: ", token)
            lemma = token.lemma_.lower()
            if lemma in THIRD_PERSON_SINGULAR[language][1:]:
                print(lemma)
                return True
        for word in THIRD_PERSON_SINGULAR[language]:
            search_word = " " + word + " "
            if text.find(search_word) != -1:
                print(word)
                return True
        return False

    def get_third_person_plural(language: str, text:str):
        nlp = nlp_dict[language]
        doc = nlp(text)
        for token in doc:
            lemma = token.lemma_.lower()
        
            if lemma in THIRD_PERSON_PLURAL[language]:
                print(lemma)
                return True
        for word in THIRD_PERSON_PLURAL[language]:
            search_word = " " + word + " "
            if text.find(search_word) != -1:
                print(word)
                return True
        return False

    b1 = get_third_person_singular(language, text)
    b2 = get_third_person_plural(language, text)
    return (b1 or b2)

# 2. First plural person.
def get_first_plural_person(language: str, text: str):
    
    def get_first_plural_person(language: str, text:str):
        nlp = nlp_dict[language]
        doc = nlp(text)
        for token in doc:
            lemma = token.lemma_.lower()
            if lemma in FIRST_PLURAL_PERSON_PRONOUNS[language]:
                #print(lemma)
                return True
        for word in FIRST_PLURAL_PERSON_PRONOUNS[language]:
            search_word = " " + word + " "
            if text.find(search_word) != -1:
                return True
        return False

    def get_plural_verbs(language: str, text: str):
        """
        This function returns true if the text contain plural verbs
        Example: ofrecemos complacemos besamos queremos 
        """
        nlp = nlp_dict[language]
        doc = nlp(text)
        for token in doc:
            if token.pos_ == "VERB":
                if "Plur" in token.tag_ and "Ind" in token.tag_ and "Person=1" in token.tag_:
                    if language == "spanish" and "emos" in str(token):
                        return True
                    elif language != "spanish":
                        return True
        return False

    b1 = get_plural_verbs(language, text)
    b2 = get_first_plural_person(language, text)
    return (b1 or b2)

# 3. Sex type.
def get_sex_type(language: str, text: str):

    dicc = {
        "0-0-0": 0,
        "1-0-0": 1,
        "0-1-0": 2,
        "0-0-1": 3,
        "1-1-0": 4,
        "1-0-1": 5,
        "0-1-1": 6,
        "1-1-1": 7,
    }

    oral_words = ["oral", "sexo oral", "un delicioso", "paja"]
    vaginal_words = ["vaginal", "sexo vaginal", "poses", "en cuatro", "buen sexo", "penetraciones", "penetrando", "penetrar"]
    anal_words = ["anal", "sexo anal", "beso negro"]

    def search_words(words: List[str]):
        for word in words:
            if text.find(word) != -1:
                return text.find(word)
        return -1

    def service_is_offered(position: int):
        if position == -1:
           return "0"
        subtext = text[position-30:position]
        if subtext.find("no") == -1:
           return "1"
        return "0"

    oral = service_is_offered(search_words(oral_words))
    vaginal = service_is_offered(search_words(vaginal_words))
    anal = service_is_offered(search_words(anal_words))


    return dicc[oral + "-" + vaginal + "-" + anal]

# 4. Preservative.
def get_preservative(language: str, text: str):
    dicc = {
        "0-0": 0, 
        "0-1": 2,
        "1-0": 1,
        "1-1": 1
    }
    without_preservative_words = ["sin proteccion", "sin preservativo", "sin condon", "sin gorrito"]
    with_preservative_words = ["con proteccion", "con condon", "gorrito", "con preservativo"]

    def search_words(words: List[str]):
        for word in words:
            if text.find(word) != -1:
                print(word)
                return text.find(word)
        return -1
    
    without_preservative = "1" if search_words(without_preservative_words) >= 0 else "0"
    with_preservative = "1" if search_words(with_preservative_words) >= 0 else "0"

    return dicc[without_preservative + "-" + with_preservative]

# 5. Service place.
def get_service_place(language: str, text: str):

    dicc = {
        "0-0": 0, 
        "1-0": 0, 
        "0-1": 2, 
        "1-1": 2, 
    }

    outside_words = ["a domicilio", "domicilios", "hoteles", "moteles", "viajes", "salidas"]
    inside_words = ["tengo sitio", "sitio propio", "apartamento", "estoy ubicada", "estoy ubicado", "con apto",
                   "apto privado"]

    def search_words(words: List[str]):
        for word in words:
            if text.find(word) != -1:
                print(word)
                return text.find(word)
        return -1

    inside = "1" if search_words(inside_words) >= 0 else "0"
    outside = "1" if search_words(outside_words) >= 0 else "0"
    return dicc[inside + "-" + outside]

# Keywords.
def get_keywords(keywords, language: str, text: str):
    """
    Fix misspelling words using https://spacy.io/universe/project/contextualSpellCheck
    """
    age_keywords = list()
    sexual_exploitation_keywords = list()
    movement_keywords = list()
    
    for keyword_obj in keywords:
        #keyword_row = keywords.iloc[i]
        
        language_kw = keyword_obj.language
        keyword = format_string(keyword_obj.keyword)
        
        if keyword == "ama" or keyword == "amo":
           keyword = " " + keyword + " "
      
        age_flag = keyword_obj.age_flag
        trafficking_flag = keyword_obj.trafficking_flag
        movement_flag = keyword_obj.movement_flag
        #meaning = keyword_row.meaning

        #print(keyword, age_flag, trafficking_flag, movement_flag)
        
        if language_kw != language:
            continue

        if text.find(keyword) != -1:
            if trafficking_flag: 
                if keyword not in sexual_exploitation_keywords:
                  sexual_exploitation_keywords.append(keyword)
            if movement_flag:
                if keyword not in movement_keywords:
                  movement_keywords.append(keyword)
            if age_flag:
                if keyword not in age_keywords:
                  age_keywords.append(keyword)
                    
    return age_keywords, sexual_exploitation_keywords, movement_keywords

# 6. Foreing.

# Places of interest.
GERUND_OF_INTEREST = {}
GERUND_OF_INTEREST["colombia"] = ["venezuela", "venezolano", "ecuador", "ecuatoriano", "peru", "peruano", "chile", "bolivia", "argentina"]
GERUND_OF_INTEREST["canada"] = ["asian", "colombian", "venezuelan", "brazilean"]
GERUND_OF_INTEREST["peru"] = ["venezuela", "ecuador", "colombia", "brazil", "chile", "bolivia", "argentina"]

def get_foreign(language: str, ad_country: str, text: str):
    nlp = nlp_dict[language]
    doc = nlp(text)
    nationalities = list()
    for token in doc: 
        if token.lemma_.lower() in GERUND_OF_INTEREST[ad_country]:
            nationalities.append(token.lemma_.lower())
    
    foreign_keywords = ["recien llegada", "pocos dias", "poquitos dias", "por poco tiempo", 
                        "aqui por poco tiempo", "chica nueva", "nueva en el ambiente", "recién llegada", 
                        "nueva en la ciudad", "nueva en tu ciudad", "de regreso"]
    foreign_flag = False
    for word in foreign_keywords:
        if text.find(word) != -1:
            print(word)
            foreign_flag = True
            break
    foreign = True if (foreign_flag or len(nationalities) > 0) else False

    return foreign, ", ".join(nationalities) #, cities

def get_nlp_dicc(ad, Keyword, chainbreaker_website_endpoint):

    # Get attributes.
    id_ad = ad.id_ad
    title = ad.title
    text = ad.text
    country = ad.country
    language = ad.language
      
    # Third person.
    third_person = get_third_person(language, text)

    # First plural person
    first_plural_person = get_first_plural_person(language, text)
    
    # Format text to correctly execute other functions.
    title = format_string(title)
    text = format_string(text)

    # Sex type
    sex_type = get_sex_type(language, title + " " + text)

    # Preservative
    preservative = get_preservative(language, title + " " + text)
  
    # Service place
    service_place = get_service_place(language, title + " " + text)

    # Keywords.
    keywords = Keyword.query.filter_by(language = "spanish").all()
    keywords_res = get_keywords(keywords, "spanish", title + " " + text)
    age_keywords = ", ".join(keywords_res[0]) if ", ".join(keywords_res[0]) != "" else ""
    sexual_exploitation_keywords = ", ".join(keywords_res[1])if ", ".join(keywords_res[1]) != "" else ""
    movement_keywords = ", ".join(keywords_res[2]) if ", ".join(keywords_res[2]) != "" else ""

    # Foreign.
    foreign = get_foreign(language, country, title + " " + text)
    foreign_bool = 1 if foreign[0] else 0
    origin_country = foreign[1]


    data = {}
    data["id_ad"] = id_ad
    data["third_person"] = 1 if third_person else 0 
    data["first_plural_person"] = 1 if first_plural_person else 0

    data["sex_type"] = sex_type
    data["preservative"] = preservative
    data["service_place"] = service_place
    data["foreign"] = foreign_bool
    data["origin_country"] = origin_country


    coin_dicc = {
        "colombia": "COP", 
        "peru": "S", 
        "mexico": "MXN"
    }
    data["coin_type"] = coin_dicc[country]


    data["age_keywords"] = age_keywords
    data["movement_keywords"] = movement_keywords
    data["sexual_exploitation_keywords"] = sexual_exploitation_keywords

    print("Data: ")
    print(data)
    print("")
    print("---")
    
    route = "/api/machine_learning/upload_instance"
    res = requests.post(chainbreaker_website_endpoint + route, data = data)
    return res