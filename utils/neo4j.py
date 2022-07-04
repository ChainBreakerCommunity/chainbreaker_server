from py2neo import Graph, NodeMatcher, Node, Relationship, Transaction
import datetime
from typing import List
import json
from utils.env import get_config
config = get_config()

graph = Graph(config["NEO4J_ENDPOINT"], user = config["NEO4J_USER"], password = config["NEO4J_PASSWORD"])

def get_node(label: str, **kwargs) -> Node:
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

def get_ads_inside_dates(start_date, end_date) -> tuple:
    query = "MATCH (a: Ad) WHERE date(a.date) >= date('{start_date}') AND date(a.date) <= date('{end_date}') RETURN a.id_ad" \
        .format(start_date = start_date, end_date = end_date)
    ads = graph.run(query).data()
    ids_list = list()
    for ad in ads:
        ids_list.append(ad["a.id_ad"])
    return tuple(ids_list)

def create_new_date_for_ad(id_ad: int) -> None:
    today = datetime.datetime.today()
    datem = datetime.datetime(today.year, today.month, today.day)

    Ad = get_node("Ad", id_ad = id_ad)
    Date = get_node("Date", date = datem)
    Ad_Date = Relationship(Ad, "HAS_DATE", Date)
    tx = graph.begin()
    tx.create(Ad_Date) 
    graph.commit(tx)

def create_ad(data: dict):
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
    params = {
                "id_ad": int(data["id_ad"]), 
                "language": data["language"], 
                "link": data["link"], 
                "category": data["category"], 
                "title": data["title"], 
                "text": data["text"], 
                "country": data["country"], 
                "region": data["region"], 
                "city": data["city"], 
                "website": data["website"], 
                "date": datetime.datetime.strptime(data["first_post_date"], "%Y-%m-%d")
            }

    # Previously, we guarantee that at least one of the following values is not None!
    if data["phone"] != "":
        params["phone"] = data["phone"]
    if data["external_website"] != "": 
        params["external_website"] = data["external_website"]
    if data["email"] != "":
        params["email"] = data["email"]

    # Create Ad Node.
    Ad = Node("Ad", **params)

    # Create/Get linked Nodes.    
    Date = get_node("Date", date = params["date"])
    Language = get_node("Language", language = params["language"]) 
    Website = get_node("Website", name = params["website"])
    Category = get_node("Category", name = params["category"])
    Country = get_node("Country", name = params["country"])
    Region = get_node("Region", name = params["region"])
    City = get_node("City", name = params["city"])
     
    # Create Relantionships.
    Ad_Language = Relationship(Ad, "HAS_LANGUAGE", Language)
    Ad_Date = Relationship(Ad, "HAS_DATE", Date)
    Ad_Website = Relationship(Ad, "HAS_WEBSITE", Website)
    Ad_Category = Relationship(Ad, "HAS_CATEGORY", Category)
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
    tx.create(Ad_Country)
    tx.create(Ad_Region)
    tx.create(Ad_City)
    
    if data["phone"] != "":
        Phone = get_node("Phone", number = params["phone"])
        Ad_Phone = Relationship(Ad, "HAS_PHONE", Phone)
        tx.create(Phone)
        tx.create(Ad_Phone)

    if data["external_website"] != "":
        ExternalWebsite = get_node("ExternalWebsite", name = data["external_website"])
        Ad_ExternalWebsite = Relationship(Ad, "HAS_EXTERNAL_WEBSITE", ExternalWebsite)
        tx.create(ExternalWebsite)
        tx.create(Ad_ExternalWebsite)

    if data["email"] != "":
        Email = get_node("Email", name = data["email"])
        Ad_Email = Relationship(Ad, "HAS_EMAIL", Email)
        tx.create(Email)
        tx.create(Ad_Email)

    # Return graph and tx object.
    return graph, tx

def get_labels_count() -> List:
    output = list()
    for label in graph.run("CALL db.labels()").to_series():
        result = {}
        query = f"MATCH (:`{label}`) RETURN count(*) as count"
        count = graph.run(query).to_data_frame().iloc[0]['count']
        result["label"] = str(label)
        result["count"] = str(count)
        output.append(result)
    return output

def delete_graph():
    query = "CALL gds.graph.drop('in-memory-graph-1655055741396');"
    graph.run(query)

def get_communities(country: str or None) -> List[List[int]]:

    query = """CALL gds.graph.create(
                'in-memory-graph-1655055741396', 
                ['Ad', 'ExternalWebsite', 'Email', 'Phone'], 
                {
                    HAS_PHONE: {
                        orientation: 'UNDIRECTED',
                        properties: {}
                    }, 
                    HAS_EXTERNAL_WEBSITE: {
                        orientation: 'UNDIRECTED',
                        properties: {}
                    }, 
                    HAS_EMAIL: {
                        orientation: 'UNDIRECTED',
                        properties: {}
                    }
                }, 
                {});
            """
    graph.run(query)

    query = """
            CALL gds.wcc.stream('in-memory-graph-1655055741396', {}) 
            YIELD nodeId, componentId AS community
            WITH gds.util.asNode(nodeId) AS node, community
            WITH collect(node) AS allNodes, community
            RETURN community, allNodes AS nodes, size(allNodes) AS size
            ORDER BY size DESC
            """
    results = graph.run(query).data()

    query = "CALL gds.graph.drop('in-memory-graph-1655055741396');"
    graph.run(query)

    communities = list()

    for i in range(len(results)):
        community = results[i]["nodes"]
        ads_community = list()
        add_to = True
        for i in range(len(community)):
            node = community[i]
            if node.has_label("Ad"):
                ad_country = node["country"]
                if country != "":
                    if ad_country != country:
                        add_to = False
                        # Examine next community because we only care about a specific country!
                        continue
                id_ad = node["id_ad"]
                ads_community.append(id_ad)
        if add_to == True:
            communities.append(ads_community)
    return communities

def get_node_info(label: str, attributes: dict):
    nodes_matcher = NodeMatcher(graph)
    attributes = {"id_ad": int(attributes["id_ad"])}
    result = nodes_matcher.match(label, **attributes).first()
    if result == None:
        return False
    result = result["node"]
    return result

def get_last_ad():
    counts = get_labels_count()
    number = 0
    for c in counts:
        if c["label"] == "Ad":
            number = c["count"]
            break
    nodes_matcher = NodeMatcher(graph)
    result = dict(nodes_matcher.match("Ad").skip(int(number) - 1).first())
    result = json.dumps(result, indent=4, sort_keys=True, default=str)
    return result
