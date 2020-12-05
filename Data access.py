#########################################
##### Name:Fenghe Fu                #####
##### Uniqname:fufenghe             #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
# JM EDITED LINE
import secret # file that contains your OAuth credentials
from bs4 import BeautifulSoup
import sqlite3

yelp_key = secret.YELP_KEY
baseurl = "https://api.yelp.com/v3/businesses/search"

CITY_CHCHE_FILE = "city_cache.json"
CITY_CACHE_DICT = {}
YELP_CACHE_FILE = "yelp_cache.json"
YELP_CACHE_DICT = {}

def load_cache(filename):
    try:
        cache_file = open(filename, "r")
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(filename, cache_dict):
    cache_file = open(filename, "w")
    cache_file_contents = json.dumps(cache_dict)
    cache_file.write(cache_file_contents)
    cache_file.close()

#Cities Crawling
def built_city_dict():
    CITY_CACHE_DICT = load_cache(CITY_CHCHE_FILE)
    if(len(CITY_CACHE_DICT) == 0):
        city_cache_dict = {}
        print("fetching")
        baseurl = "https://ballotpedia.org"
        base_url = "https://ballotpedia.org/Largest_cities_in_the_United_States_by_population"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find(class_ = "marqueetable")
        tr_list = table.find_all("tr")
        for tr in tr_list[2:52]:
            td_list = tr.find_all("td")
            city_path_tag = td_list[1].find("a")
            city_path = city_path_tag["href"]
            city_name_string = td_list[1].text.strip()
            comma_position = city_name_string.find(",")
            city_name = city_name_string[0:comma_position]
            state_name = city_name_string[comma_position+1:]
            city_cache_dict[city_name] = {}
            city_cache_dict[city_name]["state"] = state_name
            print(city_name + " in" + state_name)

            city_url = baseurl + city_path
            response2 = requests.get(city_url)
            soup2 = BeautifulSoup(response2.text, "html.parser")
            p_class = soup2.find(id = "mw-content-text")
            p_tag = p_class.find("p")
            text = p_tag.text
            city_cache_dict[city_name]["desc"] = text.replace("[1]", "")
            print(text.replace("[1]", ""))
        save_cache(CITY_CHCHE_FILE, city_cache_dict)
        return city_cache_dict
    else:
        print("Using cache")
        for city in CITY_CACHE_DICT.keys():
            print(city + " in" + CITY_CACHE_DICT[city]["state"])
            print(CITY_CACHE_DICT[city]["desc"])
        return CITY_CACHE_DICT

###Yelp API
def construct_unique_key(baseurl, params):
    params_str = []
    connector = "_"

    for key in params.keys():
        params_str.append(f"{key}_{params[key]}")
    params_str.sort()
    return baseurl + connector + connector.join(params_str)

def make_request(baseurl, params, headers):
    response = requests.get(baseurl, params = params, headers = headers)
    content = response.json()
    return content

def make_request_with_cache(baseurl, city):
    headers = {'authorization':'Bearer '+ yelp_key}
    params = {
        "location": city,
        "categories": "chinese, All)",
        "limit": "10"
    }
    unique_key = construct_unique_key(baseurl, params)
    print(unique_key)

    if unique_key in YELP_CACHE_DICT.keys():
        print("fetching cached data")
        return YELP_CACHE_DICT[unique_key]
    else:
        print("making new request")
        YELP_CACHE_DICT[unique_key] = make_request(baseurl, params, headers)
        #print(len(CACHE_DICT[unique_key]["statuses"]))
        save_cache(YELP_CACHE_FILE, YELP_CACHE_DICT)
        return YELP_CACHE_DICT[unique_key]

class Bussiness:
    def __init__(self, name = None, city = None,  
                 address = None, longitude = None, latitude = None,
                 review_count = None, rating = None, price = None):
        self.name = name
        self.city = city
        self.address = address
        self.longitude = longitude
        self.latitude = latitude
        self.review_count = review_count
        self.rating = rating
        self.price = price

    def info(self):
        return self.name + " (" + self.city + ")" + ": " + self.rating + " " + self.price

def try_query(dic, key):
    try:
        value = dic[key]
        return value
    except:
        return " "

def find_businesses_records_in_city(Yelp_Data):
    site_instance_list = []

    info_of_businesses = Yelp_Data["businesses"]
    for i in info_of_businesses:
        name = try_query(i, "name")
        location = try_query(i, "location")
        city = try_query(location, "city")
        address = try_query(location, "address1")
        coordinates = try_query(i, "coordinates")
        longitude = try_query(coordinates, "longitude")
        latitude = try_query(coordinates, "latitude")
        review_count = try_query(i, "review_count")
        rating = try_query(i, "rating")
        price = try_query(i, "price")

        site_intance = Bussiness(name, city,  
                                address, longitude, latitude,
                                review_count, rating, price)
        site_instance_list.append(site_intance)
    return site_instance_list

#Create Database
def Create_Cities_Table(city_cache_dict):
    try:   
        Create_Cities_Table = '''
            CREATE TABLE IF NOT EXISTS "Cities" (
                "city"	TEXT NOT NULL,
                "state"	TEXT NOT NULL,
                "description"	TEXT NOT NULL,
                PRIMARY KEY("city")
                );
    '''
        conn = sqlite3.connect("FAPJ_DB.sqlite")
        cur = conn.cursor()
        cur.execute(Create_Cities_Table)
        add_city = "INSERT INTO Cities VALUES (?, ?, ?)"

        for city in city_cache_dict:
            cur.execute(add_city, (city, city_cache_dict[city]["state"], 
                                city_cache_dict[city]["desc"])
                                )
        conn.commit()
    except:
        return None

def Create_Businesses_Table(site_instance_list):
    Create_Businesses_Table = '''
    CREATE TABLE IF NOT EXISTS "Businesses" (
	    "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	    "name"	TEXT NOT NULL,
	    "cityname"	TEXT NOT NULL,
	    "address"	TEXT,
	    "longitude"	REAL NOT NULL,
	    "latitude"	REAL NOT NULL,
	    "review count"	INTEGER,
	    "rating"	REAL,
	    "price"	TEXT,
        FOREIGN KEY (cityname) REFERENCES Cities (city)
        );
'''
    conn = sqlite3.connect("FAPJ_DB.sqlite")
    cur = conn.cursor()
    cur.execute(Create_Businesses_Table)
    add_city = "INSERT INTO Businesses VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"

    for bussiness in site_instance_list:
        cur.execute(add_city, (bussiness.name, bussiness.city, bussiness.address,
        bussiness.longitude, bussiness.latitude, bussiness.review_count,
        bussiness.rating, bussiness.price)
                               )
    conn.commit()

# Create_Cities_Table = '''
#     CREATE TABLE IF NOT EXISTS "Cities" (
# 	    "city"	TEXT NOT NULL,
# 	    "state"	TEXT NOT NULL,
# 	    "description"	TEXT NOT NULL,
# 	    PRIMARY KEY("city")
#         );
# '''


#main

CITY_CACHE_DICT = built_city_dict()
YELP_CACHE_DICT = load_cache(YELP_CACHE_FILE)
Yelp_data_in_city = make_request_with_cache(baseurl, "Tulsa")
site_instance_list = find_businesses_records_in_city(Yelp_data_in_city)
for i in site_instance_list:
    print(i.name)

Create_Cities_Table(CITY_CACHE_DICT)
Create_Businesses_Table(site_instance_list)


