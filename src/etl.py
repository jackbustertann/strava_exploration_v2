import pandas as pd
from src.transform.json import transform_response_json
from src.utils.files import output_to_csv, output_to_json


class ETL:
    def __init__(self, gcs_obj, gbq_obj, settings, gcp_env):
        self.gcs_obj = gcs_obj
        self.gbq_obj = gbq_obj
        self.settings = settings
        self.gcp_env = gcp_env
        self.gcp_project = settings[gcp_env]["project"]
        self.gcs_bucket_name = settings[gcp_env]["gcs"]["bucket"]
        self.gbq_schema_name = settings[gcp_env]["gbq"]["schema"]

    def run_upload(
        self,
        gcs_obj,
        response_df,
        source_file_name,
        gcs_bucket_name,
        gcs_blob_name,
        gbq_schema = {},
        file_format = "json"
    ):

        # outputting data to csv, with schema constraints
        if file_format == "csv":
            output_to_csv(response_df, source_file_name, schema=gbq_schema)
        
        elif file_format == "json":
            output_to_json(response_df, source_file_name)
        
        else:
            raise AssertionError(
                f"Un-supported file_format {file_format} for run_upload"
            )

        # uploading data to gcs bucket
        gcs_obj.upload_to_gcs(source_file_name, gcs_bucket_name, gcs_blob_name)

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
        self, response_json, gcs_obj, gcs_args, gbq_obj, gbq_args, transform_args, file_format="csv"
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

        response_df = transform_response_json(
            response_json,
            explode_list_keys=transform_args.get("explode_list_keys", {}),
            explode_dict_keys=transform_args.get("explode_dict_keys", False),
            set_values=transform_args.get("set_values", {}),
        )

        self.run_upload(
            gcs_obj,
            response_df,
            gcs_args["source_file_name"],
            gcs_args["bucket_name"],
            gcs_args["blob_name"],
            gbq_args["schema"],
            file_format=file_format
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

    def run_strava_ingest(self, response_json, endpoint, file_suffix, upload_only=True, file_format="json", transform_settings = {}, **kwargs):

        gcs_folder = kwargs.get("gcs_folder", endpoint)

        files_dict = self.gcs_obj.generate_file_locations(
            endpoint, 
            suffix=file_suffix, 
            folder=gcs_folder,
            file_format=file_format
        )

        gcs_args = {
            "source_file_name": files_dict["file_path_local"],
            "bucket_name": self.gcs_bucket_name,
            "blob_name": files_dict["file_path_gcs"],
        }

        if upload_only:

            self.run_upload(
                self.gcs_obj,
                response_json,
                gcs_args["source_file_name"],
                gcs_args["bucket_name"],
                gcs_args["blob_name"],
                file_format=file_format
            )
        
        else:

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

            transform_args = {
                k: v for k, v in transform_settings.items() 
                if k in ["explode_list_keys", "explode_dict_keys"]
            }

            transform_args["set_values"] = {
                k: kwargs[k] for k in transform_settings["set_value_columns"]
            }

            self.run_ingest(
                response_json,
                self.gcs_obj,
                gcs_args,
                self.gbq_obj,
                gbq_args,
                transform_args,
                file_format=file_format
            )

        print(f"Data ingestion complete for endpoint: {endpoint} \n")
