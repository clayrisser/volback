#!/bin/bash

if [ "$ALLOW_SOURCE_MISMATCH" == "true" ]; then
    _ALLOW_SOURCE_MISMATCH="--allow-source-mismatch "
fi

eval "(echo $PASSPHRASE; echo $PASSPHRASE) | duplicity ""$BACKUP_TYPE ""$_ALLOW_SOURCE_MISMATCH""--full-if-older-than $FULL_IF_OLDER_THAN $BACKUP_DIR $TARGET_URL"

bash /scripts/clean.sh
