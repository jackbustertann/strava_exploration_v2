import configparser
from datetime import datetime, timedelta
from pytz import utc
import json

from classes import StravaAPI, ETL

# - refresh access token -

config = configparser.ConfigParser()

config.read('credentials.cfg')

api_creds = config['STRAVA_API_V3']

api_obj = StravaAPI(api_creds = api_creds)

api_obj.refresh_access_token()

# - connecting to google cloud clients -

etl = ETL()

gcs_creds = config['GOOGLE_CLOUD_STORAGE']
gcs_sa_file, gcs_bucket = gcs_creds['service_account_file'], gcs_creds['bucket_name']

etl.initiate_gcs_client(service_account_file = gcs_sa_file)

bq_creds = config['GOOGLE_BIG_QUERY']
bq_sa_file = bq_creds['service_account_file']

etl.initiate_bq_client(service_account_file = bq_sa_file)

# - get last modified date -

start_date = datetime.combine(datetime.now(tz = utc), datetime.min.time()) - timedelta(days = 2)
start_date_unix = int(start_date.timestamp())

current_date = datetime.now(tz = utc)
current_date_str = datetime.strftime(current_date, '%Y-%m-%d')

# - get bq table configs -

with open('bq_config.json', 'r') as f:
    bq_config = json.load(f)

# - get activities -

activities_file = f'activities_{current_date_str}.json'
activities_file_local = f'data/activities/{activities_file}'
activities_file_gcs = f'activities/{activities_file}'

activities_json = api_obj.get_activities(after = start_date_unix)

etl.ingest_data(
    response_json = activities_json, 
    source_file_name = activities_file_local, 
    gcs_bucket_name = gcs_bucket,
    gcs_blob_name = activities_file_gcs,
    bq_table_id = bq_config['ACTIVITIES']['table_id'],
    bq_write_disposition = bq_config['ACTIVITIES']['write_disposition'],
    bq_schema = bq_config['ACTIVITIES']['schema']
    )

# - loop over activities -
activity_ids = [activity['id'] for activity in activities_json]

for activity_id in activity_ids:

    # - get activity laps -
    activity_laps_file = f'activity_laps_{activity_id}.json'
    activity_laps_file_local = f'data/activity_laps/{activity_laps_file}'
    activities_laps_file_gcs = f'activity_laps/{activity_laps_file}'


    activity_laps_json = api_obj.get_activity_laps(activity_id)

    etl.ingest_data(
        response_json = activity_laps_json, 
        source_file_name = activity_laps_file_local, 
        gcs_bucket_name = gcs_bucket,
        gcs_blob_name = activities_laps_file_gcs,
        bq_table_id = bq_config['ACTIVITY_LAPS']['table_id'],
        bq_write_disposition = bq_config['ACTIVITY_LAPS']['write_disposition'],
        bq_schema = bq_config['ACTIVITY_LAPS']['schema']
        )

    # - get activity zones -
    activity_zones_file = f'activity_zones_{activity_id}.json'
    activity_zones_file_local = f'data/activity_zones/{activity_zones_file}'
    activities_zones_file_gcs = f'activity_zones/{activity_zones_file}'

    activity_zones_json = api_obj.get_activity_zones(activity_id)

    etl.ingest_data(
        response_json = activity_zones_json, 
        source_file_name = activity_zones_file_local, 
        gcs_bucket_name = gcs_bucket,
        gcs_blob_name = activities_zones_file_gcs,
        bq_table_id = bq_config['ACTIVITY_ZONES']['table_id'],
        bq_write_disposition = bq_config['ACTIVITY_ZONES']['write_disposition'],
        bq_schema = bq_config['ACTIVITY_ZONES']['schema'],
        set_values = {'activity_id': activity_id},
        explode_cols = ['distribution_buckets']
        )


