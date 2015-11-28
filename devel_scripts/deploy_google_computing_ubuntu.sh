#!/bin/bash
# -*- coding: UTF-8 -*-
# Script for deploying relax on Google Cloud Computing GCC

# Install apt-get packages
function doaptget {
  # Install lynx
  sudo apt-get -y install lynx

  # Install for server management
  sudo apt-get -y install htop

  # Install for running relax in multiple CPU mode
  sudo apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev

  # Install dependencies
  sudo apt-get -y install python-numpy
  sudo apt-get -y install python-scipy python-matplotlib python-pip

  # For trunk checkout and graphs
  sudo apt-get -y install subversion scons grace
}

# Install python packages
function dopip {
  sudo pip install mpi4py
  sudo pip install epydoc
}

function getversions {
  # From the wiki, get current versions
  VMIN=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_minfx" | grep -A 10 "Template:Current version minfx" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VBMR=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_bmrblib" | grep -A 10 "Template:Current version bmrblib" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VMPI=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_mpi4py" | grep -A 10 "Template:Current version mpi4py" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VREL=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_relax" | grep -A 10 "Template:Current version relax" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`

  echo "Current version of minfx is: $VMIN"
  echo "Current version of bmrblib is: $VMBR"
  echo "Current version of mpi4py is: $VMPI"
  echo "Current version of relax is: $VREL"
}

# Make home bin
function dobin {
  mkdir -p $HOME/bin
  echo '' >> $HOME/.bashrc
  echo 'export PATH=$PATH:$HOME/bin' >> $HOME/.bashrc
  source $HOME/.bashrc
}

# Do local istallations of pip
function dopiplocal {
  # Install minfx
  mkdir -p $HOME/Downloads
  cd $HOME/Downloads
  curl http://download.gna.org/minfx/minfx-$VMIN.tar.gz -o minfx-$VMIN.tar.gz
  tar -xzf minfx-$VMIN.tar.gz
  cd minfx-$VMIN
  sudo pip install .
  cd $HOME

  # Install bmrblib
  mkdir -p $HOME/Downloads
  cd $HOME/Downloads
  curl http://download.gna.org/bmrblib/bmrblib-$VBMR.tar.gz -o bmrblib-$VBMR.tar.gz
  tar -xzf bmrblib-$VBMR.tar.gz
  cd bmrblib-$VBMR
  sudo pip install .
  cd $HOME
}

# Get latest compiled version of relax
function getlatest {
  cd $HOME
  if [ ! -d "$HOME/relax-$VREL" ]; then
    curl http://download.gna.org/relax/relax-$VREL.GNU-Linux.x86_64.tar.bz2 -o relax-$VREL.GNU-Linux.x86_64.tar.bz2
    tar xvjf relax-$VREL.GNU-Linux.x86_64.tar.bz2
    rm relax-$VREL.GNU-Linux.x86_64.tar.bz2
  fi
  if [ ! \( -e "$HOME/bin/relax_$VREL" \) ]; then
    ln -s $HOME/relax-$VREL/relax $HOME/bin/relax_$VREL
  fi
  cd $HOME
}

# Get the trunk of relax with subversion
function gettrunk {
  cd $HOME
  if [ ! -d "$HOME/relax_trunk" ]; then
    svn co svn://svn.gna.org/svn/relax/trunk relax_trunk
  fi
  cd $HOME/relax_trunk
  svn up
  scons
  if [ ! \( -e "$HOME/bin/relax_trunk" \) ]; then
    ln -s $HOME/relax_trunk/relax $HOME/bin/relax_trunk
  fi
  cd $HOME
}

# Do some check of installation
function checkinstallation {
  # Then check server
  uptime
  whoami
  lscpu
  mpirun --version
  mpirun --report-bindings -np 4 echo "mpirun with 4 CPU echoes"

  # Print info
  which relax_$VREL
  relax_$VREL -i

  which relax_trunk
  relax_trunk -i
}

# Combine functions
function installandcheck {
  doaptget
  dopip
  getversions
  dobin
  dopiplocal
  getlatest
  gettrunk
  checkinstallation
}

# Do functions
installandcheck