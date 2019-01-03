###############################################################################
#                                                                             #
# Copyright (C) 2019 Troels Schwarz-Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################
.PHONY: help build dev test test-env

# Docker image name and tag
IMAGE:=tlinnet/csharp-notebook
TAG?=latest
# Shell that make should use
SHELL:=bash

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build relax
	export PYTHON_INCLUDE_DIR=`python -c 'from distutils import sysconfig; print(sysconfig.get_python_inc())'`
	scons

build-docker: DARGS?=
build-docker: ## Make the latest build of the image
	#docker build $(DARGS) --rm --force-rm -t $(IMAGE):$(TAG) .
	docker build $(DARGS) --rm --force-rm -t $(IMAGE):$(TAG) -f devel_scripts/travis-ci/Dockerfile_build .

build-env: ## Make a build environment by installing build dependencies with pip
	pip install -r devel_scripts/travis-ci/requirements.txt

dev-docker: ARGS?=
dev-docker: DARGS?=
dev-docker: PORT?=8888
dev-docker: ## Make a container from a tagged image image
	docker run -it --rm -p $(PORT):8888 $(DARGS) $(REPO) $(ARGS)

test: ## Make a test run against the latest image
	pytest devel_scripts/travis-ci/tests

test-env: ## Make a test environment by installing test dependencies with pip
	pip install -r devel_scripts/travis-ci/requirements-test.txt
