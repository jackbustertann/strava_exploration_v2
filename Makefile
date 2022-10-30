# add docs

include .env

PROJECT_VERSION := $(shell yq '.version' version.yml)
NEW_PROJECT_VERSION := $(shell expr $(PROJECT_VERSION) + 1)

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

check-branch-name:
	@export branch_name=$(git symbolic-ref --short HEAD)
	@echo $(branch_name)
ifneq (,$(findstring patch, $(branch_name)))
	@echo "patch release"
else ifneq (,$(findstring minor, $(branch_name)))
	@echo "minor release"
else ifneq (,$(findstring major, $(branch_name)))
	@echo "major release"
else
	@echo "invalid branch name"
endif

check-release-version:
	@echo "The current release version is: $(PROJECT_VERSION)"

update-release-version: check-release-version
	@echo "The new release version is: $(NEW_PROJECT_VERSION)"
	@yq -i -y '.version = '$(NEW_PROJECT_VERSION)'' version.yml


