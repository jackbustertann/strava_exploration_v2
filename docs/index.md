## Motivation 💡

- To get hands-on experience working with a modern ELT tech-stack that incorperates dbt and a cloud platform.
- To enhance the reporting provided out-of-the-box by Strava.
  - Define my own sport-specific metrics to benchmark different aspects of my training (i.e. volume, intensity and performance).
  - Aggregate my activity metrics across multiple sports and custom training periods (e.g. 6w, 13w, 26w, 52w).
  - Create my own custom activity types, such as intervals (road/track/virtual) and races (road/XC/virtual), to filter and group my activities.

## Project Plan 🤓

1. Use the [Strava API](https://developers.strava.com/docs/reference/) to collect my personal running data. ✅
2. Use a cloud-based data warehousing platform to store the data. ✅
3. Use DBT to transform, test and document the data. ✅
4. Use CI/CD to automate the deployment flow. ✅
5. Use cloud automation to refresh the data daily. ✅
6. Use a browser-based reporting tool to vizualise the data. 🚧 

## Tech Stack 👨‍💻

- Python 
- GCP
  -  Cloud Storage 
  -  Big Query 
  -  Container Registry 
  -  Cloud Run 
  -  Cloud Scheduler 
- GitHub Actions 
- Docker 
- dbt
- Streamlit 

## Data Pipeline

![](assets/Strava%20Exploration%20v2%20-%20Data%20Pipeline.png)

TODO: add activity streams endpoint

## CI/CD 

![](assets/Strava%20Exploration%20-%20CI_CD.png)

## [DBT Lineage](https://github.com/jackbustertann/dbt_bq_strava_exploration_v2) 🗄️

![](assets/strava_exploration_dbt_lineage.png)

## [Steamlit Web App](https://jackbustertann-strava-exploration-streamlit-app-app-xh16o5.streamlit.app/)

<img width="400" alt="Screenshot 2024-03-16 at 18 49 26" src="https://github.com/jackbustertann/strava_exploration_v2/assets/42582606/16341951-ccfb-4bb1-b43a-82962494f0df">

<img width="398" alt="Screenshot 2024-03-16 at 18 49 59" src="https://github.com/jackbustertann/strava_exploration_v2/assets/42582606/5bef1bf4-3bca-48bd-89ed-4e797d845c79">



## Future Optimisations 🚀

- In-corperate activity streams data source into data model. ✅
  - Define custom HR, power and pace zones that update dynamically over time.
    - HR -> age
    - power -> FTP
    - pace -> 5k race times
  - Calculate time in HR, power and pace zones.
  - Calculate best 15", 1', 5', 10' and 20' power efforts.
- Extend DBT functionality across project.
  - Use Jinja, Macros & Packages to re-factor code.
  - Use advanced materialisation types to optimise build/query time.
  - Use data quality tests to improve data integrity + source freshness.
  - Use the semantic layer to build consistent and flexible mertics.
- Migrate DWH from BigQuery to Snowfake.
  - Use snowpipe to load data directly from GCS bucket on event.
  - Apply data modelling best practices.
- Create activity-level views in Streamlit app.

