""" API tests

A series of unit tests for the parent {API} class
"""

import pytest
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from classes import API

api = API()

class TestRequest:
    """Test assertions about {request} function"""

    def test_invalid_request_type(self):
        """Test an invalid request type"""

        r_type = 'PUT'

        url = f"https://mock.codes/200"

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

            url = f"https://mock.codes/{status_code}"

            with pytest.raises(Exception) as e:
                assert api.request("GET", url)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: {status_code}"
            )

    def test_retry_request(self):
        """Test status codes which should throw exception after retry"""

        status_code = 429

        url = f"https://mock.codes/{status_code}"

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
        """Test a successful request"""

        status_code = 200

        url = f"https://mock.codes/{status_code}"

        response = api.request("GET", url)

        assert response["statusCode"] == 200
