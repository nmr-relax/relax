rm -f \#* average.pdb covara.xpm covar* eigen* fws-ev1* proj-*
echo 0 | gmx covar -f ../distribution.pdb -s ../distribution.pdb -nofit -o eigenval.xvg -v eigenvec.trr -xpma covar.xpm -l covar.log
gmx xpm2ps -f covar.xpm -o covar.eps -do covar.m2p
echo 0 | gmx anaeig -v eigenvec.trr -f ../distribution.pdb -s ../distribution.pdb -first 1 -last 1 -nframes 10 -extr fws-ev1.pdb
echo 0 | gmx anaeig -f ../distribution.pdb -s ../distribution.pdb -first 1 -last 2 -2d proj-1-2.xvg
echo 0 | gmx anaeig -f ../distribution.pdb -s ../distribution.pdb -first 2 -last 3 -2d proj-2-3.xvg
echo 0 | gmx anaeig -f ../distribution.pdb -s ../distribution.pdb -first 3 -last 4 -2d proj-3-4.xvg
