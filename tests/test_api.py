""" API tests

A series of unit tests for the parent {API} class
"""

import pytest
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from classes_new import API

api = API()


class TestGet:
    """Test assertions about {get} function"""

    def test_bad_request(self):
        """Test status codes which should throw exception without retry"""

        bad_status_codes = [401, 403, 404, 500]

        for status_code in bad_status_codes:

            url = f"https://mock.codes/{status_code}"

            with pytest.raises(Exception) as e:
                assert api.get(url)
            assert (
                str(e.value)
                == f"GET request to endpoint {url} failed with HTTP status: {status_code}"
            )

    def test_retry_request(self):
        """Test status codes which should throw exception after retry"""

        status_code = 429

        url = f"https://mock.codes/{status_code}"

        with pytest.raises(Exception) as e:
            assert api.get(url, max_retries=1)
        assert (
            str(e.value)
            == f"GET request to endpoint {url} failed with HTTP status: 429, after 1 retry"
        )

        with pytest.raises(Exception) as e:
            assert api.get(url, max_retries=2)
        assert (
            str(e.value)
            == f"GET request to endpoint {url} failed with HTTP status: 429, after 2 retries"
        )

    def test_success_request(self):
        """Test a successful request"""

        status_code = 200

        url = f"https://mock.codes/{status_code}"

        response = api.get(url)

        assert response["statusCode"] == 200
