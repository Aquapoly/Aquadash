#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib-crontab.sh"

cd /opt/aquadash/sensors

FILES=""
fileCount=0

for entry in crontab/*
do
  # Les fichiers avec une extension .disable ne sont pas rajoutés au crontab
  if [[ ! "$entry" =~ \.disable$ ]]
  then
    FILES+="$entry "
    echo "File added: $entry"
    fileCount+=1
  fi
done

if [[ $fileCount -gt 0 ]]
then
  echo "Update crontab"
  NEW_JOBS="$(cat $FILES)"

  aquadash_crontab_install_jobs "$NEW_JOBS"

  echo "Done"
else
  echo "No enabled crontab file found."
fi
