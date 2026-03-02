# Overview

The backend is divided into two components: the **app stack**, and the **camera block**.

![Overview diagram of Aquadash architecture](resources/aquadash-architecture-overview.drawio.svg "Overview of Aquadash Architecture")

---

The **app stack** is the principal component. It is entirely composed of Docker containers. Launching the **app stack** corresponds to executing:

```bash
./run app
```

---

The **camera block** is an optional component. It spans the host and a Docker container. Together, they can expose camera devices from the host to the app stack. Launching the **camera block** corresponds to executing:

```bash
./run cam
```

---

Launching all components of Aquadash corresponds to executing:

```bash
./run all
```

---

# App Stack

The **app stack** is composed of the `app` container, and the `db` container.

![The Aquadash app stack diagram](resources/aquadash-architecture-app_stack.drawio.svg "The Aquadash App Stack")

This system provides the core functionality of Aquadash. While it is running, the application's public API will be available at `host:8000`.

## Container: `app`

The `app` container is the logical core of Aquadash. Outside of camera functionality, it contains all business logic.

It exposes a public HTTP request API which is exposed at `host:8000`. Most requests will have `app` act on or fetch the data stored in the `db` container.

All camera-related requests are forwarded to the **camera block**'s API through the connection said block exposes at `:9000` over the `backend` secure Docker network.

## Container: `db`

The `db` container is a PostgreSQL database which is available over the `backend` secure Docker network at `:5432`.

It is intended to be accessed and mutated by the `app` container. It stores data relating to actuators, sensors, etc.

# Camera Block

This subsystem is composed of the `cam-client` container, and the host service `camera-daemon`.

![The Aquadash camera block diagram](resources/aquadash-architecture-camera_block.drawio.svg "The Aquadash Camera Block")

The **camera block** also makes use of the named Docker volume `timelapse_data`, exposed as `/timelapses`, which allows timelapses to persist even when the block is rebooted.

Apart from enabling camera functionality for Aquadash, the goal of this block is to decouple camera logic from the **app stack**. It opens the possibility for the latter to run completely free of `cam-client` and, most importantly, of the dependency on the host service `camera-daemon`.

## Service: `camera-daemon`

The `camera-daemon` service is a host systemd-managed service. Its responsability is to expose camera devices from the host as logical cameras accessible by `cam-client`.

The service creates a runtime directory at `/run/camera` upon starting. There, it will expose logical cameras as Unix sockets. Running the basic `run cam` command will launch the service with a single camera as specified in `.env`.

The goal of the service is to create a layer of abstraction between Docker (i.e. `cam-client`) and the physical devices of the host. The Docker container is able to mount on a logical camera socket, notwithstanding the actual existence of a physical camera at the other hand.

This unlocks the potential for hot-plugging or hot-rewiring cameras, and also supports multiple logical camera channels.

It also serves to increase security. Indeed, it only allows camera access to a narrow group of users, of which `cam-client` is, a priori, the only member (excluding root), and from the perspective of Docker, only over a socket with a specific communication protocol.

More detailed documentation on `camera-daemon` is available [here](devices/camera/README.md).

## Container: `cam-client`

This container is mainly responsible for fetching camera frames through a Unix socket managed by `camera-daemon`. It is part of the `host-dev` user group, which is instantiated by `camera-daemon` at installation, and as such has the necessary permissions.

It listens on port `:9000` over the `backend` secure Docker network, and there exposes a public HTTP API for producing camera frames and managing timelapses.

It stores timelapses in the `timelapse_data` volume (as `/timelapses` internally) in order for them to persist through shutdowns — you wouldn't want to lose an entire 7-day timelapse to a service outage!

It makes use of `/tmp/timelapses` to temporarily store timelapse frames when assembling a video from them.
