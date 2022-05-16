import time
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import json 
import re 
import sys

import logging
#logging.basicConfig(filename='geolocation.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

with open("config.json") as json_file: 
    data = json.load(json_file)

SELENIUM_ENDPOINT = data["selenium_endpoint"]
SECONDS_SLEEP = 1.5
LOCATIONS_FILE = "./geolocations/"
        
def search_place(driver_geo, keys):
    query_input = driver_geo.find_element_by_xpath("""//*[@id="searchboxinput"]""")
    query_input.clear()
    query_input.send_keys(keys)
    time.sleep(SECONDS_SLEEP)
    search_button = driver_geo.find_element_by_xpath("""//*[@id="searchbox-searchbutton"]""")
    search_button.click()
    time.sleep(SECONDS_SLEEP + 2)
    
    try:
        m1 = re.search("!3d(.+?)?hl", driver_geo.current_url)
        result1 = m1.group(0).replace("!3d", "").replace("!4d", ",").replace("?hl", "").split(",")

        m2 = re.search("@(.+?)z", driver_geo.current_url)
        result2 = m2.group(0)[1:].split(",")

        #print(result1)
        #print(result2)

        time.sleep(SECONDS_SLEEP)
        driver_geo.get("https://www.google.com/maps/?hl=es")

        return [float(result1[0]), float(result1[1]), int(result2[2][0:-1])]
    except:
        m2 = re.search("@(.+?)z", driver_geo.current_url)
        result2 = m2.group(0)[1:].split(",")

        #print(result1)
        #print(result2)

        time.sleep(SECONDS_SLEEP)
        driver_geo.get("https://www.google.com/maps/?hl=es")

        return [float(result2[0]), float(result2[1]), int(result2[2][0:-1])]
    
def location_to_array(location):
    location = location.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").replace("z", "").split(",")
    for i in range(len(location) - 1):
        location[i] = float(location[i])
    location[2] = int(location[2])
    return location

def get_location_name(country, region, city, place):
    """
    Get location name.
    """
    if region == "bogota" and place != None: 
        location_name = country + "," + region + "," + place
    elif region == "bogota" and place == None:
        location_name = country + "," + region
    elif region != "bogota" and place == None:
        location_name = country + "," + region + "," + city
    else: 
        if city != None:
            if place == None:
                location_name = country + "," + region + "," + city
            else:
                location_name = country + "," + region + "," + city + "," + place
        else: 
            location_name = country + "," + region
    return location_name

def location_to_array(location):
    """
    Location to array.
    """
    location = location.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").replace("z", "").split(",")
    for i in range(len(location) - 1):
        location[i] = float(location[i])
    location[2] = int(location[2])
    return location

def get_geolocation(country: str, region: str, city: str, place: str):
    with open(LOCATIONS_FILE + country.lower() + "_geolocations.json", "r") as json_file: 
        hash_map = json.load(json_file)

    request_info = "Request information: " + " Country: " + country + ", Region: " + region 
    if city != None:
        request_info = request_info + ", City: " + city
        if place != None:
            request_info = request_info + ", Place: " + place

    logging.warning(request_info)
    print(request_info)
    sys.stdout.flush()

    location_name = get_location_name(country, region, city, place)
    logging.warning("Location to search: ", location_name)
    print("Location to search: ", location_name)
    sys.stdout.flush()

    # Search in hashmap.
    if location_name in list(hash_map.keys()):
        # Get location in dictionary.
        logging.warning("Location found in dictionary!")
        print("Location found in dictionary!")
        sys.stdout.flush()
        gps_location = location_to_array(hash_map[location_name])
        
    else: 

        driver_geo = webdriver.Remote(SELENIUM_ENDPOINT, desired_capabilities = DesiredCapabilities.FIREFOX)
        #driver = webdriver.Chrome(executable_path="chromedriver.exe")
        driver_geo.get("https://www.google.com/maps/?hl=es")
        driver_geo.save_screenshot("screenshot.png")
        
        # Get Google Maps location.
        gps_location = search_place(driver_geo, location_name)
        fields = [location_name, str(gps_location[0]) + "," + str(gps_location[1]) + "," + str(gps_location[2]) + "z"]
        driver_geo.quit()

        # Add a new location.
        logging.warning("Save new location in map.")
        print("Save new location in map.")
        sys.stdout.flush()
        
        hash_map[fields[0]] = fields[1]
        a_file = open(LOCATIONS_FILE + country.lower() + "_geolocations.json", "w")
        json.dump(hash_map, a_file)
        a_file.close()
        time.sleep(SECONDS_SLEEP)

    latitude = gps_location[0]
    longitude = gps_location[1]
    zoom = gps_location[2]
    return latitude, longitude, zoom
