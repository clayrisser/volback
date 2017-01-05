#!/bin/bash

if [ "$COMMAND" == "backup" ]; then
    python /docker/src/backup.py
elif [ "$COMMAND" == "restore" ]; then
    python /docker/src/restore.py
else
    go-cron "$CRON_SCHEDULE" python /docker/src/backup.py >> /docker/cron.log
fi
