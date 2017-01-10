# dockplicity _Beta_
A robust backup solution for Docker volumes with duplicity

### [jamrizzi/dockplicity:latest](https://hub.docker.com/r/jamrizzi/dockplicity/)

## Features
* Restore individual docker volumes
* Works with docker volume drivers
* Automatic backups
* Data deduplication
* Clear outdated backups
* Backup encryption

## Usage

### Cron
This will backup volumes automatically every day.
```sh
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e CRON_SCHEDULE="0 0 0 * * *" \
  -e STORAGE_URL="gs://my-google-bucket" \
  -e STORAGE_ACCESS_KEY_ID=gs-access-key-id \
  -e STORAGE_SECRET_ACCESS_KEY=gs-secret-access-key \
  jamrizzi/dockplicity:latest
```

## Backup
This will run a singe backup.
```sh
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e STORAGE_URL="gs://my-google-bucket" \
  -e STORAGE_ACCESS_KEY_ID=gs-access-key-id \
  -e STORAGE_SECRET_ACCESS_KEY=gs-secret-access-key \
  jamrizzi/dockplicity:latest backup
```

## Restore
This will restore all backed up volumes.
```sh
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e STORAGE_URL="gs://my-google-bucket" \
  -e STORAGE_ACCESS_KEY_ID=gs-access-key-id \
  -e STORAGE_SECRET_ACCESS_KEY=gs-secret-access-key \
  jamrizzi/dockplicity:latest restore
```

## Options
* __CRON_SCHEDULE="0 0 0 &ast; &ast; &ast;"__ - the frequency backups run
  * Note that this cron schedule is based on seconds, not minutes.
  * It is strongly advised not to set the cron lower than "0 &ast; &ast; &ast; &ast; &ast;"
* __PASSPHRASE=hellodocker__ - the passphrase used to encrypt your backups
* __ENCRYPT=false__ - if set to true, will encrypt backups with the passphrase
* __RESTORE_VOLUME=myvolumename__ - if set, restores a single volume instead of restoring all volumes
* __TIME=now__ - restore backup from specified time (format as unix timestamp)

## Future Plans
* Automatic backup when change detected

## Error/Bugs/Features
You can file error and bug reports as well as feature requests at [https://github.com/jamrizzi/dockplicity/issues](https://github.com/jamrizzi/dockplicity/issues).

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Credit
* [Jam Risser](https://github.com/jamrizzi)
