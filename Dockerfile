FROM quay.io/jupyterhub/jupyterhub:5.4.3

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir \
    oauthenticator \
    dockerspawner \
    jupyterhub-idle-culler

EXPOSE 8000

CMD ["jupyterhub", "--ip=0.0.0.0", "--port=8000"]
