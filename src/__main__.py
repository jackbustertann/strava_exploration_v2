from decouple import config

from src.utils.files import load_yaml
from src.utils.gcp import GoogleBigQuery, GoogleCloudStorage
from src.extract.dates import Dates
from src.extract.api import StravaAPI
from src.etl import ETL
from pprint import pprint

# - storing env variables -

PROD_RUN = config("PROD_RUN", cast=bool)

USE_RUN_DATE = config("USE_RUN_DATE", cast=bool)
RUN_DATE = config("RUN_DATE", cast=str)

api_keys = ["CLIENT_ID", "CLIENT_SECRET", "ACCESS_TOKEN", "REFRESH_TOKEN"]
STRAVA_API = {k.lower(): config(f"STRAVA_API__{k}") for k in api_keys}

GCP_ENV = "gcp_prod" if PROD_RUN else "gcp_dev"
GCP_SERVICE_ACCOUNT = config("GCP__SERVICE_ACCOUNT_FILE")

# - storing settings -

settings = load_yaml("settings.yml")

if PROD_RUN:

    print(f"Running script in production environment \n")

else:

    print(f"Running script in development environment \n")

pprint(settings[GCP_ENV])

# - connecting to GCP clients -

gcs = GoogleCloudStorage(f"{GCP_SERVICE_ACCOUNT}")

gbq = GoogleBigQuery(f"{GCP_SERVICE_ACCOUNT}")

# - Strava API authentication -

strava_api = StravaAPI(api_creds=STRAVA_API)

strava_api.refresh_access_token()

# - get dates -

dt = Dates()

dt.get_current_date()

dt.get_run_date(
    gbq,
    USE_RUN_DATE,
    RUN_DATE,
    gbq.create_table_id(
        settings[GCP_ENV]["project"], settings[GCP_ENV]["gbq"]["schema"], "activities"
    ),
)

# - initiate etl obj -

etl = ETL(gcs_obj=gcs, gbq_obj=gbq, settings=settings, gcp_env=GCP_ENV)

# - get activities data -

activities_json = strava_api.get_activities(after=dt.run_date_unix)

etl.run_strava_ingest(
    response_json=activities_json,
    endpoint="activities",
    last_updated=dt.current_date_str,
)

# - loop over activities -
activity_ids = [activity["id"] for activity in activities_json]

for activity_id in activity_ids:

    # - get activity laps data -
    activity_laps_json = strava_api.get_activity_laps(activity_id)

    etl.run_strava_ingest(
        response_json=activity_laps_json,
        endpoint="activity_laps",
        last_updated=dt.current_date_str,
        activity_id=activity_id,
    )

    # - get activity zones data -
    activity_zones_json = strava_api.get_activity_zones(activity_id)

    etl.run_strava_ingest(
        response_json=activity_zones_json,
        endpoint="activity_zones",
        last_updated=dt.current_date_str,
        activity_id=activity_id,
    )
