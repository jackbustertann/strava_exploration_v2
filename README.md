# Strava Exploration

## Motivation

To build an interactive dashboard, using custom measures and dimensions, to enhance the reporting capilities provided by Strava.

## Project Plan

- 1) Use the Strava API to collect my personal running data.
- 2) Use a data warehousing platform to store and transform the data.
- 3) Use cloud automation to refresh the data daily.
- 4) Use a browser-based reporting tool to vizualise the data.

## Tech Stack

- Python
- GCP
  -  Big Query (data warehousing)
  -  Cloud Functions (cloud automation)
- dbt (data transformation)
- Streamlit (reporting)

## File Structure

- **main.py** - main script.
- **classes.py** - support classes for main script.
    - **StravaAPI** - class for interacting with Strava API endpoints.
    - **ETL** - class for transforming data for loading into data warehouse.
- **bq_config.json** - configuration file for bq load jobs.
- **credentials.cfg** - credentials file for third party connectors.