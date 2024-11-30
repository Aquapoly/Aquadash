#!/bin/bash

# Directory containing files to make executable
DEPLOY_DIR="./deploy"

# Check if the directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
  echo "Directory $DEPLOY_DIR does not exist!"
  exit 1
fi

# Iterate through all files in the deploy directory
for file in "$DEPLOY_DIR"/*; do
  if [ -f "$file" ]; then
    # Make the file executable
    chmod +x "$file"
    echo "Made $file executable"
  fi
done

echo "All files in $DEPLOY_DIR are now executable."

# Get the current directory
CURRENT_DIR=$(pwd)
echo "Current directory detected: $CURRENT_DIR"

# Directory containing the crontab files
CRONTAB_DIR="crontab"

# Check if the directory exists
if [[ ! -d $CRONTAB_DIR ]]; then
  echo "Error: Directory '$CRONTAB_DIR' not found."
  exit 1
fi

# Iterate through all files in the directory
for FILE in "$CRONTAB_DIR"/*
do
  # Skip files with .disable extension
  if [[ "$FILE" =~ \.disable$ ]]; then
    echo "Skipping disabled file: $FILE"
    continue
  fi

  # Replace the path in the file
  echo "Updating file: $FILE"
  sed -i "s|/home/aquapoly/Aquadash/Sensors|$CURRENT_DIR|g" "$FILE"
done

echo "All crontab files updated with the current directory: $CURRENT_DIR"

./deploy/enable-actuator.sh
./deploy/enable-crontab-jobs.sh

echo "Configuration of the sensors and te actuator is done"
