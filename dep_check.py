###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module for checking relax dependencies.

If essential dependencies are missing, then an error message is printed and the program terminated.
"""

# Python modules.
import sys


# Python packages.
##################

# numpy.
try:
    import numpy
    del numpy
except ImportError:
    sys.stderr.write("The dependency 'numpy' has not been installed.\n")
    sys.exit()

# Command line option parser.
try:
    import optparse
    del optparse
except ImportError:
    sys.stderr.write("The dependency 'Optik' has not been installed.\n")
    sys.exit()

# Minfx python package check.
try:
    import minfx
    del minfx
except ImportError:
    sys.stderr.write("The dependency 'minfx' has not been installed (see https://gna.org/projects/minfx/).\n")
    sys.exit()


# Compiled C modules.
#####################

# Relaxation curve fitting.
try:
    from maths_fns.relax_fit import setup
    del setup
except ImportError:
    sys.stderr.write("\nImportError: relaxation curve fitting is unavailable, try compiling the C modules.\n")
    C_module_exp_fn = False
else:
    C_module_exp_fn = True
