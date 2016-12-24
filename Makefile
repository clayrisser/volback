CWD := $(shell readlink -en $(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))


.PHONY: all
all: fetch_dependancies build push

.PHONY: dockplicity_backup
dockplicity_backup: fetch_dependancies build_dockplicity_backup push_dockplicity_backup

.PHONY: dockplicity_restore
dockplicity_restore: fetch_dependancies build_dockplicity_restore push_dockplicity_restore

.PHONY: dockplicity
dockplicity: fetch_dependancies build_dockplicity push_dockplicity


## BUILD ##
.PHONY: build
build: build_dockplicity_backup build_dockplicity_restore build_dockplicity

.PHONY: build_dockplicity_backup
build_dockplicity_backup:
	docker build -t jamrizzi/dockplicity-backup:latest -f $(CWD)/dockplicity-backup/Dockerfile $(CWD)/dockplicity-backup
	$(info built dockplicity-backup)

.PHONY: build_dockplicity_restore
build_dockplicity_restore:
	docker build -t jamrizzi/dockplicity-restore:latest -f $(CWD)/dockplicity-restore/Dockerfile $(CWD)/dockplicity-restore
	$(info built dockplicity-restore)

.PHONY: build_dockplicity
build_dockplicity:
	docker build -t jamrizzi/dockplicity:latest -f $(CWD)/dockplicity/Dockerfile $(CWD)/dockplicity
	$(info built dockplicity)


## PUSH ##
.PHONY: push
push: push_dockplicity_backup push_dockplicity_restore push_dockplicity

.PHONY: push_dockplicity_backup
push_dockplicity_backup:
	docker push jamrizzi/dockplicity-backup:latest
	$(info pushed dockplicity backup)

.PHONY: push_dockplicity_restore
push_dockplicity_restore:
	docker push jamrizzi/dockplicity-restore:latest
	$(info pushed dockplicity-restore)

.PHONY: push_dockplicity
push_dockplicity:
	docker push jamrizzi/dockplicity:latest
	$(info pushed dockplicity)


## CLEAN ##
.PHONY: clean
clean:
	docker stop $(docker ps -a -q)
	docker rm -f $(docker ps -a -q)
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
