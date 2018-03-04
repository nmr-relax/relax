#!/bin/bash
# -*- coding: UTF-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2015 Troels E. Linnet                                         #
# Copyright (C) 2017 Edward d'Auvergne                                        #
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
  echo "Current version of bmrblib is: $VBMR"
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
  curl https://iweb.dl.sourceforge.net/project/minfx/$VMIN/minfx-$VMIN.tar.gz -o minfx-$VMIN.tar.gz
  tar -xzf minfx-$VMIN.tar.gz
  cd minfx-$VMIN
  sudo pip install .
  cd $HOME

  # Install bmrblib
  mkdir -p $HOME/Downloads
  cd $HOME/Downloads
  curl https://iweb.dl.sourceforge.net/project/bmrblib/$VBMR/bmrblib-$VBMR.tar.gz -o bmrblib-$VBMR.tar.gz
  tar -xzf bmrblib-$VBMR.tar.gz
  cd bmrblib-$VBMR
  sudo pip install .
  cd $HOME
}

# Get latest compiled version of relax
function getlatest {
  cd $HOME
  if [ ! -d "$HOME/relax-$VREL" ]; then
    curl https://iweb.dl.sourceforge.net/project/relax/$VREL/relax-$VREL.GNU-Linux.x86_64.tar.bz2 -o relax-$VREL.GNU-Linux.x86_64.tar.bz2
    tar xvjf relax-$VREL.GNU-Linux.x86_64.tar.bz2
    rm relax-$VREL.GNU-Linux.x86_64.tar.bz2
  fi
  if [ ! \( -e "$HOME/bin/relax_$VREL" \) ]; then
    ln -s $HOME/relax-$VREL/relax $HOME/bin/relax_$VREL
  fi
  cd $HOME
}

# Get relax with git.
function gettrunk {
  cd $HOME
  if [ ! -d "$HOME/relax" ]; then
    git clone git://git.code.sf.net/p/nmr-relax/code relax
  fi
  cd $HOME/relax
  git checkout master; git pull
  scons
  if [ ! \( -e "$HOME/bin/relax" \) ]; then
    ln -s $HOME/relax/relax $HOME/bin/relax
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
  mpirun --report-bindings -np 2 echo "mpirun with 2 CPU echoes"

  # Print info
  which relax_$VREL
  relax_$VREL -i

  which relax
  relax -i
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
#installandcheck
