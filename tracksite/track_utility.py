# some utilities for tracking functionality
import json
import re


def format_date(datetime):
    datetime = datetime.replace('T', ' ')
    datetime = datetime.replace('Z', '')
    datetime = datetime.replace('"', '')

    return datetime


def format_message(event, carrier):
    event['message'] = event['message'].title()

    if carrier == "USPS":
        if event['message'].find(" In ") != -1:
            event['message'] = event['message'].split(" In ")[0]
        if event['message'].find(" Pm ") != -1:
            event['message'] = event['message'].split(" Pm ")[1]
        elif event['message'].find(" Am ") != -1:
            event['message'] = event['message'].split(" Am ")[1]

    return event


def add_to_profile(track, user, track_id):
    """Format tracking detail from json object track."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]

    str = track.details
    if str == '':
        return

    details = json.loads(str)
    event = details[len(details) - 1]

    datetime = event.get('datetime', ' ')
    datetime = format_date(datetime)
    event['datetime'] = datetime

    carrier = track.carrier.replace('"', '')
    event = format_message(event, carrier)

    city = event['tracking_location'].get('city', 'null')
    if city != 'null':
        event['tracking_location']['city'] = city.title()

    token = datetime.split(" ")
    date = token[0].split("-")
    year = date[0]
    month = months[int(date[1]) - 1]
    day = date[2]
    event['date'] = month + " " + day + ", " + year
    event['time'] = token[1]
    event['track_num'] = track.trackNum
    event['owner'] = user
    event['carrier'] = carrier
    event['track_id'] = track_id
    if track.est_delivery_date is None:
        event['est_date'] = ""
    else:
        event['est_date'] = track.est_delivery_date.strftime('%m/%d/%y %H:%M')

    return event


def identify(track_num):
    """Identify tracking number belongs to which shipment service"""
    track_num = track_num.strip()
    if not track_num.isalnum():
        return ''

    if re.match("^[A-Za-z]*$", track_num):
        return ''

    length = len(track_num)

    if track_num.startswith('1Z') and track_num[-1].isdigit():
        return 'UPS'
    elif length == 13 or length == 30:
        return 'USPS'
    elif length == 12 or length == 15:
        return 'fedex'
    elif length == 20:
        if track_num.isdigit():
            if track_num.startswith('96'):
                return 'fedex'
            elif track_num.startswith('0'):
                return 'USPS'
    elif length == 22:
        if track_num.isdigit():
            if track_num.startswith('00'):
                return 'fedex'
            else:
                return 'USPS'

    return ''


# easypost API test key which is limited for sample query use only
easypost_key = '5ijkBrU1DxmKSNt2rwpnNQ'

# result sample from real API
fake_result = {
    "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
    "carrier": "UPS",
    "carrier_detail": 'null',
    "created_at": "2015-10-28T00:19:09Z",
    "est_delivery_date": 'null',
    "fees": [
        {
            "amount": 'null',
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "charged": True,
            "object": "Fee",
            "refunded": False,
            "type": "TrackerFee"
        }
    ],
    "id": "trk_0e7a5f045f1a4c548169f3b6d57d2fcb",
    "mode": "production",
    "object": "Tracker",
    "shipment_id": 'null',
    "signed_by": "HANG",
    "status": "delivered",
    "tracking_code": "1ZA4R1790312830803",
    "tracking_details": [
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-28T17:01:54Z",
            "message": "BILLING INFORMATION RECEIVED",
            "object": "TrackingDetail",
            "status": "pre_transit",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": 'null',
                "country": "US",
                "object": "TrackingLocation",
                "state": 'null',
                "zip": 'null'
            }
        },
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-28T20:48:00Z",
            "message": "ORIGIN SCAN",
            "object": "TrackingDetail",
            "status": "in_transit",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": "PALATINE",
                "country": "US",
                "object": "TrackingLocation",
                "state": "IL",
                "zip": 'null'
            }
        },
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-29T00:04:00Z",
            "message": "DEPARTURE SCAN",
            "object": "TrackingDetail",
            "status": "in_transit",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": "PALATINE",
                "country": "US",
                "object": "TrackingLocation",
                "state": "IL",
                "zip": 'null'
            }
        },
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-29T22:33:00Z",
            "message": "ARRIVAL SCAN",
            "object": "TrackingDetail",
            "status": "in_transit",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": "NEW STANTON",
                "country": "US",
                "object": "TrackingLocation",
                "state": "PA",
                "zip": 'null'
            }
        },
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-30T06:28:00Z",
            "message": "OUT FOR DELIVERY",
            "object": "TrackingDetail",
            "status": "out_for_delivery",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": "PITTSBURGH",
                "country": "US",
                "object": "TrackingLocation",
                "state": "PA",
                "zip": 'null'
            }
        },
        {
            "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
            "datetime": "2015-09-30T14:22:00Z",
            "message": "DELIVERED",
            "object": "TrackingDetail",
            "status": "delivered",
            "tracking_location": {
                "api_key": "5ijkBrU1DxmKSNt2rwpnNQ",
                "city": "PITTSBURGH",
                "country": "US",
                "object": "TrackingLocation",
                "state": "PA",
                "zip": "15217"
            }
        }
    ],
    "updated_at": "2015-10-28T00:19:09Z",
    "weight": 22.4
}
