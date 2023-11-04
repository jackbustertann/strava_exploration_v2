"""API

A support script for API calls. 1 class per API, 1 method per endpoint.
"""


import time
import requests
import json
from datetime import datetime
from pytz import utc

current_date_utc = datetime.now(tz = utc)
current_date_unix = int(current_date_utc.timestamp())


class API:
    """Parent API class

    Attributes:
    """

    def request(
        self,
        r_type: str,
        url: str,
        headers={},
        params={},
        data={},
        timeout=5,
        sleep=1,
        max_retries=2,
        backoff=1.5,
    ) -> dict:
        """Sends a GET/POST request

        Args:
            r_type:
            url: endpoint url
            headers:
            params:
            data:
            timeout:
            sleep:
            max_retries:
            backoff:

        Returns:

        Raises:
        """

        valid_r_types = ['GET', 'POST']

        # if {r_type} not valid, raise exception
        if r_type.upper() not in valid_r_types:

            valid_r_types_str = ', '.join(valid_r_types)

            e_msg = f"Request type {r_type.upper()} not in ({valid_r_types_str})"

            raise Exception(e_msg)

        # if retry limit {max_retries} has not been exceeded, try again
        i = 0
        while i <= max_retries:

            r_json = requests.request(
                r_type, url, headers=headers, params=params, timeout=timeout, data=data
            )

            # if success, output reponse body
            if r_json.status_code == requests.codes.ok:

                r_body = json.loads(r_json.text)

                return r_body

            # if short term status code, retry after {sleep} s
            elif r_json.status_code in [429]:

                if i < max_retries:

                    print(f"Retrying in {sleep}s \n")

                    time.sleep(sleep)

                    sleep *= backoff

                i += 1

            # if long term status code, throw exception
            else:

                e_msg = f"{r_type.upper()} request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}"

                raise Exception(e_msg)

        # if retry limit {max_retries} has been exceeded, throw exception
        print("Retry limit exceeded \n")

        if max_retries == 1:

            e_msg = f"{r_type.upper()} request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}, after {max_retries} retry"

        else:

            e_msg = f"{r_type.upper()} request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}, after {max_retries} retries"

        raise Exception(e_msg)

class StravaAPI(API):

    def __init__(self, api_creds: dict):

        self.client_id = api_creds.get('client_id')
        self.client_secret = api_creds.get('client_secret')
        self.refresh_token = api_creds.get('refresh_token')
        self.access_token = api_creds.get('access_token')
        self.token_type = api_creds.get('token_type')
        self.expires_at = api_creds.get('expires_at')
        self.expires_in = api_creds.get('expires_in')
        self.base_url = 'https://www.strava.com/api/v3'

    def refresh_access_token(self):

        url = f'{self.base_url}/oauth/token'

        data = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': self.refresh_token
        }

        new_api_creds = self.request('POST', url = url, data = data)

        output_keys = list(new_api_creds.keys())

        expected_output_keys = ['token_type', 'access_token', 'expires_at', 'expires_in', 'refresh_token']

        missing_output_keys = sorted(list(set(expected_output_keys).difference(set(output_keys))))

        if len(missing_output_keys) > 0:

            missing_output_keys_str = ', '.join(missing_output_keys)

            e_msg = f'Output keys: ({missing_output_keys_str}) missing from refresh_access_token() response'

            raise Exception(e_msg)

        refresh_token = new_api_creds['refresh_token']

        if refresh_token != self.refresh_token:

            e_msg = 'Refresh token has changed, check Strava API settings page'

            raise Exception(e_msg)

        expires_at_unix = new_api_creds['expires_at'] 

        if expires_at_unix < current_date_unix:

            e_msg =f'Access token expired at unix timestamp: {expires_at_unix}'

            raise Exception(e_msg)

        access_token = new_api_creds['access_token']

        self.access_token = access_token

        return print("Access token refreshed! \n")

    def get_activities(self, before = current_date_unix, after = 0, page = 1, per_page = 100, iterate = True) -> list:
        
        # test: check if date range is valid
        # test: check zero data range case
        # test: check if output keys

        url = f'{self.base_url}/athlete/activities'

        headers = {'Authorization': f'Bearer {self.access_token}'}

        n_results = per_page

        activities = []

        # iterating over all pages
        while n_results == per_page:

            params = {
                'before': before,
                'after': after,
                'page': page, 
                'per_page': per_page}

            activities_page = self.request('GET', url = url, headers = headers, params = params)

            activities += activities_page

            if not iterate:
                break

            n_results = len(activities_page)

            page += 1

        return activities

    def get_activity_laps(self, activity_id: str) -> dict:

        # test: check output keys

        url = f'{self.base_url}/activities/{activity_id}/laps'

        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_laps = self.request('GET', url = url, headers = headers)

        return activity_laps

    def get_activity_zones(self, activity_id: str) -> dict:

        # test: check output keys
        
        url = f'{self.base_url}/activities/{activity_id}/zones'

        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_zones = self.request('GET', url = url, headers = headers)

        return activity_zones

    def get_activity_streams(self, activity_id: str) -> dict:

        # test: check output keys
        
        url = f'{self.base_url}/activities/{activity_id}/streams'

        headers = {'Authorization': f'Bearer {self.access_token}'}

        stream_keys_str = 'time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth'

        params = {'keys': stream_keys_str}

        activity_streams =  self.request('GET', url = url, headers = headers, params=params)

        return activity_streams
