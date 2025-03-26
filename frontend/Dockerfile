# Utiliser l'image officielle de Nginx
FROM nginx:latest

# copie les fichiers de dist/aquadash/browser dans un fichier release
COPY ./dist/aquadash/browser /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose le port 80
EXPOSE 80

