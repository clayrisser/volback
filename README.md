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
  -e TARGET_URL="gs://my-google-bucket" \
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
  -e TARGET_URL="gs://my-google-bucket" \
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
* __ACTION=cron__ - Action to take when run (cron|backup|restore)
* __TARGET_URL="gs://my_google_bucket"__ - Used to reference where backups will be stored
* __BACKUP_DIR=/volumes__ - The directory of volumes that will be backed up

__The following options depend on the action specified.__

#### Cron
* __CRON_SCHEDULE="0 0 0 &ast; &ast; &ast;"__ - The frequency backups run
  * Note that this cron schedule is based on seconds, not minutes.
  * It is strongly advised not to set the cron lower than "0 &ast; &ast; &ast; &ast; &ast;"

#### Cron or Backup
* __PASSPHRASE=hellodocker__ - The passphrase used to encrypt your backups
* __MAX_TIME=1Y__ - The maximum amount of time backups are kept (format as time)
* __FULL_MAX_COUNT=3__ - The maximum number of full backups kept
* __INCR_MAX_COUNT=30__ - The maximum number of incremental backups kept
* __FULL_IF_OLDER_THAN=1Y__ - Run a full backup if older than time (format as time)
* __ALLOW_SOURCE_MISMATCH=false__ - Don't abort attempts using the same target url to back up different volumes

#### Restore
* __RESTORE_VOLUME=myvolumename__ - If set, restores a single volume instead of restoring all volumes
* __FORCE=false__ - Forces the restore to write over existing volumes

## Time Formats
_Dockplicity uses the same time format as duplicity.  The following infomations was taken from [http://duplicity.nongnu.org/duplicity.1.html](http://duplicity.nongnu.org/duplicity.1.html)._

Time can be given in any of several formats:
* The string "now" (refers to the current time)
* A sequences of digits, like "123456890" (indicating the time in seconds after the epoch)
* A string like "2002-01-25T07:00:00+02:00" in datetime format
* An interval, which is a number followed by one of the characters s, m, h, D, W, M, or Y (indicating seconds, minutes, hours, days, weeks, months, or years respectively), or a series of such pairs. In this case the string refers to the time that preceded the current time by the length of the interval. For instance, "1h78m" indicates the time that was one hour and 78 minutes ago. The calendar here is unsophisticated: a month is always 30 days, a year is always 365 days, and a day is always 86400 seconds.
* A date format of the form YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY, which indicates midnight on the day in question, relative to the current time zone settings. For instance, "2002/3/5", "03-05-2002", and "2002-3-05" all mean March 5th, 2002.

## Backup Stores
There are over two dozon supported backup stores. More documentation on them can be found at the following link.
[http://duplicity.nongnu.org/duplicity.1.html](http://duplicity.nongnu.org/duplicity.1.html)

### Google Cloud Storage
This is the backup store used in all of the dockplicity examples. To use this backup store, follow the instructions below.
1. Enable interoperable access - [https://code.google.com/apis/console#:storage](https://code.google.com/apis/console#:storage)
2. Create access keys: [https://code.google.com/apis/console#:storage:legacy](https://code.google.com/apis/console#:storage:legacy)
3. Set the following environment variables
* __GS_ACCESS_KEY_ID=gs-access-key-id__
* __GS_SECRET_ACCESS_KEY=gs-secret-access-key__
* __TARGET_URL="gs://my-google-bucket"__

### DropBox
1. Create Dropbox API application - [https://www.dropbox.com/developers/apps/create](https://www.dropbox.com/developers/apps/create)
Then visit app settings and just use ’Generated access token’ under OAuth2 section.
2. Set the following environment variables.
* __DPBX_ACCESS_TOKEN=dpbx-access-token__
* __TARGET_URL="dpbx:///some_dir"__

* Note that all files will be synced to all connected computers. You may prefer to use a separate Dropbox account specially for the backups, and not connect any computers to that account. Alternatively, you can configure selective sync on all computers to avoid syncing of backup files.

## Future Plans
* Database dumping before backups
* Automatic backup when change detected

## Error/Bugs/Features
You can file error and bug reports as well as feature requests at [https://github.com/jamrizzi/dockplicity/issues](https://github.com/jamrizzi/dockplicity/issues).

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Documentation
[Official Duplicity Docs](http://duplicity.nongnu.org/duplicity.1.html)

## Credit
* [Jam Risser](https://github.com/jamrizzi)
* [Duplicity](http://duplicity.nongnu.org/)
