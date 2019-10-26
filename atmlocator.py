import json
from tornado.web import RequestHandler
import motor.motor_tornado

client = motor.motor_tornado.MotorClient('mongodb://localhost:27017')
db = client['otpmap']

class ATMLocatorService(RequestHandler):
    def set_default_headers(self):
        # For prototyping
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    async def get(self, uuid):
        details=self.get_argument("details", None, True)
        collection = db['atms']
        
        longitude = float(self.get_argument("longitude", 19.089563, True))
        latitude = float(self.get_argument("latitude", 47.451316, True))
        
        point = [longitude, latitude]
        print('Current location is: ', point)
        
        cursor = db['atms'].find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': "Point" ,
                        'coordinates': point
                    },
                    '$maxDistance': 5000
                }
            }
        })
        atms = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            atms.append(document)
        
        data = self.calculate_atm_ranking(atms)
        
        self.write(json.dumps({'type': 'atmlist', 'data': data}))

    def calculate_atm_ranking(self, atms):
        pass
