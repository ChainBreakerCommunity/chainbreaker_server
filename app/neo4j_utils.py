from py2neo import Graph, NodeMatcher, Node, Relationship
import datetime
import pandas as pd

def get_node(graph, label, **kwargs):
    """
    This function recieves as parameters
    - Graph instance (neo4j)
    - Nodes Matcher instance
    - A label
    - A parameters of the corresponding node
    It checks if the Ad already exists in the database. 
    In case it exists, the node instance is retrived from Neo4j
    Otherwise the node is created, and this instance is retrieve
    """
    nodes_matcher = NodeMatcher(graph)
    result = nodes_matcher.match(label, **kwargs).first()
    # Create node if it doesn't exist.
    if result == None: 
        node = Node(label, **kwargs)
        tx = graph.begin()
        tx.create(node)
        graph.commit(tx)
        return node
    # Otherwise, retrieve the node from neo4j.
    return result     

def get_ads_inside_dates(graph, start_date, end_date):
    query = "MATCH (a: Ad) WHERE date(a.date) >= date('{start_date}') AND date(a.date) <= date('{end_date}') RETURN a.id_ad" \
        .format(start_date = start_date, end_date = end_date)
    ads = graph.run(query).data()
    ids_list = list()
    for ad in ads:
        ids_list.append(ad["a.id_ad"])
    return tuple(ids_list)

def create_new_date_for_ad(graph, id_ad):
    today = datetime.datetime.today()
    datem = datetime.datetime(today.year, today.month, today.day)

    Ad = get_node(graph, "Ad", id_ad = id_ad)
    Date = get_node(graph, "Date", date = datem)
    Ad_Date = Relationship(Ad, "HAS_DATE", Date)
    tx = graph.begin()
    tx.create(Ad_Date) 
    graph.commit(tx)

def create_ad(graph, data):
    """
    This function recieves a graph instance and ad dictionary data 
    and generates all the neccessary operations in order to upload 
    the information to neo4j graph database.
    Important: It is assume that all field in data are str type or NoneType.

    - id_ad must be saved as integer
    - phone must be saved as integer
    - date must be saved as date
    """

    # Prepare & format params.
    params = {"id_ad": int(data["id_ad"]), "language": data["language"], "link": data["link"], "category": data["category"], 
              "phone": int(data["phone"]), "title": data["title"], "text": data["text"], "country": data["country"], "region": data["region"], 
              "city": data["city"], "website": data["website"], "date": datetime.datetime.strptime(data["first_post_date"], "%Y-%m-%d")}
    if data["external_website"] != None and data["external_website"] != "": 
        params["external_website"] = data["external_website"]

    # Create Ad Node.
    Ad = Node("Ad", **params)

    # Create/Get linked Nodes.    
    Date = get_node(graph, "Date", date = params["date"])
    Language = get_node(graph, "Language", language = params["language"]) 
    Website = get_node(graph, "Website", name = params["website"])
    Category = get_node(graph, "Category", name = params["category"])
    Phone = get_node(graph, "Phone", number = params["phone"])
    Country = get_node(graph, "Country", name = params["country"])
    Region = get_node(graph, "Region", name = params["region"])
    City = get_node(graph, "City", name = params["city"])
     
    # Create Relantionships.
    Ad_Language = Relationship(Ad, "HAS_LANGUAGE", Language)
    Ad_Date = Relationship(Ad, "HAS_DATE", Date)
    Ad_Website = Relationship(Ad, "HAS_WEBSITE", Website)
    Ad_Category = Relationship(Ad, "HAS_CATEGORY", Category)
    Ad_Phone = Relationship(Ad, "HAS_PHONE", Phone)
    Ad_Country = Relationship(Ad, "HAS_COUNTRY", Country)
    Ad_Region = Relationship(Ad, "HAS_REGION", Region)
    Ad_City = Relationship(Ad, "HAS_CITY", City)
    
    # Generate transaction and commit.
    tx = graph.begin()
    tx.create(Ad)    
    tx.create(Ad_Language)
    tx.create(Ad_Date)
    tx.create(Ad_Website)
    tx.create(Ad_Category)
    tx.create(Ad_Phone)
    tx.create(Ad_Country)
    tx.create(Ad_Region)
    tx.create(Ad_City)
    
    if data["external_website"] != None and data["external_website"] != "":
        ExternalWebsite = get_node(graph, "ExternalWebsite", name = data["external_website"])
        Ad_ExternalWebsite = Relationship(Ad, "HAS_EXTERNAL_WEBSITE", ExternalWebsite)
        tx.create(ExternalWebsite)
        tx.create(Ad_ExternalWebsite)
    
    # Generate relations between pre-existing ads based on external_website and phone attributes.
    if data["external_website"] != None and data["external_website"] != "":
        query = "MATCH (a: Ad) WHERE (a.id_ad <> {id_ad}) AND (a.external_website = '{external_website}' OR a.phone = {phone}) RETURN a" \
            .format(id_ad = params["id_ad"], external_website = params["external_website"], phone = params["phone"])
    else:
        query = "MATCH (a: Ad) WHERE (a.id_ad <> {id_ad}) AND a.phone = {phone} RETURN a" \
            .format(id_ad = params["id_ad"], phone = params["phone"])
    related_ads = graph.run(query).data()
    
    for res in related_ads:
        node = res["a"]
        if node["id_ad"] != params["id_ad"]:
            Ad_Related_Ad_1 = Relationship(Ad, "HAS_RELATION", node)
            tx.create(Ad_Related_Ad_1)
            break  # Only consider the first result so we avoid to create un-informative relationships.

    # Commit all operations.
    graph.commit(tx)

def get_labels_count(graph):
    output = list()
    for label in graph.run("CALL db.labels()").to_series():
        result = {}
        query = f"MATCH (:`{label}`) RETURN count(*) as count"
        count = graph.run(query).to_data_frame().iloc[0]['count']
        result["label"] = str(label)
        result["count"] = str(count)
        output.append(result)
    return output

def get_communities(graph, country):

    # Create temporary graph consisting in Ads and undirected relationships.
    create_query = """
    CALL gds.graph.create(
        "in-memory-graph-1633830502056", 
        "Ad", 
        {
            HAS_RELATION: {
                orientation: "UNDIRECTED"
            }
        },
        {} 
    )
    """
    # Run query.
    res = graph.run(create_query)
    
    # Apply weak connected components algorithm on the previous created graph.
    detection_query = """
    CALL gds.wcc.stream("in-memory-graph-1633830502056")
    YIELD nodeId, componentId AS community
    WITH gds.util.asNode(nodeId) as ad, community
    """
    if country != None:
        detection_query += " WHERE ad.country = '{country}'".format(country = country)
    detection_query += " RETURN ad.id_ad, ad.website, ad.country, community"

    # Get results
    results = graph.run(detection_query).data()

    # Delete temporary graph.
    graph.run("CALL gds.graph.drop('in-memory-graph-1633830502056');")

    # Get communities.
    data = pd.DataFrame(results)
    data.columns = ["id_ad", "website", "country", "community"]
    #print(data.tail())
    communities = {}
    for i in range(len(data)):
        row = data.iloc[i]
        id_ad = str(row["id_ad"])
        community_id = str(row["community"])
        if community_id not in communities:
            communities[community_id] = list([id_ad])
        else:
            communities[community_id].append(id_ad)

    # Return results.
    return communities

