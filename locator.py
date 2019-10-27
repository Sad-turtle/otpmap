import datetime
import json
from tornado.web import RequestHandler
import motor.motor_tornado

from pending import store_pending_visitor
from ranking import calculate_atm_ranking

client = motor.motor_tornado.MotorClient()
db = client['otpmap']

class ATMLocatorService(RequestHandler):
    collection = db['atms']
    
    def set_default_headers(self):
        # For prototyping
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    async def get(self, uuid):
        longitude = float(self.get_argument("longitude", 19.089563, True))
        latitude = float(self.get_argument("latitude", 47.451316, True))
        point = [longitude, latitude]
        print('Current location is: ', point)

        atms = await self.get_atms_in_radius(point, 3000)
        data = await calculate_atm_ranking(point, atms)

        self.write(json.dumps({'type': 'atmlist', 'data': data}))

        if data:
            await store_pending_visitor(uuid, data[0]['_id'], datetime.datetime.now(), data[0]['time_approx'])

    async def get_atms_in_radius(self, client_location, radius):
        cursor = self.collection.find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': "Point" ,
                        'coordinates': client_location
                    },
                    '$maxDistance': radius
                }
            }
        })
        
        atms = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            atms.append(document)
            
        return atms
