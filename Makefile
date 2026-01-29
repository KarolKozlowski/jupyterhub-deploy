IMAGE ?= jupyterhub-deploy:latest
DOCKER ?= docker

.PHONY: build test run

build:
	$(DOCKER) build -t $(IMAGE) .

test: build
	$(DOCKER) run --rm $(IMAGE) jupyterhub --version

run: build
	$(DOCKER) run --rm -p 8000:8000 $(IMAGE)
