import json
import math
from tornado.web import RequestHandler
import motor.motor_tornado
import geopy.distance
import datetime

client = motor.motor_tornado.MotorClient('mongodb://localhost:27017')
db = client['otpmap']
collection = db['pending_visitors']

async def store_pending_visitor(uuid, atm_id, time_now, approx_time_minutes):
    await clear_outgoing_pending_visitor_entry(uuid)
    
    expiration_time = datetime.datetime.timestamp(time_now) + approx_time_minutes * 60 * 1000
    pending_visitor = {"uuid": uuid, "atm_id": atm_id, "expiration_time": expiration_time}
    result = await collection.insert_one(pending_visitor)
    pending_visitor['_id'] = str(result.inserted_it)
    
async def pending_visitor_count(uuid, atm_id, target_time):
    expiration_time = datetime.datetime.timestamp(target_time)
    count = await collection.count({"atm_id": atm_id, "expiration_time": {"$gt": expiration_time}})
    return count

async def clear_outgoing_pending_visitor_entry(uuid):
    collection.delete_many({"uuid": uuid})
