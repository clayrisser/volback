# ident _Beta_
A robust backup solution for Docker volumes

### [jamrizzi/ident:latest](https://hub.docker.com/r/jamrizzi/ident/)

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
  -v /backup:/backup \
  -e CRON_SCHEDULE="0 0 * * *" \
  jamrizzi/ident:latest
```

## Backup
This will run a single backup for all your containers.
```sh
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /backup:/backup \
  jamrizzi/ident:latest backup
```

## Restore
This will restore all backed up volumes for a single service or container.
```sh
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /backup:/backup \
  -e SERVICE="my-service-name" \
  jamrizzi/ident:latest restore
```

## Options
* __CRON_SCHEDULE="0 0 0 &ast; &ast; &ast;"__ - the frequency backups run
  * Note that this cron schedule is based on seconds, not minutes.
  * It is strongly advised not to set the cron lower than "0 &ast; &ast; &ast; &ast; &ast;"
* __PASSPHRASE=hellodocker__ - the passphrase used to encrypt your backups
* __ENCRYPT=false__ - if set to true, will encrypt backups with the passphrase
* __TIME=now__ - restore backup from specified time (format as unix timestamp)

## Future Plans
* Automatic backup when change detected
* Notifications
* Management portal

## Error/Bugs/Features
You can file error and bug reports as well as feature requests at [https://github.com/jamrizzi/dockplicity/issues](https://github.com/jamrizzi/dockplicity/issues).

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Credit
* Created by [Jam Risser](https://github.com/jamrizzi)
* Powered by [Borg](https://borgbackup.readthedocs.io/en/stable/)
