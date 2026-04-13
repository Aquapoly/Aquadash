# Aquadash

The app is normally accessible via http://localhost.

## Environment and Settings

Building the project once will create the necessary configuration files if they don't exist.

You can also create them manually by copying the example files:

```bash
cp src/app/environment.example.ts src/app/environment.ts
cp src/app/app-settings.example.ts src/app/app-settings.ts
```

If you want to deploy this app, you will need to modify the `SERVER_URL` in `src/app/environment.ts` to point to your backend server. For example:

```ts
export const SERVER_URL = "http://192.168.1.100:8000";
```

You can also modify the values in `app-settings.ts` to fit your needs. Otherwise, the defaults will give you a working setup.

## Development

- **Start dev server:** Run `npm start` (this runs `ng serve`).
- **URL:** http://localhost:4200/
- **API endpoint for development:** edit `src/app/environment.ts` and set `SERVER_URL` for backend (default: `http://localhost:8000`).

## Build

- **Build:** `npm run build` (artifacts are produced under `dist/aquadash/`).

## Deploy (static)

- Use the repository helper `deploy.sh` to build and copy static files to the host webroot:

```bash
sudo ./deploy.sh
```

This runs `npm run build` and copies `dist/aquadash/browser/*` into `/var/www/aquadash`.

## Deploy (Docker)

- Use `launch-docker.sh` to build a production artifact and run the Docker image locally:

```bash
./launch-docker.sh
```

This script runs `npm ci`, `npm run build`, builds the Docker image and runs it (`docker run -p 80:80`). It is focused on container run and does not modify the host webroot.

## Dependencies

- **Node.js:** recommended LTS (use NodeSource or `nvm` to install per your OS).
- **npm:** bundled with Node.js. Use the bundled or a managed upgrade (avoid global `npm -g npm` in scripts).
- **Angular CLI:** only required to build locally or run `ng` commands.
- **Docker (optional):** only required if you intend to build/run the Docker image.

## Provisioning / installer scripts

- There is an optional provisioning script in the repository (`install-dependencies.sh` / `install-softwares.sh`) that attempts to install system packages (apt, Docker, Node, Angular CLI, etc.). **This script is not required to develop or deploy the frontend** and may be unsafe or incompatible with some systems (e.g., non-apt package managers, managed servers). Treat it as an optional, host-specific helper and review it before running.

- Recommended approach for new machines:
  - Use `nvm` to install Node.js per-user instead of system `apt` packages.
  - Use Docker only if you want containerized deployment; otherwise copy `dist/aquadash/browser/*` to your web host.

## Summary

- For development: `npm start`.
- For production (static): `sudo ./deploy.sh`, or build the Docker image as shown above.
