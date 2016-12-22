#!/bin/bash

duplicity remove-older-than $MAX_TIME --force "$TARGET_URL"
duplicity remove-all-but-n-full $FULL_MAX_COUNT --force "$TARGET_URL"
duplicity remove-all-inc-of-but-n-full $INCR_MAX_COUNT --force "$TARGET_URL"
duplicity cleanup --extra-clean --force "$TARGET_URL"
