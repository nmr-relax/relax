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
objects = relax_fit.o c_chi2.o exponential.o

PYTHON_PATH = /usr/include/python2.4



# Rule which is run when `make' is typed.

.PHONY : relax_curve_fitting
relax_curve_fitting : relax_fit.so


# Rule for compiling the exponential function shared object.

relax_fit.so : $(objects)
	cc -shared $(objects) -o relax_fit.so


# Rules for making the objects
relax_fit.o : relax_fit.h relax_fit.c
	cc -c -I$(PYTHON_PATH) relax_fit.c

exponential.o : relax_fit.h exponential.c
	cc -c -I$(PYTHON_PATH) exponential.c

c_chi2.o : relax_fit.h c_chi2.c
	cc -c -I$(PYTHON_PATH) c_chi2.c
