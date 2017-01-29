CWD := $(shell readlink -en $(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))

.PHONY: all
all: fetch_dependancies build sweep push
.PHONY: ident_backup
ident_backup: fetch_dependancies build_ident_backup sweep push_ident_backup
.PHONY: ident_restore
ident_restore: fetch_dependancies build_ident_restore sweep push_ident_restore
.PHONY: ident
ident: fetch_dependancies build_ident sweep push_ident

.PHONY: build
build: build_ident_backup build_ident_restore build_ident
.PHONY: build_ident_backup
build_ident_backup:
	docker pull jamrizzi/ident-backup
	cp -r ./config ./ident-backup/config
	cp -r ./shared/* ./ident-backup/src/
	docker build -t jamrizzi/ident-backup:latest -f $(CWD)/ident-backup/Dockerfile $(CWD)/ident-backup
	$(info built ident-backup)
.PHONY: build_ident_restore
build_ident_restore:
	docker pull jamrizzi/ident-restore
	cp -r ./config ./ident-restore/config
	cp -r ./shared/* ./ident-restore/src/
	docker build -t jamrizzi/ident-restore:latest -f $(CWD)/ident-restore/Dockerfile $(CWD)/ident-restore
	$(info built ident-restore)
build_ident:
	docker pull jamrizzi/ident
	cp -r ./config ./ident/config
	docker build -t jamrizzi/ident:latest -f $(CWD)/ident/Dockerfile $(CWD)/ident
	$(info built ident)

.PHONY: push
push: push_ident_backup push_ident_restore push_ident
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

.PHONY: clean
clean: sweep bleach
	$(info cleaned)
.PHONY: sweep
sweep:
	@rm -rf ident-backup/backup/*.pyc
	@rm -rf ident-restore/config ident-backup/config ident/config
	@rm -f ident-restore/src/helper.py ident-backup/src/helper.py
	$(info swept)
.PHONY: bleach
bleach:
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
