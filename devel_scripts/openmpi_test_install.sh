echo 'http://svn.gna.org/viewcvs/*checkout*/relax/trunk/devel_scripts/openmpi_test_install.sh'
echo '#Run this script with: $SHELL test_openmpi.sh'
echo ""

echo "This script is to test relax and openmpi."
echo ""

echo "Shell is: $SHELL"
echo ""

echo "> which mpicc"
which mpicc
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

echo "> mpirun --np 2 relax_trunk --multi='mpi4py'"
mpirun --np 2 relax_trunk --multi='mpi4py'
echo ""

