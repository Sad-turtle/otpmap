import json
import math
import motor.motor_tornado
import geopy.distance
import datetime
from pending import pending_visitor_count

def get_statistical_tpm_rate(atm, time_now):
    """Return approximated transaction count per minute for given time"""
    today = time_now.weekday()
    # while we still lack data for all days
    if today < 5:
        day = 'friday'
    elif today == 5:
        day = 'saturday'
    else:
        day = 'sunday'
    
    # Band aid for missing data
    if day not in atm['stats']:
        day = list(atm['stats'].keys())[0]
        
    hour_key = '{:02}'.format(time_now.hour)
    per_hour_values = atm['stats'][day][hour_key]
    
    for stats_data in per_hour_values:
        if time_now.minute <= stats_data['minutes_end']:
            return stats_data['value'] / (stats_data['minutes_end'] - stats_data['minutes_start'])

async def calculate_atm_ranking(client_location, atms, desired_amount=0):
    data = []
    nearby_atms = []
    other_atms = []
    
    for atm in atms:
        atm_location = atm['location']['coordinates']
        distance_meters = geopy.distance.distance(client_location, atm_location).m
        atm['distance'] = distance_meters
        print('ATM at {} is {:.2f}m from us'.format(tuple(reversed(atm_location)), distance_meters))

        # Our computation makes sense only for ATMs in walking vicinity of approx 1km            
        if distance_meters <= 1000 and atm['cash_remain'] >= desired_amount:
            nearby_atms.append(atm)
        else:
            other_atms.append(atm)
    
    # If there is one or less ATM near us, consider few other ones on best effort basis
    desired_distance = 1000
    while len(nearby_atms) < 2 and len(atms) > 1:
        desired_distance += 500
        nearby_atms = [atm for atm in atms if atm['distance'] <= desired_distance]
        other_atms = [atm for atm in atms if atm['distance'] > desired_distance]
        
    for atm in nearby_atms:
        time_to_go = atm['distance'] / 5000 * 60 # assume person is moving approx 5 km/hour
        time_now = datetime.datetime.now()
        # For testing:
        #time_now = datetime.datetime(2019, 10, 26, 13, 15)
        approximate_tpm = get_statistical_tpm_rate(atm, time_now)
        # Consider each coming person from app as requring additional minute
        coming_people = await pending_visitor_count(atm['_id'], time_now)
                    
        # Assume that one transaction can take up to 2 minutes
        # By taking into an account the time that is needed for one person to come and subtracting it from 2 minutes
        # we can get prediction on how much our queue will fill each minute, so by multiplying it by our walk time
        # we will get the size of queue, and it is rounded up to the next integeter for the worst case scenario
        trans_time = 2
        if approximate_tpm > 0 and trans_time > 1 / approximate_tpm:
            time_approx = time_to_go + math.ceil((time_to_go) / (abs(trans_time - 1 / approximate_tpm))) * trans_time + coming_people
        else:
            time_approx = time_to_go + coming_people

        atm['time_approx'] = math.ceil(time_approx)

        print('Time to go is {} minutes, statistical ATM usage is {} transactions/minute, {} coming people from app, approx. time: {}'.format(time_to_go, approximate_tpm, coming_people, time_approx))
        
    nearby_atms.sort(key=lambda x: x['time_approx'])
    
    return nearby_atms + other_atms
