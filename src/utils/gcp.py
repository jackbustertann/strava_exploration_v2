from google.cloud import storage, bigquery
import pandas as pd

class GoogleCloudStorage:

    def __init__(self, service_account_file):
        self.gcs_client = storage.Client.from_service_account_json(service_account_file)

    def generate_file_locations(self, endpoint, suffix):

        file_name = f'{endpoint}_{suffix}.csv'
        file_path_local = f'data/{endpoint}/{file_name}'
        file_path_gcs = f'{endpoint}/{file_name}'

        return {
            'file_name': file_name,
            'file_path_local': file_path_local,
            'file_path_gcs': file_path_gcs
        }

    def upload_to_gcs(self, source_file_name, bucket_name, destination_blob_name):

        # test: check if file is uploaded

        bucket = self.gcs_client.bucket(bucket_name)

        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        return print(f"File {source_file_name} uploaded to {destination_blob_name} \n")


class GoogleBigQuery:

    def __init__(self, service_account_file):
        self.gbq_client = bigquery.Client.from_service_account_json(service_account_file)

    def load_to_gbq_from_gcs(self, uri: str, table_id: str, write_disposition = 'WRITE_APPEND', schema = [], skip_leading_rows = 1, allow_jagged_rows = True, source_format = 'CSV'):

        # test: check uri is correct format
        # test: check write disposition is accepted value
        # test: check schema contains correct keys
        # test: check if dummy bq table is updated 

        schema = [bigquery.SchemaField(col['name'], col['type']) for col in schema]

        job_config = bigquery.LoadJobConfig(
            schema = schema,
            write_disposition = write_disposition,
            source_format = source_format,
            skip_leading_rows = skip_leading_rows,
            allow_jagged_rows = allow_jagged_rows

        )

        load_job = self.gbq_client.load_table_from_uri(uri, table_id, job_config = job_config)  

        load_job.result()  

        n_rows = load_job.output_rows

        return print(f"Loaded {n_rows} rows to {table_id} \n")

    def load_to_gbq_from_df(self, df: pd.DataFrame, table_id: str, write_disposition = 'WRITE_APPEND', schema = []): # skip test

        schema = [bigquery.SchemaField(col['name'], col['type']) for col in schema]

        job_config = bigquery.LoadJobConfig(
            schema = schema,
            write_disposition = write_disposition
        )

        load_job = self.gbq_client.load_table_from_dataframe(df, table_id, job_config = job_config)

        load_job.result()  

        n_rows = load_job.output_rows

        return print(f"Loaded {n_rows} rows to {table_id} \n")

    def query_gbq(self, query_string):

        # test: check if dummy bq table is queried

        query_job = self.gbq_client.query(query_string) 

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

        df = self.query_gbq(query_string)

        latest_date = df.loc[0, 'latest_date']

        return latest_date

    def create_table_id(self, project, schema, table):

        table_id = f'{project}.{schema}.{table}'

        return table_id