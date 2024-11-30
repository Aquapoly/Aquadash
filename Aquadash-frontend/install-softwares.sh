#!/bin/bash 

# Update the package list
set -e

clear

echo "Bienvenue sur Aquadash"
echo " "
echo "Entrez votre mot de passe pour commencer l'installation"

sudo clear
echo "Début de l'installation. Cela devrait prendre quelques minutes"
echo "Des messages vont s'afficher dans le terminal sous peu, ne pas s'en inquiéter"
sleep 4

sudo apt update -y

# Install Python
echo "Installing Python..."
sudo apt install python3 -y

# Install Systemd
echo "Ensuring systemd is installed..."
sudo apt install systemd -y

# Install Docker and Docker Compose
echo "Installing curl..."
sudo apt install curl -y
echo "Downloading and installing Docker..."
curl -fsSL test.docker.com -o get-docker.sh && sh get-docker.sh
echo "Installing Docker Compose..."
sudo apt install docker-compose -y


python3 -m venv .venv

clear 

echo "Installation réussie, il est conseillé de redémarer la machine avant de continuer"

while true; do
    read -r -p "Voulez vous redémarer maintenant? (O/n) " answer
    case $answer in
        [oO]* ) clear ;echo "Redémarage..."; sleep 5; reboot; break;;
        [Nn]* ) exit;;
        * ) echo "Veuiller entrer O ou N s'il vous plait";;
    esac
done
