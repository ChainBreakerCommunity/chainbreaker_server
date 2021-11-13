
from server import app, graph
from middleware import token_required
from flask import request, jsonify
import neo4j

@app.route("/api/graph/get_labels_count", methods = ["GET"])
def get_labels_count():
    """
    Counts the number of nodes per label in neo4j
    """
    data = neo4j.get_labels_count(graph)
    return jsonify({"labels_count": data})

@app.route("/api/graph/get_communities", methods = ["GET", "POST"])
@token_required
def get_communities(current_user):
    """
    Returns the communities identified using community detection algorithm
    """
    ALLOWED_ROLES = ["super_reader", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    country = data["country"] if data["country"] != "" else None
    communities = neo4j.get_communities(graph, country)
    return jsonify({"communities": communities})

@app.route("/api/graph/get_community_ads", methods = ["GET", "POST"])
def get_community_ads():
    """
    Returns the community of an specific advertisement.
    """
    data = request.values
    id_community = int(data["id_community"])
    communities = neo4j.get_communities(graph, country = None)
    return jsonify({"ads_ids": communities[str(id_community - 1)]})

@app.route("/api/graph/get_graph_community", methods = ["GET", "POST"])
def get_graph_community():
    """
    Returns the graph of a community.
    """
    data = request.values
    nodeId = data["nodeId"]
    return jsonify({"communities": 200})