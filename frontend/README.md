# Aquadash

Normalement l'application est accessible dans http://localhost

## Serveur de developpement 

Lancer `npm start` pour lancer le serveur de développement. Naviguer vers `http://localhost:4200/`. L'application se rechargera automatiquement si vous modifiez un fichier source. Pour un environement de développement veuillez également modifier le fichier environment.ts : `export const SERVER_URL="http://localhost:8000";`

## Build

Run `npm run build` to build the project. The build artifacts will be stored in the `dist/` directory.
Then move build files to `/var/www/aquadash` with the following command:
`sudo rm -rf /var/www/aquadash && sudo cp -r dist/aquadash /var/www/`

In one command:

`npm run build && sudo rm -rf /var/www/aquadash && sudo cp -r dist/aquadash /var/www/`

## Déploiement Docker
Lancer `docker build -t aquadash .` pour construire l'image docker. Lancer `docker run -p 80:80 aquadash` pour démarrer le conteneur docker. Naviguer vers `http://localhost/` pour accéder à l'application.
