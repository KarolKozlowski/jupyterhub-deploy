FROM jupyterhub/jupyterhub:4.1.5

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    jupyterlab \
    oauthenticator

EXPOSE 8000

CMD ["jupyterhub", "--ip=0.0.0.0", "--port=8000"]
