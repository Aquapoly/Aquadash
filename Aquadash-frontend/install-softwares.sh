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

# Mettre a jour les depots
echo "Mise a jour des depots..."
sudo apt update && sudo apt upgrade -y

# Installer Node.js (et npm inclus)
echo "Installation de Node.js..."
sudo apt install -y nodejs

# Verifier si npm est installee, sinon l'installer
if ! command -v npm &> /dev/null; then
  echo "npm non trouve, installation de npm..."
  sudo apt install -y npm
fi

# Mettre a jour npm a la derniere version
echo "Mise a jour de npm..."
sudo npm install -g npm@latest -y

# Installer Angular CLI globalement
echo "Installation d'Angular CLI..."
sudo npm install -g @angular/cli -y

# Verifier les installations
echo "Verifications des versions installees :"
echo -n "Node.js version : "; nodejs --version
echo -n "npm version : "; npm --version
echo -n "Angular CLI version : "; ng version

# Instructions finales
echo "Installation terminee. Tu peux maintenant executer 'npm run build' dans ton projet Angular."

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
