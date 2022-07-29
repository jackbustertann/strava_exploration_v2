"""Classes

A support script containing classes/functions to be imported into main script.
"""

"""To do:

    refactor classes into unit functions
        api
        strava_api
        etl

    create unit test files for each class

    auto-lint

    set-up ci/cd process
        update requirements.txt file
        testing (pytest)
        linting (black)
        building
"""


import time
import requests
import json


class API:
    """Parent API class

    Attributes:
    """

    def get(
        self,
        url: str,
        headers={},
        params={},
        timeout=5,
        sleep=1,
        max_retries=2,
        backoff=1.5,
    ) -> dict:
        """Sends a GET request

        Args:
            url: endpoint url
            headers:
            params:
            timeout:
            sleep:
            max_retries:
            backoff:

        Returns:

        Raises:
        """

        # if retry limit {max_retries} has not been exceeded, try again
        i = 0
        while i <= max_retries:

            t_1 = time.time()

            r_json = requests.request(
                "GET", url, headers=headers, params=params, timeout=timeout
            )

            t_2 = time.time()
            t_12 = t_2 - t_1

            # if success, output reponse body
            if r_json.status_code == requests.codes.ok:

                try:

                    r_body = r_json.json()

                except BaseException:

                    e_msg = f"GET request to endpoint {r_json.url} returned no results"

                    print(e_msg)

                    return {}

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

                e_msg = f"GET request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}"

                raise Exception(e_msg)

        # if retry limit {max_retries} has been exceeded, throw exception
        print("Retry limit exceeded \n")

        if max_retries == 1:

            e_msg = f"GET request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}, after {max_retries} retry"

        else:

            e_msg = f"GET request to endpoint {r_json.url} failed with HTTP status: {r_json.status_code}, after {max_retries} retries"

        raise Exception(e_msg)
