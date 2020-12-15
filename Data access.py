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
import plotly.graph_objs as go
from plotly.offline import plot

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
            #print(city_name + " in" + state_name)

            city_url = baseurl + city_path
            response2 = requests.get(city_url)
            soup2 = BeautifulSoup(response2.text, "html.parser")
            p_class = soup2.find(id = "mw-content-text")
            p_tag = p_class.find("p")
            text = p_tag.text
            city_cache_dict[city_name]["desc"] = text.replace("[1]", "")
            #print(text.replace("[1]", ""))
        save_cache(CITY_CHCHE_FILE, city_cache_dict)
        return city_cache_dict
    else:
        print("Using cache")
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

def make_request_with_cache(baseurl, city, recommend = "No"):
    headers = {'authorization':'Bearer '+ yelp_key}
    if(recommend == "No"):
        params = {
            "location": city,
            "categories": "chinese, All)",
            "limit": "50"
        }
    if(recommend == "yes"):
        params = {
            "location": city,
            "categories": "chinese, All)",
            "limit": "5",
            "sort by": "rating"
        }
    unique_key = construct_unique_key(baseurl, params)
    #print(unique_key)

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

def get_businesses_info_from_db(fields, params):
    conn = sqlite3.connect("FAPJ_DB.sqlite")
    cur = conn.cursor()
    total_fields = ""
    for i in fields:
        total_fields += "f.{}".format(i) + ", "
    total_fields = total_fields[:-2]
    command = '''SELECT {} FROM Businesses as f'''.format(total_fields)

    if (params != None):
        keys = list(params.keys())
        for key in keys:
            if keys.index(key) == 0:
                command += ' WHERE {}="{}"'.format(key, params[key])
            else:
                command += ' AND {}="{}"'.format(key, params[key])
    command += ";"
    #print(command)
    info = cur.execute(command).fetchall()
    conn.close()
    #print(info)
    return info

def get_ave_info(field, params):
    real_field = []
    data_list = []
    real_field.append(field)
    #print(params)
    info = get_businesses_info_from_db(real_field, params)
    for i in info:
        i = i[0]
        if(i == "$"):
            i = int(1)
        if(i == "$$"):
            i = int(2)
        if(i == "$$$"):
            i = int(3)
        if(i == "$$$$"):
            i = int(4)
        if(i == " "):
            i = int(1)
        data_list.append(int(i))
    ave = sum(data_list)/len(data_list)
    # print("****************************")
    # print("The average %s of the city %s is %s" % (field, params["cityname"], ave))
    return ave

#Drawing graphs
def bar_rating_price(params):
    ave_rating = []
    conn = sqlite3.connect("FAPJ_DB.sqlite")
    cur = conn.cursor()
    
    command_1 = """ SELECT rating FROM Businesses WHERE {} = "{}" AND price = "{}" """.format("cityname", params["cityname"], "$")
    command_2 = """ SELECT rating FROM Businesses WHERE {} = "{}" AND price = "{}" """.format("cityname", params["cityname"], "$$")
    command_3 = """ SELECT rating FROM Businesses WHERE {} = "{}" AND price = "{}" """.format("cityname", params["cityname"], "$$$")
    command_4 = """ SELECT rating FROM Businesses WHERE {} = "{}" AND price = "{}" """.format("cityname", params["cityname"], "$$$$")
    #print(command)
    rating = []
    rating.append([cur.execute(command_1).fetchall(), "$"])
    rating.append([cur.execute(command_2).fetchall(), "$$"])
    rating.append([cur.execute(command_3).fetchall(), "$$$"])
    rating.append([cur.execute(command_4).fetchall(), "$$$$"])
    
    for r in rating:
        params["price"] = r[1]
        try:
            ave = get_ave_info("rating", params)
            ave_rating.append([ave, r[1]])
        except:
            pass

    # print(rating)
    # print(ave_rating)

    data = go.Bar(
        x = [r[1] for r in rating],
        y = [a[0] for a in ave_rating]
    )

    layout = go.Layout(title = "Graph of rating with same price", width = 800)
    fig = go.Figure(data = data, layout = layout)
    fig.show()

def bar_cities_comparison(cities_by_user):
    cities_ave_rating = []
    cities_ave_price = []
    for c in cities_by_user:
        params = {}
        params["cityname"] = c
        ave_rating = get_ave_info("rating", params)
        ave_price = get_ave_info("price", params)
        cities_ave_rating.append(ave_rating)
        cities_ave_price.append(ave_price)

    trace1 = go.Bar(
        x = [c for c in cities_by_user],
        y = [r for r in cities_ave_rating],
        name = "rating"
    )

    trace2 = go.Scatter(
        x = [c for c in cities_by_user],
        y = [p for p in cities_ave_price],
        xaxis = "x",
        yaxis = "y2",
        name = "price"
    )

    data = [trace1, trace2]
    layout = go.Layout(
        yaxis2=dict(anchor='x', overlaying='y', side='right'), title = "Comparison between cities", width = 1000
    )

    fig = go.Figure(data = data, layout = layout)
    fig.show()

def build_recommend_table(params):
    city = params["cityname"]
    recommend = "yes"
    recommend_dict = make_request_with_cache(baseurl, city, recommend)
    list_of_recommend_instances = find_businesses_records_in_city(recommend_dict)
    name = []
    address = []
    for i in list_of_recommend_instances:
        name.append(i.name)
        address.append(i.address)
    layout=go.Layout(title = "Table of information for recommended restaurants")
    fig = go.Figure(data=[go.Table(header=dict(values=['name', 'address']),
                    cells=dict(values=[[n for n in name], [a for a in address]]))
                        ], layout = layout)
    fig.show()

def build_rating_pie(params):
    conn = sqlite3.connect("FAPJ_DB.sqlite")
    cur = conn.cursor()
    
    rating_list = [2.0, 2.5, 
    3.0, 3.5, 4.0, 4.5, 5.0]
    rating_percentage = []

    command = """ SELECT COUNT(*) FROM Businesses WHERE {} = "{}" """.format("cityname", params["cityname"])
    #print(command)
    total_number = cur.execute(command).fetchall()
    total_number = total_number[0][0]
    for i in rating_list:
        command = """ SELECT COUNT(*) FROM Businesses WHERE {} = "{}" AND rating = "{}" """.format("cityname", params["cityname"], i)
        num = cur.execute(command).fetchall()
        num = num[0][0]
        rating_percentage.append(num/total_number)

    trace = go.Pie(labels = rating_list, values = rating_percentage)
    data = [trace]
    layout = go.Layout(title = "Pie chart of percentage for different rating")
    fig = go.Figure(data = data, layout = layout)
    fig.show()

    conn.close()

#input regulation
def input_city_name(cities_list):
    while True:
        city_input = input("Please enter the number for your city: ")
        if(city_input == "exit"):
            exit()
        else:
            try:
                city_input = int(city_input)
                if(city_input not in range(1, 51)):
                    print("Invalid number, try again.")
                else:
                    break
            except:
                print("Invalid input, try again.")
    city = cities_list[city_input - 1]
    print(city + " in" + CITY_CACHE_DICT[city]["state"])
    print(CITY_CACHE_DICT[city]["desc"])
    return city

def input_choice():
    print("*"*20)
    print("1.The average rating and price for the Chinese restaurants in this city.")
    print("2.The best 5 Chinese restaurants for recommendation.")
    print("3.The rating percentage of Chinese restaurants in this city.")
    print("4.Make comparison betweem different cities you have chosen.")
    print("5.Choose/Add another city.")
    print("""Enter "exit" to end the program.""")
    print("*"*20)

    while True:
        choice = input("Please input your choice: ")
        if(choice == "exit"):
            exit()
        else:
            try:
                choice = int(choice)
                if(choice not in range(1, 6)):
                    print("Invalid number, try again.")
                else:
                    break
            except:
                print("Invalid input, try again.")
    return choice

if __name__ == "__main__":
    CITY_CACHE_DICT = built_city_dict()
    YELP_CACHE_DICT = load_cache(YELP_CACHE_FILE)
    Create_Cities_Table(CITY_CACHE_DICT)

    cities_list = list(CITY_CACHE_DICT.keys())
    for i in cities_list:
        print(cities_list.index(i) + 1, i, "in" + CITY_CACHE_DICT[i]["state"])

    cities_by_user = []
    while True:
        print("")
        city = input_city_name(cities_list)
        if(city not in cities_by_user):
            cities_by_user.append(city)
            Yelp_data_in_city = make_request_with_cache(baseurl, city)
            site_instance_list = find_businesses_records_in_city(Yelp_data_in_city)
            #print("create table!")
            Create_Businesses_Table(site_instance_list)

        choice = ""
        while choice != "exit":
            params = {"cityname": city}
            choice = input_choice()
            if(choice == 1):
                bar_rating_price(params)
            if(choice == 2):
                build_recommend_table(params)
            if(choice == 3):
                build_rating_pie(params)
            if(choice == 4):
                if(len(cities_by_user) == 1):
                    print("No other cities available. Please add another city or make other choices.")
                else:
                    print("""Now we have {} cities. Here are the comparison on rating and price between them:  """.format(len(cities_by_user)))
                    bar_cities_comparison(cities_by_user)
            if(choice == 5):
                break
    

