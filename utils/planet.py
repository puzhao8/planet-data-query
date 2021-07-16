import os, time
import json
import requests
from requests.auth import HTTPBasicAuth
from prettyprinter import pprint

""" Authenticating """
planet_keyDict = {
    'puzhao': 'cc1f2979d2fd47f690f45128ad8272c0',
    'xikun':'f20e9dbcbccf4895a5290a5322300845'
}
os.environ['PL_API_KEY']=planet_keyDict['puzhao']

# API Key stored as an env variable
PLANET_API_KEY = os.getenv('PL_API_KEY')
auth = HTTPBasicAuth(PLANET_API_KEY, '')

# set content type to json
headers = {'content-type': 'application/json'}

query_url = 'https://api.planet.com/data/v1/quick-search'
orders_url = 'https://api.planet.com/compute/ops/orders/v2'


def query_planet(cfg):
  """ Define AOI """
  # Stockton, CA bounding box (created via geojson.io) 
  geojson_geometry = {
    "type": "Polygon",
    "coordinates": cfg.roi
  }

  """ Create Filters """
  # get images that overlap with our AOI 
  geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geojson_geometry
  }

  # get images acquired within a date range
  date_range_filter = {
    "type": "DateRangeFilter",
    "field_name": "acquired",
    "config": {
      "gte": cfg.start,
      "lte": cfg.end
    }
  }

  # only get images which have <50% cloud coverage
  cloud_cover_filter = {
    "type": "RangeFilter",
    "field_name": "cloud_cover",
    "config": {
      "lte": cfg.cloud_level
    }
  }

  # combine our geo, date, cloud filters
  combined_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_range_filter, cloud_cover_filter]
  }


  """ Searching: Items and Assets """
  item_type = cfg.item_type

  # API request object
  search_request = {
    "item_types": [item_type], 
    "filter": combined_filter
  }

  # fire off the POST request
  search_result = \
    requests.post(
      query_url,
      auth=HTTPBasicAuth(PLANET_API_KEY, ''),
      json=search_request)

  # print(json.dumps(search_result.json(), indent=1))


  # extract image IDs only
  image_ids = [feature['id'] for feature in search_result.json()['features']]

  print()
  print(f"total number of images: {len(image_ids)}")
  pprint(image_ids)

  return image_ids


# # Requests example
# auth = HTTPBasicAuth(PLANET_API_KEY, '')
# response = requests.get(orders_url, auth=auth)
# print(response)

# orders = response.json()['orders']
# print(len(orders))

""" Ordering """

def order_planet_to_gee(cfg):
    request = {  
      "name":"gcs_delivery_order",
      "products":[
          {  
            "item_ids": cfg.image_ids,
            "item_type": cfg.item_type, #"PSScene4Band",
            "product_bundle":"analytic"
          }
      ],

      "tools": [
        {
            "clip": {
              "aoi": {
                "type": "Polygon",
                "coordinates": cfg.roi
              }
            },
            # "file_format": {
            #   "format": "COG"
            # }
        }],

      "delivery": {
          "google_earth_engine":{
                "project": cfg.gcp_project_id, # "ee-globalchange-gee4geo"
                "collection": "Planet",
                # "path_prefix": ""
          }
        }
    }

    order_url = place_order(request, auth)
    print(order_url)

    return order_url


def place_order(request, auth):
    response = requests.post(orders_url, data=json.dumps(request), auth=auth, headers=headers)
    print(response.status_code)
    order_id = response.json()['id']
    print(order_id)
    order_url = orders_url + '/' + order_id
    return order_url

""" Check Order State """
def check_state(order_url):
    response = requests.get(order_url, auth=auth).json()['state']
    print(response)


""" Cancel an Order """
def cancel_order(order_url):
    response = requests.put(order_url, auth=auth)
    print(response)



""" Poll for Order Success """
# # re-order since we canceled our last order
# order_url = place_order(request, auth)

def poll_for_success(order_url, auth, num_loops=30):
    count = 0
    while(count < num_loops):
        count += 1
        r = requests.get(order_url, auth=auth)
        response = r.json()
        state = response['state']
        print(state)
        end_states = ['success', 'failed', 'partial']
        if state in end_states:
            break
        time.sleep(10)
        
# poll_for_success(order_url, auth)