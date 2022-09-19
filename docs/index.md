## Motivation 💡

- To apply a modern tech-stack to a end-to-end technical project that I can showecase to future employers.
- To enhance the reporting provided out-of-the-box by Strava using my own custom dimensions and measures.

## Project Plan 🤓

1. Use the [Strava API](https://developers.strava.com/docs/reference/) to collect my personal running data. ✅
2. Use a data warehousing platform to store and transform the data. ✅
3. Use a browser-based reporting tool to vizualise the data. ✅
4. Use CI/CD as part of developement flow 🚧
5. Use cloud automation to refresh the data daily. 🚧 

## Tech Stack 👨‍💻

- Python ✅
- GCP
  -  Cloud Storage (data storage) ✅
  -  Big Query (data warehousing) ✅
  -  Container Registary (container storage) 🚧 
  -  Kubernetes (cloud automation) 🚧 
- dbt (data transformation) ✅
- Streamlit (reporting) ✅
- GitHub Actions (CI/CD) 🚧 
- Docker (containerisation) 🚧 

## Data Pipeline 

![](assets/Strava%20Exploration%20v2%20-%20Data%20Pipeline.png)

## CI/CD 

![](assets/Strava%20Exploration%20-%20CI_CD.png)

## [DBT Schema](https://github.com/jackbustertann/dbt_bq_strava_exploration_v2) 🗄️

![](assets/strava_exploration_dbt_schema.png)

## [Streamlit App](https://github.com/jackbustertann/strava_exploration_streamlit_app) 📈

![](assets/strava_exploration_streamlit_app.png)

## Coming Soon 🚀

- New manual refresh button for streamlit app
- New charts:
  * Activity comparison tool
  * Segment progress tracker
- New endpoints:
  * Activity Segments
  * Activity Streams
  * Club Activities

