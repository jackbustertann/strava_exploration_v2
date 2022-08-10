"""Classes

A support script containing classes/functions to be imported into main script.
"""

"""To do:

    refactor classes into unit functions
        api
        strava_api
        etl

    create unit test files for each class
"""


import time
import requests
import json
from datetime import datetime
from pytz import utc
from google.cloud import storage, bigquery
import csv
import os
import pandas as pd

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

            e_msg = f"Request type {r_type.upper()} not in ({', '.join(valid_r_types)})"

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

        self.client_id = api_creds['client_id']
        self.client_secret = api_creds['client_secret']
        self.refresh_token = api_creds['refresh_token']
        self.access_token = api_creds['access_token']

    def refresh_access_token(self):

        # test: check if access token is in response keys

        url = 'https://www.strava.com/api/v3/oauth/token'
        data = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': self.refresh_token
        }

        new_api_creds = self.request('POST', url = url, data = data)

        access_token = new_api_creds['access_token']
        self.access_token = access_token

        return print("Access token refreshed \n")

    def get_activities(self, before = current_date_unix, after = 0, page = 1, per_page = 100, iterate = True) -> list:
        
        # test: check if date range is valid
        # test: check zero data range case
        # test: check if output keys

        url = 'https://www.strava.com/api/v3/athlete/activities'
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

        url = f'https://www.strava.com/api/v3/activities/{activity_id}/laps'
        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_laps = self.request('GET', url = url, headers = headers)

        return activity_laps

    def get_activity_zones(self, activity_id: str) -> dict:

        # test: check output keys
        
        url = f'https://www.strava.com/api/v3/activities/{activity_id}/zones'
        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_zones = self.request('GET', url = url, headers = headers)

        return activity_zones

class GoogleCloudPlatform:

    def initiate_gcs_client(self, service_account_file):

        # test: check service account file contains correct keys

        self.gcs_client = storage.Client.from_service_account_json(service_account_file)

        return print('Google Cloud Storage client initiated! \n')

    def initiate_bq_client(self, service_account_file):

        # test: check service account file contains correct keys

        self.bq_client = bigquery.Client.from_service_account_json(service_account_file)

        return print('Big Query client initiated! \n')

    def upload_to_gcs(self, source_file_name, bucket_name, destination_blob_name):

        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        return print(f"File {source_file_name} uploaded to {destination_blob_name} \n")

    def load_to_bq_from_gcs(self, uri: str, table_id: str, write_disposition = 'WRITE_APPEND', schema = [], skip_leading_rows = 1, allow_jagged_rows = True, source_format = 'CSV'):

        # test: check uri is correct format
        # test: check write disposition is accepted value
        # test: check schema contains correct keys

        schema = [bigquery.SchemaField(col['column_name'], col['data_type']) for col in schema]

        job_config = bigquery.LoadJobConfig(
            schema = schema,
            write_disposition = write_disposition,
            source_format = source_format,
            skip_leading_rows = skip_leading_rows,
            allow_jagged_rows = allow_jagged_rows

        )

        load_job = self.bq_client.load_table_from_uri(uri, table_id, job_config = job_config)  

        load_job.result()  

        n_rows = load_job.output_rows

        return print(f"Loaded {n_rows} rows to {table_id} \n")

    def load_to_bq_from_df(self, df: pd.DataFrame, table_id: str, write_disposition = 'WRITE_APPEND', schema = []):

        schema = [bigquery.SchemaField(col['column_name'], col['data_type']) for col in schema]

        job_config = bigquery.LoadJobConfig(
            schema = schema,
            write_disposition = write_disposition
        )

        load_job = self.bq_client.load_table_from_dataframe(df, table_id, job_config = job_config)

        load_job.result()  

        n_rows = load_job.output_rows

        return print(f"Loaded {n_rows} rows to {table_id} \n")

    def query_bq(self, query_string):

        query_job = self.bq_client.query(query_string) 

        df = query_job.result().to_dataframe()

        return df

    def get_latest_date(self, table_id, date_col, date_format = '%Y-%m-%dT%H:%M:%SZ'):

        # test: check if output dataframe contains latest date column
        # test: check if latest date column is correct format

        query_string = f"""
        SELECT 
            MAX(PARSE_TIMESTAMP('{date_format}', {date_col})) AS latest_date 
        FROM 
            `{table_id}`
        """

        df = self.query_bq(query_string)

        latest_date = df.loc[0, 'latest_date']

        return latest_date

class Process:

    def flatten_data(self, response_json):

        # test: check specific case

        response_df = pd.json_normalize(response_json, sep = '_')

        return response_df

    def explode_data(self, df, col):

        # test: check specific case

        # creating a copy of data for processing
        df_raw = df.copy()

        # creating a row for every dict
        df_exploded = df_raw.explode(col)

        # creating a column for every dict attribute
        df_widened = pd.json_normalize(df_exploded[col])

        # dropping original col
        df_reduced = df_exploded.drop(columns = col).reset_index(drop = True)

        # combining new col with original data
        df_concat = pd.concat([df_reduced, df_widened], axis = 1)

        return df_concat

class Extract:

    def output_to_json(self, response_json, file):

        n_rows = len(response_json)

        with open(file, 'w') as f:
            json.dump(response_json, f, indent = 1)

        return print(f"{n_rows} rows outputted to file {file} \n")

    def output_to_csv(self, df, file, index = False, schema = []):

        n_rows = len(df)
        
        df.to_csv(file, index = index)

        if len(schema) > 0:
            self.reorder_csv(file, schema)

        return print(f"{n_rows} rows outputted to file {file} \n")

    def reorder_csv(self, file, schema):

        temp_file = file.split('.')[0] + '_temp.csv'

        os.rename(file, temp_file)

        with open(temp_file, 'r') as infile, open(file, 'a') as outfile:

            bq_cols = [col['column_name'] for col in schema]

            writer = csv.DictWriter(outfile, fieldnames = bq_cols)

            writer.writeheader()

            for row in csv.DictReader(infile):

                writer.writerow(row)
        
        os.remove(temp_file)

class Load(GoogleCloudPlatform):

    pass

class ETL(Process, Extract, Load):

    def process_data(self, response_json, set_values = {}, explode_cols = []):

        # test: check specific cases (one for each opt param)
        # test: check empty df case

        n_rows = len(response_json)

        if n_rows > 0:

            # flattening nested response data
            response_df = self.flatten_data(response_json)

            # setting values for new columns (e.g. last modified timestamp)
            for key, value in set_values.items():
                response_df[key] = value

            # exploding keys that contain a list of dicts
            for col in explode_cols:
                response_df = self.explode_data(response_df, col)
        
        else:

            response_df = pd.DataFrame()

        return response_df

    def extract_data(self, response_df, source_file_name, gcs_bucket_name, gcs_blob_name, bq_job_config):

        # outputting data to csv, with schema constraints
        self.output_to_csv(response_df, source_file_name, schema = bq_job_config['schema'])

        # uploading data to gcs bucket
        self.upload_to_gcs(source_file_name, gcs_bucket_name, gcs_blob_name)

    def load_data(self, gcs_bucket_name, gcs_blob_name, bq_table_id, bq_job_config): 

        # loading data to bq from gcs bucket
        bq_uri = f'gs://{gcs_bucket_name}/{gcs_blob_name}'

        self.load_to_bq_from_gcs(bq_uri, bq_table_id, bq_job_config['write_disposition'], bq_job_config['schema'])

    def ingest_data(self, response_json, source_file_name, gcs_bucket_name, gcs_blob_name, bq_table_id, bq_job_config, set_values = {}, explode_cols = []):

        response_df = self.process_data(response_json, set_values=set_values, explode_cols=explode_cols)

        self.extract_data(response_df, source_file_name, gcs_bucket_name, gcs_blob_name, bq_job_config)

        self.load_data(gcs_bucket_name, gcs_blob_name, bq_table_id, bq_job_config)
