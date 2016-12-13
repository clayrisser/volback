#!/bin/bash

if [ $RESTORE_VOLUME ]; then
    _RESTORE_VOLUME="--file-to-restore $RESTORE_VOLUME "
fi
if [ "$FORCE" == "true" ]; then
    _FORCE="--force "
fi

eval "(echo $PASSPHRASE) | duplicity ""restore ""$_RESTORE_VOLUME""$_FORCE""--time $RESTORE_TIME $TARGET_URL $BACKUP_DIR/$RESTORE_VOLUME"
