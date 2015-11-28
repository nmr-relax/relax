#!/bin/bash
# -*- coding: UTF-8 -*-
# Script for deploying relax on Google Cloud Computing GCC

function download {
  # Install lynx
  sudo apt-get -y install lynx

  # From the wiki, get current versions
  VMIN=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_minfx" | grep -A 10 "Template:Current version minfx" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VBMR=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_bmrblib" | grep -A 10 "Template:Current version bmrblib" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VMPI=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_mpi4py" | grep -A 10 "Template:Current version mpi4py" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`
  VREL=`lynx -dump "http://wiki.nmr-relax.com/Template:Current_version_relax" | grep -A 10 "Template:Current version relax" | grep -B 1 "Retrieved from" | head -n 1 | tr -d '[[:space:]]'`

  echo "Current version of minfx is: $VMIN"
  echo "Current version of bmrblib is: $VMBR"
  echo "Current version of mpi4py is: $VMPI"
  echo "Current version of relax is: $VREL"

  # Install for server management
  sudo apt-get -y install htop

  # Install for running relax in multiple CPU mode
  sudo apt-get -y install openmpi-bin openmpi-doc libopenmpi-dev

  # Install dependencies
  sudo apt-get -y install python-numpy
  sudo apt-get -y install python-scipy python-matplotlib python-pip
  sudo pip install mpi4py
  sudo pip install epydoc
  sudo apt-get -y install subversion scons grace

  # Make home bin
  mkdir -p $HOME/bin
  echo '' >> $HOME/.bashrc
  echo 'export PATH=$PATH:$HOME/bin' >> $HOME/.bashrc
  source $HOME/.bashrc

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

  # Get latest compiled version of relax
  curl http://download.gna.org/relax/relax-$VREL.GNU-Linux.x86_64.tar.bz2 -o relax-$VREL.GNU-Linux.x86_64.tar.bz2
  tar xvjf relax-$VREL.GNU-Linux.x86_64.tar.bz2
  rm relax-$VREL.GNU-Linux.x86_64.tar.bz2
  ln -s $HOME/relax-4.0.0/relax $HOME/bin/relax_$VREL

  # Get the subversion of relax
  svn co svn://svn.gna.org/svn/relax/trunk relax_trunk

  # Build
  cd $HOME/relax_trunk
  scons
  ln -s $HOME/relax_trunk/relax $HOME/bin/relax_trunk
  cd $HOME
}


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

  which relax_svn
  relax_svn -i
}

# Do functions
download
checkinstallation