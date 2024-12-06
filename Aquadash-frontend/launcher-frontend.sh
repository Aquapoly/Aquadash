#!/bin/bash  

npm install
npm run build
sudo rm -rf /var/www/aquadash  
sudo cp -r dist/aquadash /var/www/aquadash

sudo docker build -t aquadash .
sudo docker run -p 80:80 aquadash