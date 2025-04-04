from datetime import datetime, timedelta
import json
import pytz
import requests


def get_dexafit(date, **kwargs):
    url = 'https://dexafitdetroitscheduling.as.me/api/scheduling/v1/availability/times?owner=b13e408a' \
            f'&appointmentTypeId=67627001&calendarId=6528790&startDate={date}&maxDays=1&timezone=America%2FNew_York'
    
    appointments = requests.get(url).json()

    if date not in appointments:
        return {'error': 'No appointments available for the selected date.'}
    
    for appointment in appointments[date]:
        time = appointment['time'].split('T')[1]
        appointment['formatted_time'] = datetime.strptime(time, '%H:%M:%S%z').strftime('%I:%M %p')
    
    return {'slots': appointments[date]}

def get_e3fitology(date, **kwargs):
    eastern = pytz.timezone('America/New_York') # UTC -4:00

    # Date Conversions
    try:
        naive_date = datetime.strptime(date, '%Y-%m-%d')
        date = naive_date.strftime('%Y-%m-%d')
        localized_date = eastern.localize(naive_date)
    except ValueError:
        return {'error': 'Invalid date format. Please use YYYY-MM-DD.'}

    start = int(localized_date.timestamp()) * 1000
    end = start + 86400
    url = 'https://backend.leadconnectorhq.com/appengine/appointment/free-slots?calendar_id=MNRgulWYxIEovwWVLFKb&' \
            'startDate={start_timestamp}&endDate={end_timestamp}&timezone=America%2FNew_York&sendSeatsPerSlot=false'

    response = requests.get(url.format(start_timestamp=start, end_timestamp=end))

    if date not in response.json():
        return {'error': 'No appointments available for the selected date.'}

    appointments = {'slots': []}

    for appointment in response.json()[date]['slots']:
        time = appointment.split('T')[1]        
        
        dict_ = {}
        dict_['time'] = appointment
        dict_['formatted_time'] = datetime.strptime(time, '%H:%M:%S%z').strftime('%I:%M %p')

        appointments['slots'].append(dict_)

    return appointments

def get_squareup(date, **kwargs):
    eastern = pytz.timezone('America/New_York') # UTC -4:00
    # with open('squareup_params.json') as file:
    #     params = json.load(file)

    url = 'https://app.squareup.com/appointments/api/buyer/availability'
    
    date = datetime.strptime(date, '%Y-%m-%d')

    current_month = datetime.now().month
    month = date.month

    # Parse the date and create date range for the request
    # date = date.strftime('%Y-%m-%d')
    # start_date = f'{datetime.now().strftime("%Y-%m-%d")}T00:00:00.000-04:00'
    # end_date = f'{date}T22:59:59.999-04:00'

    if month == current_month:
        current_date = datetime.now()
        start_date = f'{current_date.strftime("%Y-%m-%d")}T00:00:00.000-04:00'
    elif month > current_month:
        current_date = date.replace(day=1)
        start_date = f'{current_date.strftime("%Y-%m-%d")}T00:00:00.000-04:00'
    else:
        return {'slots': []}
    
    end_date = f'{(current_date + timedelta(days=31)).strftime("%Y-%m-%d")}T22:59:59.999-04:00'

    service_variation_id = kwargs.get('type', '')
    staff_id = kwargs.get('staff', '')

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'origin': 'https://book.squareup.com',
    }

    # Update the payload with the correct date range
    payload = {
        'search_availability_request': {
            'query': {
                'filter': {
                    'start_at_range': {
                        'start_at': start_date,
                        'end_at': end_date
                    },
                    'location_id': 'LHM69S0RE35FM',
                    'segment_filters': [{
                        'service_variation_id': service_variation_id or 'NJB4BWMVOQZYUDIGOVYZLICZ',
                        'team_member_id_filter': {'any': [staff_id or 'TM6xJx4LcoqZHDYi']}
                    }],
                }
            }
        }
    }

    # Make the API request
    response = requests.post(url, headers=headers, json=payload)

    # Process the response
    if response.status_code == 200:
        data = response.json()
        appointments = {'slots': []}

        # Extract the available slots from the response
        for slot in data.get('availability', []):
            raw_time = datetime.fromtimestamp(slot['start'], tz=eastern).strftime('%Y-%m-%dT%H:%M:%S-04:00')
            time = raw_time.split('T')[1]

            appointments['slots'].append({
                'time': raw_time,
                'formatted_time': datetime.strptime(time, '%H:%M:%S%z').strftime('%I:%M %p'),
            })

        return appointments
    else:
        return {'error': f'API request failed with status code {response.status_code}'}


# def get_available_slots(business_name, date):
#     asd = {
#         'service_variation_id': 'YQH7I7USAFNRRLJKCJY36ERU',
#         'staff_id': 'TMFX3LMZJKj61PXb'
#     }
#     appointments = globals()[f'get_{business_name}'](date, **asd)
#     print(len(appointments['slots']))
#     return appointments

# print(get_available_slots('squareup', '2025-03-31'))