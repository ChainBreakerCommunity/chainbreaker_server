from server import app, db
import folium
from models import Ad
from flask import jsonify, render_template
from utils import get_size

@app.route("/api/map/get_locations_map", methods = ["GET"])
def get_locations_map():
    #Great Folium Tutorial https://www.youtube.com/watch?v=t9Ed5QyO7qY
    start_coords = (4.581440, -73.397964)
    folium_map = folium.Map(location=start_coords, zoom_start=3)

    zoom_filter = 0
    ads = db.session.query(Ad) \
        .filter(Ad.zoom >= zoom_filter) \
        .all()

    from random import shuffle
    data = list()
    shuffle(ads)
    counter = 0
    for ad in ads: 
        counter += 1
        data.append([ad.latitude, ad.longitude])
        """
        popup = "Ad Id: " + str(ad.id_ad) + ". Location: " + ad.city + " "
        if ad.place != None:
            popup += ad.place
        folium.Marker(
            [ad.latitude, ad.longitude], 
            popup = popup
        ).add_to(folium_map)
        if counter >= app.config["MAX_ADS_PER_REQUEST"]:
            break
        """
    #folium.PolyLine(data, weight = 1, color = "blue", opacity = 0.6).add_to(folium_map)
    from folium.plugins import HeatMap, Draw
    draw = Draw(export = True)
    draw.add_to(folium_map)
    HeatMap(data).add_to(folium.FeatureGroup(name="Heat Map")).add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    print("Request memory size: ", get_size(folium_map), " bytes.")
    #folium_map._repr_html_()
    folium_map.save(outfile = "folium_map.html")
    return jsonify({"message": "ok"})

@app.route("/api/map/template")
def template():
    return render_template("folium_map.html")