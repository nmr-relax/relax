#!/bin/tcsh
###############################################################################
#                                                                             #
# Copyright (C) 2016 Troels E. Linnet                                         #
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

echo 'http://svn.gna.org/viewcvs/*checkout*/relax/trunk/devel_scripts/openmpi_test_install_tcsh.sh'
echo 'Source the commands with: source openmpi_test_install_tcsh.sh'
echo ""

set A="'"
echo "This is functions to test openmpi, python and openmpi." echo ""

echo "Shell is: $SHELL"; echo ""

echo "> which mpirun"; which mpirun; echo ""

echo "> module avail"; module avail; echo ""

echo "> lscpu"; lscpu; echo ""

echo "> mpirun --version"; mpirun --version;echo ""

echo "> mpirun --report-bindings -np 2 echo $A hello world $A"; mpirun --report-bindings -np 2 echo "hello world"; echo ""

echo "> mpirun --report-bindings -np 2 python -c $A print "\""hello"\"" $A"; mpirun --report-bindings -np 2 python -c "print $A hello $A"; echo ""

echo "> mpirun --report-bindings -np 2 python --version"; mpirun --report-bindings -np 2 python3 --version; echo ""

echo "> mpirun --report-bindings -np 2 /usr/bin/env python --version"; mpirun --report-bindings -np 2 /usr/bin/env python --version; echo ""

echo "Testing python, mpi4py and mpirun"; python3 --version; /usr/bin/env python --version; python3 -c "import mpi4py; print mpi4py.__version__"

mpirun -np 2 python3 -c "import mpi4py; from mpi4py import MPI; print($A Mpi4py %s process %d of %d on %s.$A %(mpi4py.__version__, MPI.COMM_WORLD.Get_rank(),MPI.COMM_WORLD.Get_size(), MPI.Get_processor_name()))"

echo "Done"
