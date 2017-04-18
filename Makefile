CWD := $(shell readlink -en $(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))

.PHONY: all
all: fetch_dependancies build sweep push
.PHONY: ident_backup
ident_backup: fetch_dependancies build_ident_backup sweep push_ident_backup
.PHONY: ident_restore
ident_restore: fetch_dependancies build_ident_restore sweep push_ident_restore
.PHONY: ident
ident: fetch_dependancies build_ident sweep push_ident

.PHONY: start
start: env db.sqlite3
	env/bin/python manage.py runserver

.PHONY: init
init:
	docker pull jamrizzi/ident
	docker pull jamrizzi/ident-backup
	docker pull jamrizzi/ident-restore

.PHONY: build
build: build_ident_backup build_ident_restore build_ident
.PHONY: ident_base
ident_base:
	docker build --squash -t jamrizzi/ident-base:latest -f ./shared/base/Dockerfile ./shared
.PHONY: build_ident_backup
build_ident_backup:
	cp -r ./shared/config ./ident-backup/config
	cp -r ./shared/* ./ident-backup/src/pkg/
	docker build -t jamrizzi/ident-backup:latest -f $(CWD)/ident-backup/deployment/Dockerfile $(CWD)/ident-backup
	$(info built ident-backup)
.PHONY: build_ident_restore
build_ident_restore:
	cp -r ./shared/config ./ident-restore/config
	cp -r ./shared/* ./ident-restore/src/pkg/
	docker build -t jamrizzi/ident-restore:latest -f $(CWD)/ident-restore/deployment/Dockerfile $(CWD)/ident-restore
	$(info built ident-restore)
build_ident:
	cp -r ./shared/config ./ident/config
	cp -r ./shared/* ./ident/src/pkg/
	docker build -t jamrizzi/ident:latest -f $(CWD)/ident/deployment/Dockerfile $(CWD)/ident
	$(info built ident)

.PHONY: push
push: push_ident_base push_ident_backup push_ident_restore push_ident
.PHONY: push_ident_base
push_ident_base:
	docker push jamrizzi/ident-base:latest
	$(info pushed ident base)
.PHONY: push_ident_backup
push_ident_backup:
	docker push jamrizzi/ident-backup:latest
	$(info pushed ident backup)
.PHONY: push_ident_restore
push_ident_restore:
	docker push jamrizzi/ident-restore:latest
	$(info pushed ident-restore)
.PHONY: push_ident
push_ident:
	docker push jamrizzi/ident:latest
	$(info pushed ident)

.PHONY: pull
pull: pull_ident_base pull_ident_backup pull_ident_restore pull_ident
.PHONY: pull_ident_base
pull_ident_base:
	docker pull jamrizzi/ident-base:latest
	$(info pulled ident base)
.PHONY: pull_ident_backup
pull_ident_backup:
	docker pull jamrizzi/ident-backup:latest
	$(info pulled ident backup)
.PHONY: pull_ident_restore
pull_ident_restore:
	docker pull jamrizzi/ident-restore:latest
	$(info pulled ident-restore)
.PHONY: pull_ident
pull_ident:
	docker pull jamrizzi/ident:latest
	$(info pulled ident)

.PHONY: clean
clean: sweep bleach
	$(info cleaned)
.PHONY: sweep
sweep:
	@find . -name "*.pyc" -type f -delete
	@rm -rf ident-restore/config ident-backup/config ident/config
	@rm -f ident-restore/src/pkg/helper.py ident-backup/src/pkg/helper.py ident/src/pkg/helper.py
	@rm -rf **/*.pyc
	$(info swept)
.PHONY: bleach
bleach:
	rm -rf ident/env ident/db.sqlite3
	$(info bleached)

.PHONY: fetch_dependancies
fetch_dependancies: docker
	$(info fetched dependancies)
.PHONY: docker
docker:
ifeq ($(shell whereis docker), $(shell echo docker:))
	curl -L https://get.docker.com/ | bash
endif
	$(info fetched docker)

ident/env:
	virtualenv env
	env/bin/pip install -r requirements.txt
	$(info created virtualenv)

ident/db.sqlite3:
	make migrate
	$(info created db.sqlite3)

.PHONY: migrate
migrate:
	ident/env/bin/python manage.py makemigrations
	ident/env/bin/python manage.py migrate
	$(info migrated database)

.PHONY: freeze
freeze:
	ident/env/bin/pip freeze > ident/requirements.txt
