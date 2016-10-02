#!/bin/bash
# -*- coding: UTF-8 -*-
# Script for deploying relax on Google Cloud Computing GCC

# Install yum packages
function doyum {
  # Install lynx
  sudo yum -y install lynx

  # Install for running relax in multiple CPU mode
  sudo yum -y install openmpi-devel
  echo "module load openmpi-1.10-x86_64" >> $HOME/.bash_profile

  # Install dependencies
  sudo yum -y install scipy python-matplotlib

  # For trunk checkout and graphs
  sudo yum -y install subversion scons 

  # Install xmgrace. Add the EPEL repository.
  wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
  sudo rpm -ivh epel-release-6-8.noarch.rpm
  sudo yum -y install grace
}

# Install python
function dopython {
  # Install python 2.7 packages
  sudo yum list python27\* | grep -E 'numpy|scipy|matplotlib|mpi4py' 
  sudo yum -y install python27-numpy python27-scipy

  # Python 2.7 scl (short for “Software Collection”) 
  scl -l

  # Instead of using a subshell, we will source dire  
  #scl enable python27 bash
  #cat /opt/rh/python27/enable
  source scl_source enable python27
  echo "source scl_source enable python27" >> $HOME/.bash_profile

  # Test for sudo and sourcing
  python --version
  sudo python --version
  sudo -- sh -c 'source scl_source enable python27; python --version'

  # Pip and packages
  sudo -- sh -c 'source scl_source enable python27; easy_install pip'
  pip --version
  sudo -- sh -c 'source scl_source enable python27; pip install --upgrade pip'
  pip --version

  # mpi4py
  sudo -- sh -c 'source scl_source enable python27; env MPICC=/usr/lib64/openmpi-1.10/bin/mpicc pip install mpi4py'
  mpirun -np 2 python -c "import mpi4py; from mpi4py import MPI; print('Mpi4py %s process %d of %d on %s.' %(mpi4py.__version__, MPI.COMM_WORLD.Get_rank(),MPI.COMM_WORLD.Get_size(), MPI.Get_processor_name()))"

  # Install python epydoc
  sudo -- sh -c 'source scl_source enable python27; pip install epydoc'
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
  mpirun --report-bindings -np 2 echo "mpirun with 2 CPU echoes"

  # Print info
  which relax_$VREL
  relax_$VREL -i

  which relax_trunk
  relax_trunk -i
}

# Combine functions
function installandcheck {
  doyum
  dopython
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

