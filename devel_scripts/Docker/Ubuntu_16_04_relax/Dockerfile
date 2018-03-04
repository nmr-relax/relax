# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

FROM ubuntu:16.04

# Install packages
RUN apt-get update && \
    apt-get install -y \
        dx lynx htop curl \
        subversion git scons grace \        
        openmpi-bin openmpi-doc libopenmpi-dev \
        python-numpy python-scipy python-matplotlib python-pip python-wxgtk3.0

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
    curl https://iweb.dl.sourceforge.net/project/minfx/$VMIN/minfx-$VMIN.tar.gz -o minfx-$VMIN.tar.gz && \
    tar -xzf minfx-$VMIN.tar.gz && \
    cd minfx-$VMIN && \
    pip install . && \
    cd $HOME

RUN VBMR=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_bmrblib" | grep -A 10 "Template:Current version bmrblib" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'` && \
    echo "Installing current version of bmrblib: $VBMR" && \
    mkdir -p $HOME/Downloads && \
    cd $HOME/Downloads && \
    curl https://iweb.dl.sourceforge.net/project/bmrblib/$VBMR/bmrblib-$VBMR.tar.gz -o bmrblib-$VBMR.tar.gz && \
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

# Get relax
RUN cd $HOME && \
    pwd && \
    git clone git://git.code.sf.net/p/nmr-relax/code relax && \
    cd $HOME/relax && \
    git pull && \
    scons && \
    ./relax -i && \
    mkdir -p $HOME/bin && \
    ln -s $HOME/relax/relax $HOME/bin/relax && \
    cd $HOME

# Modify PATH
ENV PATH="/home/developer/bin:${PATH}"

# Stop Gtk-WARNING 
RUN mkdir -p $HOME/.local/share
