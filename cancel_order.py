
import requests
from requests.auth import HTTPBasicAuth
from utils.planet import PLANET_API_KEY

auth = HTTPBasicAuth(PLANET_API_KEY, '')

order_url = "https://api.planet.com/compute/ops/orders/v2/d26de392-91fd-4c5f-987e-b5c16c3d9a59"
response = requests.put(order_url, auth=auth)
print(response)