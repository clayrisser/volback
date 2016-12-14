#!/bin/bash

if [ "$ACTION" == "backup" ]; then # single backup
    bash /scripts/backup.sh
elif [ "$ACTION" == "restore" ]; then # single restore
    bash /scripts/restore.sh
else # backup cron
    touch /var/log/cron.log
    go-cron "$CRON_SCHEDULE" bash /scripts/cron.sh >> /var/log/cron.log
    tail -f /var/log/cron.log
fi
