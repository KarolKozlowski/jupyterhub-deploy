import os
from cryptography.fernet import Fernet

### --- common --- ###
# Function to load or create secret keys
def get_or_create_secret(key_name, base_dir='/srv/jupyterhub'):
    """
    Load or generate a secret key.

    Args:
        key_name: Name of the key (e.g., 'crypt_key', 'api_token')
        base_dir: Directory to store secrets

    Returns:
        The secret key as a string
    """
    secret_file = os.path.join(base_dir, f'{key_name}_secret')

    if os.path.exists(secret_file):
        # Load existing secret
        with open(secret_file, 'r') as f:
            return f.read().strip()
    else:
        # Generate new secret
        secret = Fernet.generate_key().decode()
        with open(secret_file, 'w') as f:
            f.write(secret)
        os.chmod(secret_file, 0o600)  # Secure permissions
        return secret


### --- JupyterHub OAuth configuration --- ###
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
# c.GenericOAuthenticator.auth_state_groups_key = "groups"
c.GenericOAuthenticator.claim_groups_key = "groups"

# Request scopes including offline_access for refresh tokens
c.GenericOAuthenticator.scope = ['openid', 'profile', 'email', 'offline_access']

# Enable auth_state and token refresh
c.GenericOAuthenticator.enable_auth_state = True
c.GenericOAuthenticator.refresh_pre_spawn = True
c.GenericOAuthenticator.auth_refresh_age = 300  # Refresh if older than 5 minutes

# Admin and access control
c.GenericOAuthenticator.admin_groups = ['jupyterhub-admins']
c.GenericOAuthenticator.allowed_groups = ['jupyterhub-users', 'jupyterhub-admins']

# Encryption key for auth_state
c.CryptKeeper.keys = [get_or_create_secret('crypt_key')]

### --- JupyterHub Custom Docker Spawner --- ###
# Custom Docker Spawner to set UID/GID from OAuth claims
from dockerspawner import DockerSpawner

class CustomDockerSpawner(DockerSpawner):
    async def start(self):
        # Clean up any existing container with this name first
        try:
            existing = await self.get_object()
            if existing:
                self.log.warning(f"Removing existing container {self.container_name}")
                await self.remove_object()
        except Exception as e:
            self.log.debug(f"No existing container to remove: {e}")

        # Get auth_state before starting
        auth_state = await self.user.get_auth_state()

        if auth_state:
            oauth_user = auth_state.get('oauth_user', {})

            # Extract UID/GID from OAuth claims
            uid = oauth_user.get('uid', '1000')
            gid = oauth_user.get('gid', '1000')

            # Set environment variables for the container
            self.environment['NB_UID'] = str(uid)
            self.environment['NB_GID'] = str(gid)
            self.environment['CHOWN_HOME'] = 'yes'
            self.environment['CHOWN_HOME_OPTS'] = '-R'

        return await super().start()

# Use the class directly, not as a string
c.JupyterHub.spawner_class = CustomDockerSpawner

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
c.DockerSpawner.image = 'registry.np.dotnot.pl/quay.io/jupyter/pytorch-notebook:cuda12-latest'

# Enable GPU support
c.DockerSpawner.extra_host_config = {
    'device_requests': [
        {
            'driver': 'nvidia',
            'count': -1,  # -1 = all GPUs, or specify number
            'capabilities': [['gpu', 'compute', 'utility']]
        }
    ]
}

# Use internal IPs for communication
c.DockerSpawner.use_internal_ip = True

# Start containers as root so they can change UID/GID at startup
c.DockerSpawner.extra_create_kwargs = {'user': 'root'}

# Remove containers when they are stopped
c.DockerSpawner.remove = True

# Force remove containers on conflict
c.DockerSpawner.remove_containers = True

# Instead, ensure hub is accessible from spawned containers
c.JupyterHub.hub_ip = '0.0.0.0'  # Listen on all interfaces inside container

# Resource limits
c.DockerSpawner.mem_limit = '2G'
c.DockerSpawner.cpu_limit = 1.0

c.DockerSpawner.notebook_dir = '/home/jovyan/work'
c.DockerSpawner.volumes = {
    '/share/db/jupyterhub/users/{raw_username}/jovyan/': '/home/jovyan',
    '/share/homes/{raw_username}/jupyter/': '/home/jovyan/work'
}

### --- JupyterHub OAuth Idle Culler Configuration --- ###
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
