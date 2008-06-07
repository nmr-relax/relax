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


# Python packages.
##################


# numpy.
try:
    import numpy
except ImportError:
    sys.stderr.write("The dependency 'numpy' has not been installed.\n")
    sys.exit()

# Command line option parser.
try:
    import optparse
except ImportError:
    sys.stderr.write("The dependency 'Optik' has not been installed.\n")
    sys.exit()

# Minfx python package check.
try:
    import minfx
except ImportError:
    sys.stderr.write("The dependency 'minfx' has not been installed (see https://gna.org/projects/minfx/).\n")
    sys.exit()
