""" Strava API tests

A series of unit tests for the {StravaAPI} class
"""

import pytest
import requests_mock
import os, sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from classes import StravaAPI

strava_api_creds = dict(
    client_id = 12345,
    client_secret = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    access_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    refresh_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    token_type = "Helloo",
    expires_at = 9999999999,
    expires_in = 100000
)

strava_api = StravaAPI(strava_api_creds)

real_http = False

class TestRefreshAccessToken:

    @pytest.mark.parametrize("r_text,e_msg",[
        (json.dumps({
            'token_type': strava_api.token_type,
            'access_token': strava_api.access_token,
            'refresh_token': strava_api.refresh_token
        }), 
        'Output keys: (expires_at, expires_in) missing from refresh_access_token() response'
        )
    ])
    def test_output_keys_are_valid(self, r_text, e_msg):

        status_code = 200

        url = f"{strava_api.base_url}/oauth/token"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request("POST", url, text = r_text, status_code = status_code)

            with pytest.raises(Exception) as e:
                assert strava_api.refresh_access_token()
            assert (
                str(e.value)
                == e_msg
            )

    @pytest.mark.parametrize("r_text,e_msg",[
        (json.dumps({
            'token_type': strava_api.token_type,
            'access_token': strava_api.access_token,
            'refresh_token': strava_api.refresh_token,
            'expires_at': 0,
            'expires_in': strava_api.expires_in
        }), 
        'Access token expired at unix timestamp: 0'
        )
    ])
    def test_access_token_is_valid(self, r_text, e_msg):

        status_code = 200

        url = f"{strava_api.base_url}/oauth/token"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request("POST", url, text = r_text, status_code = status_code)

            with pytest.raises(Exception) as e:
                assert strava_api.refresh_access_token()
            assert (
                str(e.value)
                == e_msg
            )

    @pytest.mark.parametrize("r_text,e_msg",[
        (json.dumps({
            'token_type': strava_api.token_type,
            'access_token': strava_api.access_token,
            'refresh_token': strava_api.refresh_token[:-1] + 'b',
            'expires_at': strava_api.expires_at,
            'expires_in': strava_api.expires_in
        }), 
        'Refresh token has changed, check Strava API settings page'
        )
    ])
    def test_refresh_token_is_valid(self, r_text, e_msg):

        status_code = 200

        url = f"{strava_api.base_url}/oauth/token"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request("POST", url, text = r_text, status_code = status_code)

            with pytest.raises(Exception) as e:
                assert strava_api.refresh_access_token()
            assert (
                str(e.value)
                == e_msg
            )