#!/bin/bash

if [ "$COMMAND" == "backup" ]; then
    echo Running backup . . .
    python /docker/src/backup.py
elif [ "$COMMAND" == "restore" ]; then
    echo Running restore . . .
    python /docker/src/restore.py
else
    go-cron "$CRON_SCHEDULE" python /docker/src/backup.py >> /docker/cron.log
fi
