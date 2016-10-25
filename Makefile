SHELL:=/bin/bash

.PHONY: help run run-fancy db-reset db-init css css-watch _classloader \
	init structure-export config-export config-import \
	deploy-test-server run-deploy-db run-live-db _log-follow \
	ci-config-import ci-db-init _ci-init ci-run-acceptance_tests

.DEFAULT_GOAL := help

DB_CONTAINER?=docker_camac_db_1
DB_CONTAINER_HOSTNAME?=localhost
DB_CONTAINER_PORT?=49160


_log-follow: # Tail the log of the application
	@tail -f camac/logs/application.log


run-fancy: ## Create a tmux session that runs several useful commands at once: make up, make log-follow and make watch
	@tmux new-session -n 'camac runner' -d 'make run'
	@tmux split-window -v 'make _log-follow' # split vertically
	@tmux select-pane -U # go one pane upwards
	@tmux select-pane -U # go one pane upwards
	@tmux split-window -h 'make watch' # split horizontally on the most upper pane

	@tmux -2 attach-session -d

_ci-init: _submodule-update
	@rm -f camac/configuration
	@ln -fs ../kt_uri/configuration camac/configuration
	@ENV='ci' make -C camac/configuration/configs/
	@ENV='ci' make htaccess
	for i in `ls kt_uri/library/`; do rm -f "camac/library/$$i"; done
	for i in `ls kt_uri/library/`; do ln -sf "../../kt_uri/library/$$i" "camac/library/$$i"; done
	@chmod o+w camac/logs
	@chmod o+w camac/configuration/upload
	@make _classloader

_init: _submodule-update # Initialise the code, create the necessary symlinks
	@rm -f camac/configuration
	@ln -fs ../kt_uri/configuration camac/configuration
	@ENV='dev' make -C camac/configuration/configs/
	@ENV='dev' make htaccess
	for i in `ls kt_uri/library/`; do rm -f "camac/library/$$i"; done
	for i in `ls kt_uri/library/`; do ln -sf "../../kt_uri/library/$$i" "camac/library/$$i"; done
	@chmod o+w camac/logs
	@chmod o+w camac/configuration/upload
	@make _classloader

_submodule-update:
	@git submodule update --init --recursive || true


run: _init ## Runs the docker containers
	@docker-compose -f docker/docker-compose.yml up

db-reset: _sync_db_tools ## Drops the database and re-initialises it. Use the DB_CONTAINER variable to override the destination docker container
	@echo "Resetting the database"
	@sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no  chmod +x /var/local/tools/database/drop_user.sh
	@sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no bash /var/local/tools/database/drop_user.sh
	@make db-init

_sync_db_tools:
	echo "Syncing tools to docker container"
	sshpass -p "admin" scp -o StrictHostKeyChecking=no -r -P $(DB_CONTAINER_PORT) tools root@$(DB_CONTAINER_HOSTNAME):/var/local/
	sshpass -p "admin" scp -o StrictHostKeyChecking=no -r -P $(DB_CONTAINER_PORT) database root@$(DB_CONTAINER_HOSTNAME):/var/local/

db-init: _sync_db_tools ## Initialises the default database structure (without any data). Use the DB_CONTAINER variable to override the destination docker container
	echo "Initialise the database"
	echo "Create the camac user"
	sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no  chmod +x /var/local/tools/database/create_camac_user.sh
	sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no bash /var/local/tools/database/create_camac_user.sh
	echo "Insert the base structure"
	sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no chmod +x /var/local/tools/database/insert_base_structure.sh
	sshpass -p "admin" ssh root@$(DB_CONTAINER_HOSTNAME) -p $(DB_CONTAINER_PORT) -o StrictHostKeyChecking=no bash /var/local/tools/database/insert_base_structure.sh


structure-export: ## Dumps the database structure. Use the DB_CONTAINER variable to override the destination docker container
	@chmod +x tools/camac/export-structure.sh
	@tools/camac/export-structure.sh $(DB_CONTAINER)


_classloader: # Build the classmaps. These are important for performance
	@bash tools/camac/classmap_generator.sh

css: ## Create the css files from the sass files
	@cd camac/configuration/public/css/; make css


css-watch: ## Watch the sass files and create the css when they change
	@cd camac/configuration/public/css/; make watch


run-live-db: ## This is merely a command to help run another docker instance of the database (to be able to perform deplyoments)
	@docker ps | grep docker_camac_live_db_1 || echo "You must run the live version of the Database"
	@docker exec -it docker_camac_live_db_1 chmod +x /var/local/tools/database/create_camac_user.sh
	@docker exec -it docker_camac_live_db_1 /var/local/tools/database/create_camac_user.sh
	@docker exec -it docker_camac_live_db_1 chmod +x /var/local/tools/database/insert_uri_dump.sh
	@docker exec -it docker_camac_live_db_1 chown -R oracle /var/local/database/
	@docker exec -it docker_camac_live_db_1 /var/local/tools/database/insert_uri_dump.sh

_deployment_confirmation:
	@echo "Configuration will be overridden on the server"
	@echo "Press ctrl-c to abort"
	@read ohyeah

deploy-test-server: _deployment_confirmation css _classloader ## Move the code onto the test server
	@git checkout test
	@git commit --allow-empty -m "Test-Server deployment"
	@ENV='test' make -C camac/configuration/configs/
	@ENV='test' make htaccess
	@rsync -Lavz camac/* sy-jump:/mnt/sshfs/root@camac.sycloud.ch/var/www/uri/ --exclude=*.log --exclude=db-config*.ini
	@ssh sy-jump "chown -R www-data /mnt/sshfs/root@camac.sycloud.ch/var/www/uri/logs"
	@scp tools/deploy/test-server-htaccess sy-jump:/mnt/sshfs/root@camac.sycloud.ch/var/www/uri/public/.htaccess
	@scp tools/deploy/test-server-passwd sy-jump:/mnt/sshfs/root@camac.sycloud.ch/var/www/uri/passwd
	@cd db_admin/uri_database/ && USE_DB='test_server' python manage.py importconfig
	@ENV='dev' make -C camac/configuration/configs/

deploy-portal-test-server:
	@rsync -avz iweb_mock/* sy-jump:/mnt/sshfs/root@camac.sycloud.ch/var/www/iweb/ --exclude=node_modules/*
	# TODO: npm install, forever restart. How to call a command on the server?

run-deploy-db: ## This is merely a command to help run another docker instance for deploying
	docker-compose -f docker/docker-deploy-db.yml up


config-export: ## export the current database configuration
	@make -C db_admin/ exportconfig
	@echo "Config successfully written"


config-import: ## import the current database configuration. This will override your existing stuff!
	@make -C db_admin/ importconfig
	@echo "Config successfully imported"


data-truncate: ## Truncate the data in the database
	@make -C db_admin/ truncatedata
	# @make -C db_admin/ reset_sequences # TODO
	@echo "Data sucessfully truncated"


config-shell: ## start a database shell from the configuration management application
	@cd db_admin/uri_database/ && USE_DB='docker_dev' python manage.py shell


help: ## Show the help messages
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


run-acceptance-tests: ## run the acceptance tests
	@make -C db_admin/ run-acceptance-tests ${ARGS}

run-acceptance-tests-fast: ## run the acceptance tests fast - meaning, don't runn quite every test
	@make -C db_admin/ run-acceptance-tests-fast ${ARGS}

ci-run-acceptance-tests: ## Run a subset of the acceptance tests
	@make -C db_admin/ run-acceptance-tests-ci

install-api-doc: ## installs the api doc generator tool
	npm i -g apidoc

generate-api-doc: ## generates documentation for the i-web portal API
	apidoc -i kt_uri/configuration/Custom/modules/portal/controllers/ -o doc/
	@echo "Documentation was saved in /doc folder."

ci-config-import:
	@make -C db_admin/  importconfig-ci
	@echo "config successfully imported"

ci-pretend:
	@source /etc/profile
	@source /opt/xvfb.sh
	@pip install -r db_admin/requirements.txt
	@source /etc/apache2/envvars
	@python .wait-for-oracle-db.py oracle-eatmydata 1521
	@ssh-keyscan -H oracle-eatmydata > ~/.ssh/known_hosts
	@make _ci-init
	@make db-init DB_CONTAINER_HOSTNAME=oracle-eatmydata DB_CONTAINER_PORT=22
	@make ci-config-import
	@make ci-run-acceptance-tests

htaccess:
	python .make_htaccess.py ${ENV}
