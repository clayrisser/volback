#!/bin/bash

if [ "$TYPE" == "backup" ]; then # single backup
    bash /scripts/backup.sh
elif [ "$TYPE" == "restore" ]; then # single restore
    bash /scripts/restore.sh
else # backup cron
    touch /var/log/cron.log
    go-cron "$BACKUP_CRON" bash /scripts/cron.sh >> /var/log/cron.log
    tail -f /var/log/cron.log
fi
