""" API tests

A series of unit tests for the parent {API} class
"""

import pytest
import requests_mock
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from classes import API

mock_base_url = 'https://mock.codes/'
real_http = False

api = API()

class TestRequest:
    """Test assertions about {request} function"""

    def test_invalid_request_type(self):
        """Test an invalid request type"""

        invalid_r_types = ["PUT", "DELETE"]

        status_code = 200

        url = f"{mock_base_url}/{status_code}"

        for r_type in invalid_r_types:

            with requests_mock.Mocker(real_http=real_http) as m:

                m.request(r_type, url, status_code = status_code)

                with pytest.raises(Exception) as e:
                    assert api.request(r_type, url)
                assert (
                    str(e.value)
                    == f"Request type {r_type} not in (GET, POST)"
                )      

    def test_bad_request(self):
        """Test status codes which should throw exception without retry"""

        bad_status_codes = [401, 403, 404, 500]

        for status_code in bad_status_codes:
        
            with requests_mock.Mocker(real_http=real_http) as m:

                url = f"{mock_base_url}/{status_code}"

                m.request('GET', url, status_code = status_code)

                with pytest.raises(Exception) as e:
                    assert api.request("GET", url)
                assert (
                    str(e.value)
                    == f"GET request to endpoint {url} failed with HTTP status: {status_code}"
                )

    def test_retry_request(self):
        """Test status codes which should throw exception after retry"""

        status_code = 429

        url = f"{mock_base_url}/{status_code}"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request('GET', url, status_code = status_code)

            with pytest.raises(Exception) as e:
                assert api.request("GET", url, max_retries=1)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: 429, after 1 retry"
            )

            with pytest.raises(Exception) as e:
                assert api.request("GET", url, max_retries=2)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: 429, after 2 retries"
            )

    def test_success_request(self):
        """Test successful status code"""

        status_code = 200

        url = f"{mock_base_url}/{status_code}"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request('GET', url, status_code = status_code, text = '{"statusCode": 200, "description": "OK"}')

            response = api.request('GET', url)

        assert response["statusCode"] == 200 
        assert response["description"] == "OK"

            




