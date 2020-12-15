## SI 507 Final Project

This program allows users to get information and data of the Chinese restaurants from 1 of 50 biggest American cities provided by the program. Users are able to view the data presented by various ways.

### Data Sources:

1. The 50 largest cities in America, which provides the cities choices for the users.
   https://ballotpedia.org/Largest_cities_in_the_United_States_by_population

2. Information such as ratings, locations and open times of restaurants could be obtained from Yelp Fusion: https://www.yelp.com/developers/documentation/v3 In order to get the API key, we need firstly create app from https://www.yelp.com/developers/v3/manage_app



### Program Structure:

This program uses Web API , json, requests, crawling, sqlite3, BeautifulSoup, and plotly. Here are the basic descriptions of the main functions and class.

##### Data accessing:

(1) *built_city_dict()*: Crawling the biggest 50 cities and their states and descriptions from the website and make a dictionary (city_cache_dict) to store them.

(2) *make_request_with_cache(baseurl, city, recommend = "No")*: Making request through Yelp API. The "recommend" part is related to how to use the function based on different goals. Then it will return a dictionary to store the API info.

(3) *class Bussiness*: class to store the basic information (name, cityname, address......) of a business

(4) *find_businesses_records_in_city(Yelp_Data)*: This function take the return value of function(2) as input. Then it will return a list of instances of the businesses in a certain city.

##### Database management:

(5) *Create_Cities_Table(city_cache_dict)*: It will create a database from city_cache_dict.

(6) *Create_Businesses_Table(site_instance_list)*: It will create a database from a instances list from function (4). The database will contain basic information from the businesses in that list.

(7) *get_businesses_info_from_db(fields, params)*: This function will obtain information described by "fields" and "params". "fields" is a list that indicates the type of the proposed information. "params" is a dictionary that contains the conditions used for "WHERE" and "AND" in this function to screen the information. 

(8) *get_ave_info(field, params)*: The "params" is still like those in function(7), but "field" is a string that is the data type for average calculation.

##### Drawing graphs:

(9) *bar_rating_price(params)*: "params" is still a dictionary but only contains the selected city. This function will return a bar chart showing the average rating in the same price in the selected city. 

(10) *build_recommend_table(params)*: "params" is same as above. This function will return a table showing 5 best recommended restaurants in the selected city. 

(11) *build_rating_pie(params)*: "params" is same as above. This function will return a pie chart showing the percentage of the ratings in the selected city. 

(12) *bar_cities_comparison(cities_by_user)*: "cities_by_user" is the list of cities selected by the user in the interface. This function will return a bar chart showing the average rating and price of each city in the list. 



### Interface Description:

in this program, firstly a list of 50 cities ranked by population is provided to the user. The user is able to choose one based on the index of the city in the list. Then the program will show which state does the city belong to and its brief description. The choice of city can be done multiple times and depends on the user. Once a city was chosen, it will be added into a list named “cities_by_user”.

Afterwards, the user has 5 choices for data presentation. The first one allows user to view a bar chart that shows average rating and price for the Chinese restaurants in this city. The second choice gives recommendation of the best 5 Chinese restaurants in this city as a table. The third choice shows a pie chart about the percentage of rating scores of the restaurants in that city. The fourth choice makes comparison about the average rating and price between cities the user has chosen in this program. The fifth choice let the user to choose or add another city, and it actually adds a new city into the “cities_by_user” list for the comparison part in fourth choice.

All of the graphs are presented using Plotly.



## User Guide

1. Install the package:

   ```python
   $ pip install -r requirements.txt 
   ```

2. Run the program

   ```python
   Python Data\ access.py 
   ```

   