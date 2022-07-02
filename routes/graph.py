from flask import Blueprint, render_template, request, jsonify
from dotenv import dotenv_values
import utils.neo4j
from middlewares.token_required import token_required

from dotenv import dotenv_values
config = dotenv_values(".env")
#import os
#config = os.environ


graph = Blueprint("graph", __name__)

@graph.route("/get_labels_count", methods = ["GET"])
def get_labels_count():
    """Counts the number of nodes per label in neo4j
    """
    if not config["NEO4J_ENABLE"]: 
        return jsonify({"message": "Sorry. Service not available at the moment."}), 400
    data = utils.neo4j.get_labels_count()
    return jsonify({"labels_count": data})

@graph.route("/get_communities", methods = ["POST"])
def get_communities():
    """Returns the communities identified using community detection algorithm
    """
    if not config["NEO4J_ENABLE"]: 
        return jsonify({"message": "Sorry. Service not available at the moment."}), 400
    #ALLOWED_ROLES = ["super_reader", "researcher", "admin"]
    #if current_user.permission not in ALLOWED_ROLES:
    #    return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    country = data["country"] if data["country"] != "" else None
    communities = utils.neo4j.get_communities(country = country)
    return jsonify({"communities": communities})

@graph.route("/delete_graph", methods = ["GET"])
def delete_graph():
    utils.neo4j.delete_graph()
    return jsonify({"message": "ok"}), 200

@graph.route("/get_node_info", methods = ["POST"])
def get_node_info():
    data = dict(request.values)
    label = data["label"]
    del data['label']
    node = utils.neo4j.get_node_info(label, data)
    return jsonify({"node": node}), 200

@graph.route("/get_last_ad", methods = ["GET"])
def get_last_ad():
    node = utils.neo4j.get_last_ad()
    return jsonify({"node": node}), 200