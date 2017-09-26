#!/bin/bash
# -*- coding: UTF-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2015-2016 Troels E. Linnet                                    #
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

# Install yum packages
function doyum {
  # Install lynx
  sudo yum -y install lynx

  # Install for running relax in multiple CPU mode
  sudo yum -y install openmpi-devel
  echo "module load mpi/openmpi-x86_64" >> $HOME/.bash_profile

  # For trunk checkout and graphs
  sudo yum -y install subversion scons 

  # Install xmgrace. Add the EPEL repository.
  sudo yum -y install wget curl bzip2
  wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
  sudo yum -y install epel-release-latest-7.noarch.rpm
  sudo yum -y install grace

  # Install dependencies
  sudo yum -y install numpy
  sudo yum -y install scipy python-matplotlib

  # mpi4py
  sudo yum -y install mpi4py-openmpi

  # wxPython for GUI
  sudo yum -y install wxPython
}

# Install python packages
function dopip {
  # Install python pip
  sudo easy_install pip
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
  curl https://iweb.dl.sourceforge.net/project/bmrblib/$VMIN/bmrblib-$VMIN.tar.gz -o bmrblib-$VMIN.tar.gz
  tar -xzf bmrblib-$VBMR.tar.gz
  cd bmrblib-$VBMR
  sudo pip install .
  cd $HOME
}

# Get latest compiled version of relax
function getlatest {
  sudo yum -y install 
  cd $HOME
  if [ ! -d "$HOME/relax-$VREL" ]; then
    curl https://iweb.dl.sourceforge.net/project/relax/$VMIN/relax-$VMIN.GNU-Linux.x86_64.tar.bz2 -o relax-$VREL.GNU-Linux.x86_64.tar.bz2
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
  #mpirun --report-bindings --np 2 relax_$VREL --multi='mpi4py' --version

  which relax
  relax -i
  #mpirun --report-bindings --np 2 relax --multi='mpi4py' --version
}

# Combine functions
function installandcheck {
  doyum
  dopip
  getversions
  dobin
  dopiplocal
  getlatest
  gettrunk
  checkinstallation
}

echo "After running 'installandcheck', you should restart the terminal or logout and login again."

# Do functions
#installandcheck

