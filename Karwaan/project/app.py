# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import re, math
from collections import Counter
from googlemaps import convert
from googlemaps import Client
from googlemaps.convert import as_list

WORD = re.compile(r'\w+')

#applying cosine similarity for finding similarities between user interests and places
def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])
     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)
     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)

#remove spaces from the category column of dataset
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

#calulating weighted rating of places
def rcmd(text_1,src):
    
    
    metadata = pd.read_csv('merged-1.csv', low_memory=False)
    #print(metadata.head())
    #print("Select your preferred category:\n1.wildlife\n2.ancient\n3.religious\n4.nature\n5.adventure\n6.beaches\n7.mountain")
    #text1 = input("Enter User Interests: ").lower()
    #text1= 'wildlife'
    vector1 = text_to_vector(text_1)
    print(vector1)
    C = metadata['Overall rating'].mean()
    m = metadata['count'].quantile(0.75)
    
    def weighted_rating(x, m=m, C=C):
        v = x['count']
        R = x['Overall rating']
        # Calculation based on the Bayesian Rating Formula
        return (v/(v+m) * R) + (m/(m+v) * C)
    
    metadata['category'] = metadata['category'].apply(clean_data)
    metadata['score'] = metadata.apply(weighted_rating, axis=1)
    #print(metadata.head())
    cos=[]
    for i in list(metadata['category']):
        #print(type(i))
        text2 = i
        vector2 = text_to_vector(text2)
        cosine = get_cosine(vector1, vector2)
        cos.append(cosine)
    metadata['cosine']=cos
    x=metadata['cosine']>0.0
    rec=pd.DataFrame(metadata[x])
    rec=rec.sort_values('score',ascending=False)
    #src = 'mumbai'
    #src=input("Enter your location: ")
    dest=list(rec['title'])
    #print(type(dest))
    
    
    
    def distance_matrix(client,origins, destinations,
                        mode=None, language=None, avoid=None, units=None,
                        departure_time=None, arrival_time=None, transit_mode=None,
                        transit_routing_preference=None, traffic_model=None, region=None):
    
        params = {
            "origins": convert.location_list(origins),
            "destinations": convert.location_list(destinations)
        }
    
        if mode:
            # NOTE(broady): the mode parameter is not validated by the Maps API
            # server. Check here to prevent silent failures.
            if mode not in ["driving", "walking", "bicycling", "transit"]:
                raise ValueError("Invalid travel mode.")
            params["mode"] = mode
    
        if language:
            params["language"] = language
    
        if avoid:
            if avoid not in ["tolls", "highways", "ferries"]:
                raise ValueError("Invalid route restriction.")
            params["avoid"] = avoid
    
        if units:
            params["units"] = units
    
        if departure_time:
            params["departure_time"] = convert.time(departure_time)
    
        if arrival_time:
            params["arrival_time"] = convert.time(arrival_time)
    
        if departure_time and arrival_time:
            raise ValueError("Should not specify both departure_time and"
                             "arrival_time.")
    
        if transit_mode:
            params["transit_mode"] = convert.join_list("|", transit_mode)
    
        if transit_routing_preference:
            params["transit_routing_preference"] = transit_routing_preference
    
        if traffic_model:
            params["traffic_model"] = traffic_model
    
        if region:
            params["region"] = region
        #print(client._request("/maps/api/distancematrix/json", params))
        return client._request("/maps/api/distancematrix/json", params)
    
    client = Client(key='AIzaSyBnNfxEnrUv-5K57KJ22rfA1mhKnpIi3Yg')
    dist=[]
    dur=[]
    for d in dest:
        d=d
        # print(d)
        output=distance_matrix(client,src,d)
        # print(output)
        # print(type(output['rows'][0]['elements'][0]['status']))
        if output['destination_addresses']==['']:
            break
        if output['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
            a1='99999 km'
            a2='999'
        else:
            a1=(output['rows'][0]['elements'][0]['distance']['text'])
            a2=(output['rows'][0]['elements'][0]['duration']['text'])
        na1 = re.sub('\D', '', a1)
        
    
        dist.append(int(na1))
        dur.append(a2)
    #print(type(dist))
    rec['distance']=dist
    rec['duration']=dur
    
    final=pd.DataFrame(rec,index=None,columns=['title','State','score','distance','duration'])
    indexnames = final[ (final['distance'] >= 2000)].index
    final.drop(indexnames, inplace=True)
    return(final.head(5))

app = Flask(__name__)
from flask import Response, jsonify, make_response
import logging
@app.route("/")
def home():
    #logging.getLogger().setLevel(logging.DEBUG)
    #app.logger.info("sss")
    #return "hello world"
    return render_template('home.html')

@app.route("/recommend")
#@app.route("/city/<city>/interest/<interest>")
#def recommend(city:str, interest:str):
def recommend():
    interest = request.args.get('interest')
    city= request.args.get('city')
    logging.getLogger().setLevel(logging.DEBUG)
    a=rcmd(interest,city)
    #html = a.to_html()
    #print(html)
    html_string_start = '''<!DOCTYPE html>
    <html>
  <head><title>Recommended places</title></head>
  <link rel="stylesheet" type="text/css" href="mystyle.css"/>
   <style>body {
	background: linear-gradient(-45deg, #120920, #06222A, #23262F, #49091A);
	background-size: 400% 400%;
	-webkit-animation: gradient 15s ease infinite;
	        animation: gradient 15s ease infinite;
					font-family: 'Open Sans', sans-serif;
				  font-weight: 300;
				  line-height: 1.42em;
}

@-webkit-keyframes gradient {
	0% {
		background-position: 0% 50%;
	}
	50% {
		background-position: 100% 50%;
	}
	100% {
		background-position: 0% 50%;
	}
}

@keyframes gradient {
	0% {
		background-position: 0% 50%;
	}
	50% {
		background-position: 100% 50%;
	}
	100% {
		background-position: 0% 50%;
	}

}


h1 {
  font-size:3em;
  font-weight: 300;
  line-height:1em;
  text-align: center;
  color: #4DC3FA;
}

h2 {
	padding-left: 200px;
	padding-right: 200px;
	padding-top:  50px;
  font-size:1.5em;
  font-weight: 300;
  text-align: center;
  display: block;
  line-height:1em;
  padding-bottom: 2em;
  color: #ffffff;
}

h2 a {
  font-weight: 700;
  text-transform: uppercase;
  color: #FB667A;
  text-decoration: none;
}

.blue { color: #185875; }
.yellow { color: #FFF842; }




.center {

  width: 180px;
  height: 60px;
  position: absolute;
}

.btn {
  width: 180px;
  height: 60px;
  cursor: pointer;
  background: transparent;
  border: 1px solid #91C9FF;
  outline: none;
  transition: 1s ease-in-out;
	color: White;
	font-weight: bold;
}

svg {
  position: absolute;
  left: 0;
  top: 0;
  fill: none;
  stroke: #fff;
  stroke-dasharray: 150 480;
  stroke-dashoffset: 150;
  transition: 1s ease-in-out;
}

.btn:hover {
  transition: 0.5s ease-in-out;
  background: #FFF842;
	color: black;
}

.btn:hover svg {
  stroke-dashoffset: -480;
}

.btn span {
  color: white;
  font-size: 18px;
  font-weight: 100;
}


.container th h1 {
	  font-weight: bold;
	  font-size: 1em;
  text-align: left;
  color: #ffffff;
}

.container td {
	  font-weight: normal;
	  font-size: 1em;
  -webkit-box-shadow: 0 2px 2px -2px #0E1119;
	   -moz-box-shadow: 0 2px 2px -2px #0E1119;
	        box-shadow: 0 2px 2px -2px #0E1119;
					color: #ffffff;
}



.container {
	  text-align: left;
	  overflow: hidden;
	  width: 80%;
	  margin: 0 auto;
  display: table;
  padding: 0 0 8em 0;
}

.container td, .container th {

	  padding-bottom: 2%;
	  padding-top: 2%;
  padding-left:1%;
}

/* Background-color of the odd rows */
.container tr:nth-child(odd) {
	  background-color: #323C50;
}

/* Background-color of the even rows */
.container tr:nth-child(even) {
	  background-color: #2C3446;
}

.container th {
	  background-color: #1F2739;
}


.container tr:hover {
   background-color: #464A52;
-webkit-box-shadow: 0 6px 6px -6px #0E1119;
	   -moz-box-shadow: 0 6px 6px -6px #0E1119;
	        box-shadow: 0 6px 6px -6px #0E1119;
}

.container td:hover {
  background-color: #FFF842;
  color: #403E10;
  font-weight: bold;

  box-shadow: #7F7C21 -1px 1px, #7F7C21 -2px 2px, #7F7C21 -3px 3px, #7F7C21 -4px 4px, #7F7C21 -5px 5px, #7F7C21 -6px 6px;
  transform: translate3d(6px, -6px, 0);

  transition-delay: 0s;
	  transition-duration: 0.4s;
	  transition-property: all;
  transition-timing-function: line;
}

@media (max-width: 800px) {
.container td:nth-child(4),
.container th:nth-child(4) { display: none; }
}

   </style><body> 
  <div >
    
      <h2 >Here are some more like this</h2>
      
   '''
    html_string_end = '''
    </div></body>
   </html>
   '''

    with open(r'templates\abc.html', 'w') as f:
        f.write(html_string_start)
        f.write('<table class="container">')
        for header in a.columns.values:
            f.write('<th>'+str(header)+'</th>')
        for i in range(len(a)):
            f.write('<tr>')
            for col in a.columns:
                value = a.iloc[i][col]    
                f.write('<td>'+str(value)+'</td>')
            f.write('</tr>')
        f.write('</table>')
        f.write(html_string_end)
    return render_template("abc.html",interest=interest,city=city)
        #if type(a)==type('string'):
         #   return render_template('abc.html',interest=interest,city=city,a=a,t='s')
        #else:
          #  return render_template('abc.html',interest=interest,city=city,a=a,t='l')
        #response = make_response(jsonify(a.to_dict()),200)
        #app.logger.error(a)
       # return response
    


if __name__ == '__main__':
    #app.debug = True
    app.run(debug=True, FLASK_ENV=development)
