import json
import math
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
import motor.motor_tornado
import geopy.distance
import datetime

client = motor.motor_tornado.MotorClient('mongodb://localhost:27017')
db = client['otpmap']
collection = db['pending_visitors']

class ConfirmATMSelectionService(RequestHandler):    
    def set_default_headers(self):
        # For prototyping
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    async def get(self, uuid):
        suggestion_id = self.get_argument("suggestion_id", 0, True)
        await confirm_pending_visitor(suggestion_id)
        # It is not important for the client whether this fails or not
        self.write(json.dumps({'type': 'status', 'data': 'OK'}))

async def store_pending_visitor(uuid, atm_id, time_now, approx_time_minutes):
    await clear_outgoing_pending_visitor_entry(uuid)
    
    expiration_time = datetime.datetime.timestamp(time_now) + approx_time_minutes * 60 * 1000
    pending_visitor = {"uuid": uuid, "atm_id": atm_id, "expiration_time": expiration_time, "active": False}
    result = await collection.insert_one(pending_visitor)
    pending_visitor['_id'] = str(result.inserted_it)
    
async def confirm_pending_visitor(uuid, suggestion_id):
    await collection.update_one({'_id': suggestion_id}, {'$set': {'active': 'True'}})

async def pending_visitor_count(uuid, atm_id, target_time):
    expiration_time = datetime.datetime.timestamp(target_time)
    count = await collection.count({"atm_id": atm_id, "expiration_time": {"$gt": expiration_time}, "active": True})
    return count

async def clear_outgoing_pending_visitor_entry(uuid):
    await collection.delete_many({"uuid": uuid})

async def pending_visitor_cleanup():
    current_time = datetime.datetime.timestamp(datetime.datetime.now())
    await collection.delete_many({"expiration_time": {"$lt": current_time}})

cleanup_period = 600

def schedule_pending_visitor_cleanup(ioloop):
    ioloop.call_later(cleanup_period, pending_visitor_cleanup)
