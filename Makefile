# add docs

include .env

clean-files:
	@echo "removing cache files"
	@echo | find . | grep -E "(/*cache*)"
	@find . | grep -E "(/*cache*)" | xargs rm -rf

update-requirements:
	@echo "updating requirements.txt"
	@pipenv requirements > requirements.txt

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
	@docker build --tag strava-exploration-v2 .
	@docker run --env-file .env --env PROD_RUN=False -p 8080:8080 strava-exploration-v2
	-@docker rm `docker ps -q -f status=exited`
	@docker image rm strava-exploration-v2

docker-prod-run: activate-venv
	@docker build --tag strava-exploration-v2 .
	@docker run --env-file .env --env PROD_RUN=True -p 8080:8080 strava-exploration-v2
	-@docker rm `docker ps -q -f status=exited`
	@docker image rm strava-exploration-v2

unit-tests:
	@pytest tests -v --cov -W ignore::DeprecationWarning

pr: unit-tests clean


