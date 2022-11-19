# Set-up production environment in GCP

# - Store versioned docker images in GCR []

# 1) using gcloud cli

# -- Authenticate with gcloud:
# gcloud auth login
# gcloud config set project strava-exploration-v2
# gcloud iam service-accounts create gcr-test
# gcloud projects add-iam-policy-binding strava-exploration-v2 --member "serviceAccount:gcr-test@strava-exploration-v2.iam.gserviceaccount.com" --role "roles/storage.admin"
# gcloud projects add-iam-policy-binding strava-exploration-v2 --member "serviceAccount:gcr-test@strava-exploration-v2.iam.gserviceaccount.com" --role "roles/iam.serviceAccountTokenCreator"
# gcloud iam service-accounts keys create .secret/gcr-test.json --iam-account gcr-test@strava-exploration-v2.iam.gserviceaccount.com
# cat .secret/gcr-test.json | docker login -u _json_key --password-stdin \
https://gcr.io
# gcloud auth activate-service-account strava-exploration-v2-gcr-test@strava-exploration-v2.iam.gserviceaccount.com --key-file=.secret/gcr-test.json

# -- Build + Tag image: 
# -- docker build -t gcr.io/strava-exploration-v2/strava-exploration-v2:v0.2.1 .

# -- Push image to GCR 
# -- docker push gcr.io/strava-exploration-v2/strava-exploration-v2:v0.2.1
# -- gcloud container images list-tags gcr.io/strava-exploration-v2/strava-exploration-v2
# -- gcloud container images list --repository=[HOSTNAME]/[PROJECT-ID]

# -- Pull image from GCR
# -- docker pull gcr.io/strava-exploration-v2/strava-exploration-v2:v0.2.1

# 2) using github actions

# -- authenticate with gcloud
# -- configure docker
# -- build + tag docker image
# -- push docker image to ECR

# - Deploy a new Cloud Run instance

# - Trigger Cloud Run job on a schedule using Cloud Scheduler

