from unittest import skip
import requests
import time
from datetime import datetime
from pytz import utc
import pandas as pd
import json
import numpy as np
import csv
import os

from google.cloud import storage, bigquery

current_date_utc = datetime.now(tz = utc)
current_date_unix = int(current_date_utc.timestamp())

# add descriptions to functions
# add data type validation to function inputs
# add tests to function inputs

class StravaAPI():

    def __init__(self, api_creds):

        self.client_id = api_creds['client_id']
        self.client_secret = api_creds['client_secret']
        self.refresh_token = api_creds['refresh_token']
        self.access_token = api_creds['access_token']

    def make_request(self, type, url, headers = {}, params = {}, data = {}, timeout = 10, sleep = 5, max_retries = 2, backoff = 2):

        i = 0

        while i <= max_retries:

            t_1 = time.time()

            r = requests.request(type, url, headers = headers, params = params, data = data, timeout = timeout)

            t_2 = time.time()
            t_12 = t_2 - t_1

            print(f'{type} request send to endpoint {r.url} \n')

            print(f'{type} request elapsed in {round(t_12, 2)}s, with HTTP status: {r.status_code} {r.reason} \n')

            if r.status_code == requests.codes.ok:

                r_dict = r.json()  

                return r_dict
            
            elif r.status_code in [408, 429]:

                print('Retrying in {sleep}s \n')

                time.sleep(sleep)

                sleep *= backoff
                i += 1

            else:

                return r.raise_for_status()

        print('Retry limit exceeded \n')

        return r.raise_for_status()

    def refresh_access_token(self):

        url = 'https://www.strava.com/api/v3/oauth/token'
        data = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': self.refresh_token
        }

        new_api_creds = self.make_request('POST', url = url, data = data)

        access_token = new_api_creds['access_token']
        self.access_token = access_token

        return print("Access token refreshed \n")

    def get_activities(self, before = current_date_unix, after = 0, page = 1, per_page = 100, iterate = True):
        
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

            activities_page = self.make_request('GET', url = url, headers = headers, params = params)

            activities += activities_page

            if not iterate:
                break

            n_results = len(activities_page)
            page += 1

        return activities

    def get_activity_laps(self, activity_id):

        url = f'https://www.strava.com/api/v3/activities/{activity_id}/laps'
        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_laps = self.make_request('GET', url = url, headers = headers)

        return activity_laps

    def get_activity_laps_list(self, activity_ids):

        activity_laps_list = []

        for activity_id in activity_ids:

            activity_laps = self.get_activity_laps(activity_id)

            activity_laps_list += activity_laps
        
        return activity_laps_list

    def get_activity_zones(self, activity_id):
        
        url = f'https://www.strava.com/api/v3/activities/{activity_id}/zones'
        headers = {'Authorization': f'Bearer {self.access_token}'}

        activity_zones = self.make_request('GET', url = url, headers = headers)

        return activity_zones

    def get_activity_zones_list(self, activity_ids):

        activity_zones_list = []

        for activity_id in activity_ids:

            activity_zones = self.get_activity_zones(activity_id)

            activity_zones_list += activity_zones
        
        return activity_zones_list

class ETL():

    def __init__(self):
        pass

    def initiate_gcs_client(self, service_account_file):

        self.gcs_client = storage.Client.from_service_account_json(service_account_file)

        return print('Google Cloud Storage client initiated! \n')

    def initiate_bq_client(self, service_account_file):

        self.bq_client = bigquery.Client.from_service_account_json(service_account_file)

        return print('Big Query client initiated! \n')

    def output_to_json(self, response_json, file):

        n_rows = len(response_json)

        with open(file, 'w') as f:
            json.dump(response_json, f, indent = 1)

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
        
        return print(f'Updated schema for {file} \n')

    def output_to_csv(self, df, file, index = False, schema = []):

        n_rows = len(df)
        
        df.to_csv(file, index = index)

        if len(schema) > 0:
            self.reorder_csv(file, schema)

        return print(f"{n_rows} rows outputted to file {file} \n")

    def upload_to_gcs(self, source_file_name, bucket_name, destination_blob_name):

        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        return print(f"File {source_file_name} uploaded to {destination_blob_name} \n")

    def load_to_bq_from_gcs(self, uri: str, table_id: str, write_disposition = 'WRITE_APPEND', schema = [], skip_leading_rows = 1, allow_jagged_rows = True, source_format = 'CSV'):

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

    def flatten_data(self, response_json):

        response_df = pd.json_normalize(response_json, sep = '_')

        return response_df

    def explode_data(self, df, col):

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

    def cast_data_types(self, df, schema):

        df_casted = df.copy()

        float_cols = [col['column_name'] for col in schema if (col['data_type'] == 'FLOAT')]
        for float_col in float_cols:
            try:
                df_casted[float_col] = df_casted[float_col].astype(float)
            except KeyError:
                df_casted[float_col] = np.nan

        int_cols = [col['column_name'] for col in schema if col['data_type'] == 'INTEGER']
        for int_col in int_cols:
            try:
                df_casted[int_col] = df_casted[int_col].fillna(-1)
                df_casted[int_col] = df_casted[int_col].astype(int)
            except KeyError:
                df_casted[int_col] = -1

        str_cols = [col['column_name'] for col in schema if col['data_type'] == 'STRING']
        for str_col in str_cols:
            try:
                df_casted[str_col] = df_casted[str_col].fillna("")
                df_casted[str_col] = df_casted[str_col].astype(str)
            except KeyError:
                df_casted[str_col] = ""

        bool_cols = [col['column_name'] for col in schema if col['data_type'] == 'BOOLEAN']
        for bool_col in bool_cols:
            try:
                df_casted[bool_col] = df_casted[bool_col].fillna(False)
                df_casted[bool_col] = df_casted[bool_col].astype(bool)
            except KeyError:
                df_casted[bool_col] = ""

        # add datetime 

        return df_casted

    def query_bq(self, query_string):

        query_job = self.bq_client.query(query_string) 

        df = query_job.result().to_dataframe()

        return df
    
    def get_latest_date(self, table_id, date_col, date_format = '%Y-%m-%dT%H:%M:%SZ'):

        query_string = f"""
        SELECT 
            MAX(PARSE_TIMESTAMP('{date_format}', {date_col})) AS latest_date 
        FROM 
            `{table_id}`
        """

        df = self.query_bq(query_string)

        latest_date = df.loc[0, 'latest_date']

        return latest_date

    def ingest_data(self, response_json, source_file_name, gcs_bucket_name, gcs_blob_name, bq_table_id, bq_job_config = {}, set_values = {}, explode_cols = []):

        n_rows = len(response_json)

        if n_rows > 0:

            # flattening nested response data
            response_df = self.flatten_data(response_json)

            # setting values for new columns (e.g. last modified timestamp)
            for key, value in set_values.items():
                response_df[key] = value

            # exploding keys contain list values
            for col in explode_cols:
                response_df = self.explode_data(response_df, col)
        
        else:

            response_df = pd.DataFrame()

        # outputting data to csv, with schema constraints
        self.output_to_csv(response_df, source_file_name, schema = bq_job_config['schema'])

        # uploading data to gcs bucket
        self.upload_to_gcs(source_file_name, gcs_bucket_name, gcs_blob_name)

        # loading data to bq from gcs bucket
        bq_uri = f'gs://{gcs_bucket_name}/{gcs_blob_name}'

        self.load_to_bq_from_gcs(bq_uri, bq_table_id, bq_job_config['write_disposition'], bq_job_config['schema'])

