import json
import math
from tornado.web import RequestHandler
import motor.motor_tornado
import geopy.distance
import datetime

client = motor.motor_tornado.MotorClient('mongodb://localhost:27017')
db = client['otpmap']
collection = db['withdrawal_codes']

class WithdrawalQRCodeService(RequestHandler):    
    def set_default_headers(self):
        # For prototyping
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    async def get(self, uuid):
        amount = float(self.get_argument("amount", 0, True))
        atm_id = float(self.get_argument("atm_id", 0, True))
        
        await clear_pending_withdrawal_codes(uuid)

        data = await self.generate_withdrawal_code(uuid, atm_id, amount)
        self.write(json.dumps({'type': 'qrcode', 'data': data}))

async def clear_pending_withdrawal_codes(uuid):
    collection.delete_many({"uuid": uuid})

async def generate_withdrawal_code(uuid, atm_id, amount):
    qr_code = {'uuid': uuid, 'amount': amount, 'atm_id': atm_id}
    result = await collection.insert_one(qr_code)
    qr_code['_id'] = str(result.inserted_it)
    return qr_code
