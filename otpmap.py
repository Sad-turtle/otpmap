import tornado.ioloop
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

import pyrestful.rest
from pyrestful.rest import get,post
import motor.motor_tornado

import json

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
        #point = [19.089563, 47.451316] # longitude, latitude
        
        longitude = float(self.get_argument("longitude", 19.089563, True))
        latitude = float(self.get_argument("latitude", 47.451316, True))
        
        point = [longitude, latitude]
        #point = [19.0579744, 47.4859617]
        print(point)
        
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
        data = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            data.append(document)
        print([data['location'] for data in data])

        self.write(json.dumps({'type': 'atmlist', 'data': data}))
    
def make_app():
  urls = [("/atms/([^/]+)/", ATMLocatorService)]
  return Application(urls)

if __name__ == '__main__':
    try:
        app = make_app()
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(8080)
        print("Listening on 0.0.0.0:8080")
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("\nExiting")
