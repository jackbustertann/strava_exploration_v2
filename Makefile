# add docs

include .env

# PROJECT_VERSION := $(shell yq '.version' settings.yml)

clean-files:
	@echo "removing cache files"
	@echo | find . | grep -E "(/*cache*)"
	@find . | grep -E "(/*cache*)" | xargs rm -rf

update-requirements:
	@echo "updating requirements.txt"
	@pipenv lock -r > requirements.txt

lint-files:
	@echo "linting files"
	@black src/*.py 

clean: update-requirements clean-files lint-files

activate-venv:
ifeq ($(VIRTUAL_ENV), )
	@echo "activating virtual env"
	pipenv shell
else
	@echo "virtual env is already activated"
endif

local-staging-run: activate-venv
	@echo $(RUN_DATE)
	@export PROD_RUN=False
	@python -m src

local-prod-run: activate-venv
	@echo $(RUN_DATE)
	@export PROD_RUN=True
	@python -m src

docker-clean:
	@echo "Remove all non-running containers"
	-@docker rm `docker ps -q -f status=exited`
	@echo "Delete all untagged/dangling (<none>) images"
	-@docker rmi `docker images -q -f dangling=true`

docker-staging-run: activate-venv
	@docker build --tag strava-exploration-v3:test .
	@docker run --env-file .env --env PROD_RUN=False strava-exploration-v3:test
	-@docker rm `docker ps -q -f status=exited`
	@docker image rm strava-exploration-v3:test

docker-prod-run: activate-venv
	@docker build --tag strava-exploration-v3:test .
	@docker run --env-file .env --env PROD_RUN=True strava-exploration-v3:test
	-@docker rm `docker ps -q -f status=exited`
	@docker image rm strava-exploration-v3:test

unit-tests:
	@pytest tests -v --cov -W ignore::DeprecationWarning


# check-release-version:
# PROJECT_VERSION=$(yq '.version' settings.yml)
# echo $PYTHON_VERSION

# update-release-version:
# PROJECT_VERSION=$(expr $PROJECT_VERSION + 1)
# echo $PROJECT_VERSION
# yq -i -y '.version = '$PROJECT_VERSION'' settings.yml

# check-branch-name

# pr
# check-branch-name
# activate-venv
# unit-tests
# clean
# docker-staging-run
# docker-clean
# update-release-version

