CWD := $(shell readlink -en $(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))
DOCKER_USER := "jamrizzi"
TAG := "major-refactor"

.PHONY: all
all: clean fetch_dependancies build
.PHONY: ident_base
ident_base: clean fetch_dependancies build_ident_base
.PHONY: ident_backup
ident_backup: clean fetch_dependancies build_ident_backup
.PHONY: ident_restore
ident_restore: clean fetch_dependancies build_ident_restore
.PHONY: ident
ident: clean fetch_dependancies build_ident

.PHONY: init
init:
	docker pull $(DOCKER_USER)/ident-base:$(TAG)
	docker pull $(DOCKER_USER)/ident-backup:$(TAG)
	docker pull $(DOCKER_USER)/ident-restore:$(TAG)
	docker pull $(DOCKER_USER)/ident:$(TAG)

.PHONY: build
build: build_ident_base build_ident_backup build_ident_restore build_ident
.PHONY: ident_base
build_ident_base:
	docker build --squash -t $(DOCKER_USER)/ident-base:$(TAG) -f $(CWD)/shared/base/Dockerfile $(CWD)/shared
	$(info built $(DOCKER_USER)/ident-base:$(TAG))
.PHONY: build_ident_backup
build_ident_backup:
	cp -r ./shared/config ./ident-backup/config
	cp -r ./shared/helper.py ./ident-backup/src/pkg/helper.py
	docker build -t $(DOCKER_USER)/ident-backup:$(TAG) -f $(CWD)/ident-backup/deployment/Dockerfile $(CWD)/ident-backup
	$(info built ident-backup)
.PHONY: build_ident_restore
build_ident_restore:
	cp -r ./shared/config ./ident-restore/config
	cp -r ./shared/helper.py ./ident-restore/src/pkg/helper.py
	docker build -t $(DOCKER_USER)/ident-restore:$(TAG) -f $(CWD)/ident-restore/deployment/Dockerfile $(CWD)/ident-restore
	$(info built ident-restore)
build_ident:
	cp -r ./shared/config ./ident/config
	cp -r ./shared/helper.py ./ident/src/pkg/helper.py
	docker build -t $(DOCKER_USER)/ident:$(TAG) -f $(CWD)/ident/deployment/Dockerfile $(CWD)/ident
	$(info built ident)

.PHONY: push
push: push_ident_base push_ident_backup push_ident_restore push_ident
.PHONY: push_ident_base
push_ident_base:
	docker push $(DOCKER_USER)/ident-base:$(TAG)
	$(info pushed ident-base:latest)
.PHONY: push_ident_backup
push_ident_backup:
	docker push $(DOCKER_USER)/ident-backup:$(TAG)
	$(info pushed ident backup)
.PHONY: push_ident_restore
push_ident_restore:
	docker push $(DOCKER_USER)/ident-restore:$(TAG)
	$(info pushed ident-restore)
.PHONY: push_ident
push_ident:
	docker push $(DOCKER_USER)/ident:$(TAG)
	$(info pushed ident)

.PHONY: pull
pull: pull_ident_base pull_ident_backup pull_ident_restore pull_ident
.PHONY: pull_ident_base
pull_ident_base:
	docker pull $(DOCKER_USER)/ident-base:$(TAG)
	$(info pulled ident base)
.PHONY: pull_ident_backup
pull_ident_backup:
	docker pull $(DOCKER_USER)/ident-backup:$(TAG)
	$(info pulled ident backup)
.PHONY: pull_ident_restore
pull_ident_restore:
	docker pull $(DOCKER_USER)/ident-restore:$(TAG)
	$(info pulled ident-restore)
.PHONY: pull_ident
pull_ident:
	docker pull $(DOCKER_USER)/ident:$(TAG)
	$(info pulled ident)

.PHONY: run_ident
run_ident:
	docker run --name some-ident --rm -e TAG=$(TAG) -v /var/run/docker.sock:/var/run/docker.sock $(DOCKER_USER)/ident:$(TAG)

.PHONY: env
env: ident-backup/env ident-restore/env ident/env
ident-backup/env:
	virtualenv ident-backup/env
	ident-backup/env/bin/pip install -r ident-backup/requirements.txt
	$(info created ident-backup virtualenv)
ident-restore/env:
	virtualenv ident-restore/env
	ident-restore/env/bin/pip install -r ident-restore/requirements.txt
	$(info created ident-restore virtualenv)
ident/env:
	virtualenv ident/env
	ident/env/bin/pip install -r ident/requirements.txt
	$(info created ident virtualenv)

.PHONY: freeze
freeze: freeze_ident_backup freeze_ident_restore freeze_ident
.PHONY: freeze_ident_backup
freeze_ident_backup:
	ident-backup/env/bin/pip freeze > ident-backup/requirements.txt
.PHONY: freeze_ident_restore
freeze_ident_restore:
	ident-restore/env/bin/pip freeze > ident-restore/requirements.txt
.PHONY: freeze_ident
freeze_ident:
	ident/env/bin/pip freeze > ident/requirements.txt

.PHONY: clean
clean:
	@find . -name "*.pyc" -type f -delete
	@rm -rf ident-backup/config ident-restore/config ident/config
	@rm -rf ident-backup/src/pkg/helper.py ident-restore/src/pkg/helper.py ident/src/pkg/helper.py
	@rm -rf ident-backup/env ident-restore/env ident/env
	@rm -rf **/*.pyc
	$(info cleaned)

.PHONY: fetch_dependancies
fetch_dependancies: docker
	$(info fetched dependancies)
.PHONY: docker
docker:
ifeq ($(shell whereis docker), $(shell echo docker:))
	curl -L https://get.docker.com/ | bash
endif
	$(info fetched docker)
