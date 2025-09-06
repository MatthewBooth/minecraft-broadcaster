# Minecraft Broadcaster

Minecraft Broadcaster periodically sends LAN server announcements over IPv4 multicast. It advertises each configured server MOTD and port to the local network; it does not host a Minecraft server.

## Requirements

- Python 3.13 or later, or Docker with Compose
- A host and network that allow IPv4 multicast

The broadcaster sends to `224.0.2.60:4445` with multicast TTL 1, keeping announcements on the local network.

## Configure

Each broadcast uses the format `MOTD|PORT`. Separate multiple broadcasts with commas when using the `BROADCASTS` environment variable. Ports must be in the range `1–65535`.

| Setting                      | Purpose                                | Default                              |
|------------------------------|----------------------------------------|--------------------------------------|
| `BROADCASTS`                 | Comma-separated `MOTD \| PORT` entries | None; at least one entry is required |
| `BROADCAST_INTERVAL_SECONDS` | Delay between announcement rounds      | `1`                                  |

For example:

```text
BROADCASTS="Creative Server|25565,Survival Server|25555"
BROADCAST_INTERVAL_SECONDS=1
```

Invalid entries are skipped with a warning. An empty list or invalid interval stops startup with an error.

## Run with Docker Compose

Copy the sample configuration to Compose's `.env` file, edit it, and start the service:

```sh
cp .env.dist .env
# Edit .env to set your MOTDs, ports, and interval.
docker compose up -d --build
```

Compose uses host networking so multicast announcements can reach the LAN. Follow the logs with `docker compose logs -f`; stop the service with `docker compose down`.

## Run from Python

Install the project and its command-line entry point:

```sh
python -m pip install .
minecraft-broadcaster --broadcast 'Creative Server|25565' --broadcast 'Survival Server|25555' --interval 1
```

Or run the script directly:

```sh
python broadcast.py --broadcast 'Creative Server|25565' --interval 1
```

`--broadcast` can be repeated. If no CLI options are supplied, the program reads `BROADCASTS` and `BROADCAST_INTERVAL_SECONDS` from the environment. Explicit CLI options take precedence over those environment values. Run `minecraft-broadcaster --help` for option details.

## Run the published container

Images are published to `ghcr.io/mattboothdev/minecraft-broadcaster`. The package must be public for anonymous pulls. Tags are generated as follows:

| Build source | Image tags |
| --- | --- |
| Push to `master` | `dev`, full commit SHA |
| Push to `develop` | `develop`, full commit SHA |
| Version tag such as `v1.2.3` | `latest`, `1.2.3`, `1.2`, `1`, full commit SHA |

Pull requests run the checks and build the image without publishing it. Workflow dispatch builds and publishes the image using the tags available for the selected ref.

```sh
docker run -d --name minecraft-broadcaster \
  --restart unless-stopped \
  --network host \
  -e 'BROADCASTS=Creative Server|25565,Survival Server|25555' \
  -e BROADCAST_INTERVAL_SECONDS=1 \
  ghcr.io/mattboothdev/minecraft-broadcaster:latest
```

The container also accepts CLI options after the image name:

```sh
docker run -d --name minecraft-broadcaster --restart unless-stopped --network host \
  ghcr.io/mattboothdev/minecraft-broadcaster:latest \
  --broadcast 'Creative Server|25565' --interval 1
```

## Development

Install development dependencies, run the tests, and check style and formatting:

```sh
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
```

GitHub Actions runs these checks on pull requests, pushes to `master` or `develop`, version tags, and manual workflow runs. Images are built after checks pass; pull requests do not publish images.

## Contributing

Contributions are welcome. Create a feature branch from `master`, make and commit your changes there, then open a pull request targeting `master`. GitHub Actions runs the test, lint, and formatting checks on pull requests and pushes to `master` or `develop`; run them locally before opening your pull request.
