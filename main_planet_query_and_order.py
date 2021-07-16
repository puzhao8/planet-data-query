""" Reference """
# https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/data-api-tutorials/search_and_download_quickstart.ipynb

from easydict import EasyDict as edict
from prettyprinter import pprint
from utils.planet import query_planet, order_planet_to_gee


""" Configuration """
cfg = edict({
  # http://geojson.io/
  'roi': [[ 
            [
              -96.40336669921875,
              52.37432989187307
            ],
            [
              -95.9611669921875,
              52.37432989187307
            ],
            [
              -95.9611669921875,
              52.595111729383675
            ],
            [
              -96.40336669921875,
              52.595111729383675
            ],
            [
              -96.40336669921875,
              52.37432989187307
            ]
        ]],

  'start': "2021-06-28T00:00:00.000Z",
  'end': "2021-07-06T00:00:00.000Z",

  'cloud_level': 0.1,
  'item_type': "PSScene4Band",
  
  'gcp_project_id': "ee-globalchange-gee4geo"
})

image_ids = query_planet(cfg)

# filtering
sat_ids = ['2448', '2444', '2442',
           '241b', '241e', '2465']

image_ids_flt = [image_id for image_id in image_ids if image_id.split("_")[-1] in sat_ids]
print(len(image_ids_flt))
pprint(image_ids_flt)

cfg.update({'image_ids': image_ids_flt})

# order_planet_to_gee(cfg)




