#!/bin/bash

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

if [[ fileCount -gt 0 ]]
then
  echo "Update crontab"
  cat $FILES | crontab
  echo "Done"
else
  echo "No enabled crontab file found."
fi