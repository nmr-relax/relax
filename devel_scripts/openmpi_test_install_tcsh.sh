echo 'http://svn.gna.org/viewcvs/*checkout*/relax/trunk/devel_scripts/openmpi_test_install_tcsh.sh'
echo 'Source the commands with: source openmpi_test_install_tcsh.sh'
echo 'Then do: testopenmpi'
echo ""

set A="'"
alias testopenmpi 'echo "This is functions to test openmpi, python and openmpi." echo "";set A="$A";\\
  echo "Shell is: $SHELL"; echo "";\\
  echo "> which mpirun"; which mpirun; echo "";\\
  echo "> module avail"; module avail; echo "";\\
  echo "> lscpu"; lscpu; echo "";\\
  echo "> mpirun --version";mpirun --version;echo "";\\
  echo "> mpirun --report-bindings -np 2 echo $A hello world $A"; mpirun --report-bindings -np 2 echo "hello world"; echo "";\\
  echo "> mpirun --report-bindings -np 2 python -c $A print "\""hello"\"" $A"; mpirun --report-bindings -np 2 python -c "print $A hello $A"; echo "";\\
  echo "> mpirun --report-bindings -np 2 python --version"; mpirun --report-bindings -np 2 python --version; echo "";\\
  echo "> mpirun --report-bindings -np 2 /usr/bin/env python --version"; mpirun --report-bindings -np 2 /usr/bin/env python --version; echo "";\\
  echo "Testing python, mpi4py and mpirun"; python --version; /usr/bin/env python --version; python -c "import mpi4py; print mpi4py.__version__";\\
  mpirun -np 2 python -c "import mpi4py; from mpi4py import MPI; print($A Mpi4py %s process %d of %d on %s.$A %(mpi4py.__version__, MPI.COMM_WORLD.Get_rank(),MPI.COMM_WORLD.Get_size(), MPI.Get_processor_name()))";\\
  echo "Done";\\
'