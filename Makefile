###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


# Variables.
sys = uname -o
mach = uname -m


# Rule which is run when `make' is typed.

relax : maths_fns/exp_fn.so maths_fns/c_chi2.so


# Rule for compiling the exponential function shared object.

maths_fns/exp_fn.so : maths_fns/exp_fn.c
	cc -shared -I/usr/include/python2.4 maths_fns/exp_fn.c -o maths_fns/exp_fn.so

maths_fns/c_chi2.so : maths_fns/c_chi2.c
	cc -shared -I/usr/include/python2.4 maths_fns/c_chi2.c -o maths_fns/c_chi2.so


# Rule for compiling the manual.

manual : docs/relax.pdf
	cd docs/latex
	docs/latex/compile

html_manual :
	docs/latex/create_html


# Rule for creating the package distribution.

dist : relax
	echo $(sys).$(mach)


# Clean up rule.

clean :
	rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc
	rm -f *.bak */*.bak */*/*.bak */*/*/*.bak
	rm -f *.o */*.o */*/*.o */*/*/*.o
	rm -f *.so */*.so */*/*.so */*/*/*.so
