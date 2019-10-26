import csv
import asyncio
import motor.motor_asyncio
import pymongo

reader = csv.DictReader(open('atm_201909_IX_eng.csv'))
atms = {}

for row in reader:
    key = '{}_{}'.format(row['GEO_X'], row['GEO_Y'])
    
    if key not in atms:
        geo_x = float(row['GEO_X'].replace(',', '.'))
        geo_y = float(row['GEO_Y'].replace(',', '.'))
        atms[key] = {
            'location': { 'type': 'Point', 'coordinates': [ geo_y, geo_x ] },
            'zip_code': row['ZIP_CD'],
            'city': row['CITY'],
            'deposit': row['ATM_DEPOSIT_FL'] == 'Y',
            'cash_remain': 1000000,
            'stats': {}
        }
    atm = atms[key]
    day = row['TRX_DAY'].lower()
    atm['stats']['day'] = {}
    
    for hour in range(0, 23):
        period_1 = 'TRAN_CNT_{:02}00_{:02}30'.format(hour, hour)
        period_2 = 'TRAN_CNT_{:02}30_{:02}00'.format(hour, hour + 1)
        
        stat_1 = {'minutes_start': 0, 'minutes_end': 30, 'value': row[period_1]}
        stat_2 = {'minutes_start': 30, 'minutes_end': 60, 'value': row[period_2]}
        
        atm['stats']['day']['{:02}'.format(hour)] = [stat_1, stat_2]

atms = list(sorted(atms.values(), key=lambda x: x['location']['coordinates']))

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['otpmap']
collection = db['atms']

async def create_index():
    await collection.create_index([('location', pymongo.GEOSPHERE)])

async def do_delete_many():
    n = await collection.count_documents({})
    print('%s documents before calling delete_many()' % n)
    await collection.delete_many({})
    print('%s documents after' % (await collection.count_documents({})))

async def do_insert():
    result = await collection.insert_many(atms)
    print('inserted %d docs' % (len(result.inserted_ids),))

loop = asyncio.get_event_loop()
loop.run_until_complete(do_delete_many())
loop.run_until_complete(do_insert())
loop.run_until_complete(create_index())
