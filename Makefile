IMAGE ?= jupyterhub-deploy:latest
DOCKER ?= docker

.PHONY: build test run

build:
	$(DOCKER) build -t $(IMAGE) .
	@$(DOCKER) image ls --format "ID: {{.ID}}  Size: {{.Size}}  Created: {{.CreatedSince}}  Repo: {{.Repository}}  Tag: {{.Tag}}" $(IMAGE)

test: build
	$(DOCKER) run --rm $(IMAGE) jupyterhub --version

run: build
	$(DOCKER) run --rm -p 8000:8000 $(IMAGE)
