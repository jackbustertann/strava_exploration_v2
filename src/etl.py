import pandas as pd
from src.transform.json import flatten_data, explode_data
from src.utils.files import output_to_csv


class ETL:
    def __init__(self, gcs_obj, gbq_obj, settings, gcp_env):
        self.gcs_obj = gcs_obj
        self.gbq_obj = gbq_obj
        self.settings = settings
        self.gcp_env = gcp_env
        self.gcp_project = settings[gcp_env]["project"]
        self.gbq_bucket_name = settings[gcp_env]["gcs"]["bucket"]
        self.gbq_schema_name = settings[gcp_env]["gbq"]["schema"]

    def run_upload(
        self,
        gcs_obj,
        response_df,
        source_file_name,
        gcs_bucket_name,
        gcs_blob_name,
        gbq_schema,
    ):

        # outputting data to csv, with schema constraints
        output_to_csv(response_df, source_file_name, schema=gbq_schema)

        # uploading data to gcs bucket
        gcs_obj.upload_to_gcs(source_file_name, gcs_bucket_name, gcs_blob_name)

    def run_transform(self, response_json, set_values={}, explode_cols=[]):

        # test: check specific cases (one for each opt param)
        # test: check empty df case

        n_rows = len(response_json)

        if n_rows > 0:

            # flattening nested response data
            response_df = flatten_data(response_json)

            # setting values for new columns (e.g. last modified timestamp)
            for key, value in set_values.items():
                response_df[key] = value

            # exploding keys that contain a list of dicts
            for col in explode_cols:
                response_df = explode_data(response_df, col)

        else:

            response_df = pd.DataFrame()

        return response_df

    def run_load(
        self,
        gbq_obj,
        gcs_bucket_name,
        gcs_blob_name,
        gbq_table_id,
        gbq_write_disposition,
        gbq_schema,
    ):

        # loading data to bq from gcs bucket
        bq_uri = f"gs://{gcs_bucket_name}/{gcs_blob_name}"

        gbq_obj.load_to_gbq_from_gcs(
            bq_uri, gbq_table_id, gbq_write_disposition, gbq_schema
        )

    def run_ingest(
        self, response_json, gcs_obj, gcs_args, gbq_obj, gbq_args, transform_args
    ):
        """Transform raw Strava API response, upload to GCS and load to GBQ

        Args:

        - response_json: json
        - gcs_obj: obj
        - gcs_args: Dict[str, Any]
        - gbq_obj: obj
        - gbq_args: Dict[str, Any]
        - transform_args: Dict[str, Any]
        """

        response_df = self.run_transform(
            response_json,
            set_values=transform_args.get("set_values", {}),
            explode_cols=transform_args.get("explode_cols", []),
        )

        self.run_upload(
            gcs_obj,
            response_df,
            gcs_args["source_file_name"],
            gcs_args["bucket_name"],
            gcs_args["blob_name"],
            gbq_args["schema"],
        )

        self.run_load(
            gbq_obj,
            gcs_args["bucket_name"],
            gcs_args["blob_name"],
            gbq_args["table_id"],
            gbq_args["write_disposition"],
            gbq_args["schema"],
        )

        pass

    def run_strava_ingest(self, response_json, endpoint, **kwargs):

        file_suffix = kwargs[self.settings["etl"][endpoint]["file_suffix"]]

        assert file_suffix is not None

        files_dict = self.gcs_obj.generate_file_locations(endpoint, suffix=file_suffix)

        gcs_args = {
            "source_file_name": files_dict["file_path_local"],
            "bucket_name": self.gbq_bucket_name,
            "blob_name": files_dict["file_path_gcs"],
        }

        table_id = self.gbq_obj.create_table_id(
            self.gcp_project, self.gbq_schema_name, endpoint
        )

        gbq_args = {
            "schema": self.settings["tables"][endpoint]["columns"],
            "table_id": table_id,
            "write_disposition": self.settings[self.gcp_env]["gbq"]["tables"][endpoint][
                "write-disposition"
            ],
        }

        transform_settings = self.settings["etl"][endpoint]["transform"]

        assert "set_values" in transform_settings.keys()

        transform_args = {
            "set_values": {k: kwargs[k] for k in transform_settings["set_values"]}
        }

        if "explode_cols" in transform_settings.keys():
            transform_args["explode_cols"] = transform_settings["explode_cols"]

        self.run_ingest(
            response_json,
            self.gcs_obj,
            gcs_args,
            self.gbq_obj,
            gbq_args,
            transform_args,
        )

        print(f"Data ingestion complete for endpoint: {endpoint} \n")
