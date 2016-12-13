# dockplicity _Alpha_
A robust backup solution for Docker volumes with duplicity

### [jamrizzi/dockplicity:latest](https://hub.docker.com/r/jamrizzi/dockplicity/)

## Features
* Automatic backups
* Individual docker volume restores
* Incremental backups
* Automatic cleanup
* Backup encryption
* Two dozen supported backup stores
* Backup diffing

## Installation
```sh
docker run -d \
  -v /my/awsome/volume:/volumes/my-awsome-volume \
  -e GS_ACCESS_KEY_ID=gs-access-key-id \
  -e GS_SECRET_ACCESS_KEY=gs-secret-access-key \
  -e TARGET_URL=gs://my-google-bucket \
  jamrizzi/dockplicity:latest
```

## Future Plans
* Database dumping before backups
* Automatic backup when change detected

## Documentation
[Official Duplicity Docs](https://linux.die.net/man/1/duplicity)
