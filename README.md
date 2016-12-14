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

## Actions

### Cron
This action backups volumes automatically. The container runs in the background as a daemon.
```sh
docker run -d \
  -v /my/awsome/volume:/volumes/my-awsome-volume \
  -e GS_ACCESS_KEY_ID=gs-access-key-id \
  -e GS_SECRET_ACCESS_KEY=gs-secret-access-key \
  -e TARGET_URL=gs://my-google-bucket \
  jamrizzi/dockplicity:latest
```

## Backup
This action runs a singe backup. The container will exit after it is finished running the backup.
```sh
docker run -rm \
  -v /my/awsome/volume:/volumes/my-awsome-volume \
  -e ACTION=backup \
  -e GS_ACCESS_KEY_ID=gs-access-key-id \
  -e GS_SECRET_ACCESS_KEY=gs-secret-access-key \
  -e TARGET_URL=gs://my-google-bucket \
  jamrizzi/dockplicity:latest
```

## Restore
This action restores a backup. The container will exit after it is finished running the restore.
```sh
docker run -rm \
  -v /my/awsome/volume:/volumes/my-awsome-volume \
  -e ACTION=restore \
  -e GS_ACCESS_KEY_ID=gs-access-key-id \
  -e GS_SECRET_ACCESS_KEY=gs-secret-access-key \
  -e TARGET_URL=gs://my-google-bucket \
  jamrizzi/dockplicity:latest
```

## Options
* ACTION=cron - Action to take when run (cron|backup|restore)
* TARGET_URL="gs://my_google_bucket" - Used to reference where backups will be stored
* BACKUP_DIR=/volumes - The directory of volumes that will be backed up

The following options depend on the action specified.

#### Cron
* CRON_SCHEDULE="0 0 0 * * &ast;" - The frequency backups run

#### Cron or Backup
* PASSPHRASE=hellodocker - The passphrase used to encrypt your backups
* MAX_TIME=1Y - The maximum amount of time backups are kept (format as time)
* FULL_MAX_COUNT=3 - The maximum number of full backups kept
* INCR_MAX_COUNT=30 - The maximum number of incremental backups kept
* FULL_IF_OLDER_THAN=1Y - Run a full backup if older than time (format as time)
* ALLOW_SOURCE_MISMATCH=false - Don't abort attempts using the same target url to back up different volumes

#### Restore
* RESTORE_VOLUME=myvolumename - If set, restores a single volume instead of restoring all volumes
* FORCE=false - Forces the restore to write over existing volumes

## Time Formats
_Dockplicity uses the same time format as duplicity.  The following infomations was taken from [http://duplicity.nongnu.org/duplicity.1.html](http://duplicity.nongnu.org/duplicity.1.html)._

Time can be given in any of several formats:
* The string "now" (refers to the current time)
* A sequences of digits, like "123456890" (indicating the time in seconds after the epoch)
* A string like "2002-01-25T07:00:00+02:00" in datetime format
* An interval, which is a number followed by one of the characters s, m, h, D, W, M, or Y (indicating seconds, minutes, hours, days, weeks, months, or years respectively), or a series of such pairs. In this case the string refers to the time that preceded the current time by the length of the interval. For instance, "1h78m" indicates the time that was one hour and 78 minutes ago. The calendar here is unsophisticated: a month is always 30 days, a year is always 365 days, and a day is always 86400 seconds.
* A date format of the form YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY, which indicates midnight on the day in question, relative to the current time zone settings. For instance, "2002/3/5", "03-05-2002", and "2002-3-05" all mean March 5th, 2002.

## Future Plans
* Database dumping before backups
* Automatic backup when change detected

## Documentation
[Official Duplicity Docs](http://duplicity.nongnu.org/duplicity.1.html)

## Credit
* [Jam Risser](https://github.com/jamrizzi)
* [Duplicity](http://duplicity.nongnu.org/)
