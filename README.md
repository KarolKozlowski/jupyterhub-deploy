# JupyterHub Deploy

Containerized JupyterHub setup with OAuth (Generic OIDC), DockerSpawner, GPU support, and idle culling.

## What’s included

- JupyterHub image based on quay.io/jupyterhub/jupyterhub:5.4.3
- OAuth via GenericOAuthenticator (OIDC)
- DockerSpawner with per-user containers on a dedicated Docker network
- Optional GPU access via NVIDIA device requests
- Idle culler service
- Docker socket proxy for safer Docker API access

## Prerequisites

- Docker Engine and Docker Compose
- NVIDIA Container Toolkit (only if you need GPU support)
- OIDC provider (Authentik/Keycloak/Entra/Okta/etc.)

## Files

- docker-compose.yml – runs JupyterHub and docker-socket-proxy
- Dockerfile – builds the JupyterHub image with required Python packages
- jupyterhub_config-example.py – sample JupyterHub configuration
- Makefile – local build/test/run helpers

## Configuration

1. Copy the example configuration and adjust settings:
   - Create /share/www/jupyterhub/config/jupyterhub_config.py from jupyterhub_config-example.py
   - Replace OIDC endpoints, client ID/secret, callback URL
   - Review group/role settings and allowed/admin groups

2. Ensure the following directories exist on the host (as per docker-compose.yml and config):
   - /share/www/jupyterhub/config (read-only config for Hub)
   - /share/db/jupyterhub/config (state/secrets)
   - /share/db/jupyterhub/users/{username}/jovyan (home)
   - /share/homes/{username}/jupyter (work)

3. If you need GPUs, keep the NVIDIA device request in the config and ensure NVIDIA runtime is installed.

## Build and run (local)

- Build image: use the Makefile target build
- Test image: use the Makefile target test
- Run image: use the Makefile target run

## Deploy with Docker Compose

1. Set the image in docker-compose.yml (default points to registry.np.dotnot.pl/ghcr.io/karolkozlowski/jupyterhub-deploy/jupyterhub:latest)
2. Start services using Docker Compose
3. JupyterHub is exposed at 172.30.0.1:21200

## Environment variables

- REGISTRY_PROXY: base registry proxy prefix used for ghcr.io, docker.io, and quay.io (default: registry.np.dotnot.pl/). Must end with a trailing slash.
- LOG_LEVEL: controls docker-socket-proxy logging verbosity (default: info; set to debug for verbose logs)

## Security notes

- Secrets are generated under /srv/jupyterhub and stored with 0600 permissions
- The Docker API is accessed through docker-socket-proxy with limited permissions
- Review all mounted paths and set correct host permissions before going live

## Customization tips

- Change user image via c.DockerSpawner.image
- Adjust resource limits via c.DockerSpawner.mem_limit and c.DockerSpawner.cpu_limit
- Update idle culler timeout in the c.JupyterHub.services section
- Change networking via docker-compose.yml and c.DockerSpawner.network_name

## License

MIT. See LICENSE.
