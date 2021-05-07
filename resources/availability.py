from flask_restful import Resource, reqparse
from datetime import datetime
from dateutil import tz
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from models.user import UserAvailabilityModel
from collections import namedtuple
from calendar import monthrange
Date = namedtuple("Date", ["year", "month", "day"])
def all_dates_in_year(year):
    for month in range(1, 13):
        for day in range(1, monthrange(year, month)[1] + 1):
            yield Date(year, month, day)
from pytz import timezone

class NewAvailability(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('startDateTime')
        _parser.add_argument('endDateTime')
        userID = get_jwt_identity()
        data = _parser.parse_args()
        startDateTime = datetime.strptime(data['startDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        endDateTime = datetime.strptime(data['endDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if endDateTime <= startDateTime:
            return {"message": "End date time should be greater than start date time."}, 400
        availability = UserAvailabilityModel.find_exact_range(userID, startDateTime, endDateTime)
        if availability:
            return {"message": "Availability already saved."}, 400
        availabilities = UserAvailabilityModel.find_in_range(userID, startDateTime, endDateTime)
        userAvailability = UserAvailabilityModel(userID=userID, startDateTime=startDateTime, endDateTime=endDateTime)
        mergeAvailabilitiesAndSave(availabilities, userAvailability)

        return {"message": "User availability saved successfully."}, 201

class GetDates(Resource):
    @jwt_required
    def post(self):
        userID = get_jwt_identity()
        _parser = reqparse.RequestParser()
        _parser.add_argument('year')
        _parser.add_argument('timezone')
        data = _parser.parse_args()
        tzone = tz.gettz(data['timezone'])
        dates = {}
        startDateTime = datetime(int(data['year']), 1, 1, 0, 0, 0, 0, tzinfo=tzone)
        endDateTime = datetime(int(data['year']), 12, 31, 23, 59, 59, 999999, tzinfo=tzone)
        availability = UserAvailabilityModel.find_in_range_first(userID=userID,startDateTime=startDateTime,endDateTime=endDateTime)
        if len(availability) > 0:
            sdt = availability[0].startDateTime.replace(tzinfo=timezone('UTC'))
            sdt = sdt.astimezone(timezone(data['timezone']))
            month = int(sdt.strftime("%m"))
            day = int(sdt.strftime("%d"))
            if month not in dates:
                dates[month] = []
            if day not in dates[month]:
                dates[month].append(day)
        return { "dates" : dates }, 200

class UserAvailability(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('startDateTime')
        _parser.add_argument('endDateTime')
        _parser.add_argument('userID')
        data = _parser.parse_args()
        startDateTime = datetime.strptime(data['startDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        endDateTime = datetime.strptime(data['endDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        availabilities = UserAvailabilityModel.find_in_range(data['userID'], startDateTime, endDateTime)
        return {"availabilities" : [availability.json() for availability in availabilities]}, 200

class Availability(Resource):
    @jwt_required
    def post(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('startDateTime')
        _parser.add_argument('endDateTime')
        userID = get_jwt_identity()
        data = _parser.parse_args()
        startDateTime = datetime.strptime(data['startDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        endDateTime = datetime.strptime(data['endDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        availabilities = UserAvailabilityModel.find_in_range(userID, startDateTime, endDateTime)
        return {"availabilities" : [availability.json() for availability in availabilities]}, 200
    
    @jwt_required
    def delete(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id')
        userID = get_jwt_identity()
        data = _parser.parse_args()
        availability = UserAvailabilityModel.find_by_id(data["id"])
        if availability:
            if availability.userID != userID:
                return {"message" : "User not allowed to delete this availability"}, 400
            availability.delete_from_db()
        return {"message" : "Availability deleted."}, 200

# Assumes that there are overlaps
def mergeAvailabilitiesAndSave(availabilities, newAvailability):
    if len(availabilities) == 0:
        newAvailability.save_to_db()
    else:
        earliestStartDateTime = availabilities[0].startDateTime
        latestEndDateTime = availabilities[0].endDateTime
        for availability in availabilities:
            if availability.startDateTime < earliestStartDateTime:
                earliestStartDateTime = availability.startDateTime
            if availability.endDateTime > latestEndDateTime:
                latestEndDateTime = availability.endDateTime
            availability.delete_from_db()
        if newAvailability.startDateTime < earliestStartDateTime:
            earliestStartDateTime = newAvailability.startDateTime
        if newAvailability.endDateTime > latestEndDateTime:
            latestEndDateTime = newAvailability.endDateTime
        availability = UserAvailabilityModel(userID=newAvailability.userID, startDateTime=earliestStartDateTime, endDateTime=latestEndDateTime)
        availability.save_to_db()
        
