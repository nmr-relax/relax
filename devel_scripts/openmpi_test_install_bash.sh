#!/bin/bash
echo 'http://svn.gna.org/viewcvs/*checkout*/relax/trunk/devel_scripts/openmpi_test_install_bash.sh'
echo 'Source the commands with: source openmpi_test_install_bash.sh'
echo 'Then do: testopenmpi'
echo ""

function testopenmpi {
  echo "This is functions to test openmpi, python and openmpi."
  echo ""

  echo "Shell is: $SHELL"
  echo ""

  echo "> which mpirun"
  which mpirun
  echo ""

  echo "> module avail"
  module avail
  echo ""

  echo "> lscpu"
  lscpu
  echo ""

  echo "> mpirun --version"
  mpirun --version
  echo ""

  echo '> mpirun --report-bindings -np 2 echo "hello world"'
  mpirun --report-bindings -np 2 echo "hello world"
  echo ""

  A='"'
  echo "> mpirun --report-bindings -np 2 python -c 'print $A Hello $A '"
  mpirun --report-bindings -np 2 python -c 'print " Hello " '
  echo ""

  echo "> mpirun --report-bindings -np 2 python --version"
  mpirun --report-bindings -np 2 python --version
  echo ""

  echo "> mpirun --report-bindings -np 2 /usr/bin/env python --version"
  mpirun --report-bindings -np 2 /usr/bin/env python --version
  echo ""

  echo "Testing python, mpi4py and mpirun"
  python --version
  /usr/bin/env python --version
  python -c "import mpi4py; print mpi4py.__version__"
  mpirun -np 2 python -c "import mpi4py; from mpi4py import MPI; print('Mpi4py %s process %d of %d on %s.' %(mpi4py.__version__, MPI.COMM_WORLD.Get_rank(),MPI.COMM_WORLD.Get_size(), MPI.Get_processor_name()))"
  echo ""

  #echo "> mpirun --np 2 relax --multi='mpi4py'"
  #mpirun --np 2 relax --multi='mpi4py'
  #echo ""
}
