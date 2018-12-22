###############################################################################
#                                                                             #
# Copyright (C) 2018-2019 Troels Schwarz-Linnet                               #
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
# along with relax; if not, write to the Free Software                        #
#                                                                             #
###############################################################################

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

FROM ubuntu:18.04

# Install packages
RUN export DEBIAN_FRONTEND=noninteractive; \
    export DEBCONF_NONINTERACTIVE_SEEN=true; \
    echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections; \
    echo 'tzdata tzdata/Zones/Europe select Copenhagen' | debconf-set-selections; \
    apt-get update -qqy \
    && apt-get install -qqy --no-install-recommends \
	scons gcc python-dev \
    dx lynx htop curl git grace \
    openmpi-bin openmpi-doc libopenmpi-dev ssh \
    python-numpy python-scipy python-matplotlib python-pip python-wxgtk3.0 python-setuptools python-mpi4py

# Upgrade pip
RUN pip install --upgrade pip

# Install python packages with pip
RUN pip install \
        mpi4py \
        epydoc

# Install relax python pagkages
RUN VMIN=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_minfx" | grep -A 10 "Template:Current version minfx" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'` && \
    echo "Installing current version of minfx: $VMIN" && \
    mkdir -p $HOME/Downloads && \
    cd $HOME/Downloads && \
    curl -L https://iweb.dl.sourceforge.net/project/minfx/$VMIN/minfx-$VMIN.tar.gz -o minfx-$VMIN.tar.gz && \
    tar -xzf minfx-$VMIN.tar.gz && \
    cd minfx-$VMIN && \
    pip install . && \
    cd $HOME

RUN VBMR=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_bmrblib" | grep -A 10 "Template:Current version bmrblib" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'` && \
    echo "Installing current version of bmrblib: $VBMR" && \
    mkdir -p $HOME/Downloads && \
    cd $HOME/Downloads && \
    curl -L https://iweb.dl.sourceforge.net/project/bmrblib/$VBMR/bmrblib-$VBMR.tar.gz -o bmrblib-$VBMR.tar.gz && \
    tar -xzf bmrblib-$VBMR.tar.gz && \
    cd bmrblib-$VBMR && \
    pip install . && \
    cd $HOME

# Add user: 
# -m : Create the home directory if it does not exist.
# -s : User's login shell, which defaults to /bin/bash
RUN useradd -ms /bin/bash developer
USER developer
RUN mkdir -p $HOME/work
WORKDIR /home/developer/work

# Stop Gtk-WARNING 
RUN mkdir -p $HOME/.local/share

# Setup relax dir
RUN cd $HOME && \
    mkdir -p $HOME/relax && \
    mkdir -p $HOME/bin && \
    ln -s $HOME/relax/relax $HOME/bin/relax && \
    cd $HOME

# Modify PATH
ENV PATH="/home/developer/bin:${PATH}"	