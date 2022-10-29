""" API tests

A series of unit tests for the parent {API} class
"""

import pytest
import requests_mock
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.extract.api import API

mock_base_url = "https://mock.codes/"
real_http = False

api = API()


class TestRequest:
    """Test assertions about {request} function"""

    @pytest.mark.parametrize("r_type", ["PUT", "DELETE"])
    def test_invalid_request_type(self, r_type):
        """Test an invalid request types"""

        status_code = 200

        url = f"{mock_base_url}/{status_code}"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request(r_type, url, status_code=status_code)

            with pytest.raises(Exception) as e:
                assert api.request(r_type, url)
            assert str(e.value) == f"Request type {r_type} not in (GET, POST)"

    @pytest.mark.parametrize("status_code", [401, 403, 404, 500])
    def test_bad_request(self, status_code):
        """Test status codes which should throw exception without retry"""

        with requests_mock.Mocker(real_http=real_http) as m:

            url = f"{mock_base_url}/{status_code}"

            m.request("GET", url, status_code=status_code)

            with pytest.raises(Exception) as e:
                assert api.request("GET", url)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: {status_code}"
            )

    @pytest.mark.parametrize("status_code,max_retries", [(429, 1), (429, 2)])
    def test_retry_request(self, status_code, max_retries):
        """Test status codes which should throw exception after retry"""

        url = f"{mock_base_url}/{status_code}"

        retry_alias = "y" if max_retries == 1 else "ies"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request("GET", url, status_code=status_code)

            with pytest.raises(Exception) as e:
                assert api.request("GET", url, max_retries=max_retries)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: 429, after {max_retries} retr{retry_alias}"
            )

    @pytest.mark.parametrize("status_code,text", [(200, '{"statusCode": 200}')])
    def test_success_request(self, status_code, text):
        """Test successful status code"""

        url = f"{mock_base_url}/{status_code}"

        with requests_mock.Mocker(real_http=real_http) as m:

            m.request("GET", url, status_code=status_code, text=text)

            response = api.request("GET", url)

        assert response["statusCode"] == status_code
