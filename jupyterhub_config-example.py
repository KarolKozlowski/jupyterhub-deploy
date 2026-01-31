import os

c.JupyterHub.authenticator_class = "generic-oauth"

# OIDC provider details
c.GenericOAuthenticator.client_id = "YOUR_CLIENT_ID"
c.GenericOAuthenticator.client_secret = "YOUR_CLIENT_SECRET"
c.GenericOAuthenticator.oauth_callback_url = "https://your-jupyterhub-domain/hub/oauth_callback"

# OIDC endpoints (replace with your provider's URLs)
c.GenericOAuthenticator.authorize_url = "https://your-oidc-provider/protocol/openid-connect/auth"
c.GenericOAuthenticator.token_url = "https://your-oidc-provider/protocol/openid-connect/token"
c.GenericOAuthenticator.userdata_url = "https://your-oidc-provider/protocol/openid-connect/userinfo"

# Username claim from OIDC token
c.GenericOAuthenticator.username_claim = "preferred_username"
c.GenericOAuthenticator.login_service = "Your OIDC Provider"

# Group management
c.GenericOAuthenticator.manage_groups = True
c.GenericOAuthenticator.auth_state_groups_key = "groups"

# Admin and access control
c.GenericOAuthenticator.admin_groups = ['jupyterhub-admins']
c.GenericOAuthenticator.allowed_groups = ['jupyterhub-users', 'jupyterhub-admins']

# Set the spawner class to DockerSpawner
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Connect to docker-proxy via TCP
c.DockerSpawner.client_kwargs = {
    'base_url': 'tcp://docker-proxy:2375'
}

# Network configuration
network_name = 'jupyterhub-user-net'
c.DockerSpawner.network_name = network_name

# Container naming
c.DockerSpawner.prefix = 'jupyterhub'
c.DockerSpawner.name_template = '{prefix}-{username}'

# Docker image for user containers
c.DockerSpawner.image = 'registry.np.dotnot.pl/docker.io/jupyter/base-notebook:latest'

# Use internal IPs for communication
c.DockerSpawner.use_internal_ip = True

# Remove containers when they are stopped
c.DockerSpawner.remove = True

# Instead, ensure hub is accessible from spawned containers
c.JupyterHub.hub_ip = '0.0.0.0'  # Listen on all interfaces inside container

# Resource limits
c.DockerSpawner.mem_limit = '2G'
c.DockerSpawner.cpu_limit = 1.0

c.DockerSpawner.notebook_dir = '/home/jovyan/work'
c.DockerSpawner.volumes = {
    '/share/homes/{username}/jupyter/': '/home/jovyan/work'
}

# Define the idle culler service
c.JupyterHub.services = [
    {
        'name': 'jupyterhub-idle-culler-service',
        'command': [
            'python3',
            '-m',
            'jupyterhub_idle_culler',
            '--timeout=3600',  # Cull after 1 hour of inactivity
        ],
    }
]

# Define the role with permissions
c.JupyterHub.load_roles = [
    {
        "name": "jupyterhub-idle-culler-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "admin:servers",
        ],
        "services": ["jupyterhub-idle-culler-service"],
    }
]