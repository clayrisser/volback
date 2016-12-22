CWD := $(shell readlink -en $(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))


.PHONY: all
all: fetch_dependancies build push


## BUILD ##
.PHONY: build
build: build_dockplicity_backup build_dockplicity_cron

.PHONY: build_dockplicity_backup
build_dockplicity_backup:
	docker build -t jamrizzi/dockplicity-backup:latest -f $(CWD)/dockplicity-backup/Dockerfile $(CWD)/dockplicity-backup
	$(info built dockplicity backup)

.PHONY: build_dockplicity_cron
build_dockplicity_cron:
	docker build -t jamrizzi/dockplicity-cron:latest -f $(CWD)/dockplicity-cron/Dockerfile $(CWD)/dockplicity-cron
	$(info built dockplicity cron)


## PUSH ##
.PHONY: push
push: push_dockplicity_backup push_dockplicity_cron

.PHONY: push_dockplicity_backup
push_dockplicity_backup:
	docker push jamrizzi/dockplicity-backup:latest
	$(info pushed dockplicity backup)

.PHONY: push_dockplicity_cron
push_dockplicity_cron:
	docker push jamrizzi/dockplicity-cron:latest
	$(info pushed dockplicity cron)


## CLEAN ##
.PHONY: clean
clean:
	$(info cleaned)


## FETCH DEPENDANCIES ##
.PHONY: fetch_dependancies
fetch_dependancies: docker
	$(info fetched dependancies)

.PHONY: docker
docker:
ifeq ($(shell whereis docker), $(shell echo docker:))
	curl -L https://get.docker.com/ | bash
endif
	$(info fetched docker)
