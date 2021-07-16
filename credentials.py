

import ee
service_account = 'app-engine-default-service-acc@ee-globalchange-gee4geo.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './config/privatekey.json')
print(credentials)
ee.Initialize(credentials)