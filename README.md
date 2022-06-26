Github Pages Site: https://jackbustertann.github.io/strava_exploration_v2/

File Structure:

- **main.py** - main script.
- **classes.py** - support classes for main script.
    - **StravaAPI** - class for interacting with Strava API endpoints.
    - **ETL** - class for transforming data for loading into data warehouse.
- **bq_config.json** - configuration file for bq load jobs.
- **credentials.cfg** - credentials file for third party connectors.

DBT Schema GitHub Repo: https://github.com/jackbustertann/dbt_bq_strava_exploration_v2

Streamlit App GitHub Repo: https://github.com/jackbustertann/strava_exploration_streamlit_app
