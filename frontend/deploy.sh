#!/bin/bash
npm run build && \
sudo rm -rf /var/www/aquadash && \
sudo mkdir -p /var/www/aquadash && \
sudo cp -r dist/aquadash/* /var/www/aquadash/
