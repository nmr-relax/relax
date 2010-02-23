###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
import platform
from os import F_OK, access, sep
import sys


# Essential packages.
#####################

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


# Optional packages.
####################

# Readline module.
try:
    import readline
    readline_module = True
except ImportError:
    readline_module = False

# profile module (python development packages required).
try:
    import profile
    profile_module = True
except ImportError:
    profile_module = False

# BZ2 compression module.
try:
    import bz2
    bz2_module = True
except ImportError, message:
    bz2_module = False
    bz2_module_message = message.args[0]

# Gzip compression module.
try:
    import gzip
    gzip_module = True
except ImportError, message:
    gzip_module = False
    gzip_module_message = message.args[0]

# Devnull.
try:
    from os import devnull
    devnull_import = True
except ImportError, message:
    devnull_import = False
    devnull_import_message = message.args[0]

# Scientific Python import.
try:
    from Scientific.IO import PDB
    del PDB
    scientific_pdb_module = True
except ImportError:
    scientific_pdb_module = False

# VMD module imports.
try:
    from Scientific.Visualization import VMD    # This requires Numeric to be installed (at least in Scientific 2.7.8).
    del VMD
    vmd_module = True
except ImportError:
    vmd_module = False


# Compiled C modules.
#####################

# Relaxation curve fitting.
try:
    from maths_fns.relax_fit import setup
    del setup
    C_module_exp_fn = True
except ImportError, message:
    # The OS.
    system = platform.system()

    # Does the compiled file exist.
    file = 'relax_fit.so'
    if system == 'Windows' or system == 'Microsoft':
        file = 'relax_fit.pyd'
    if not access('maths_fns' + sep + file, F_OK):
        C_module_exp_fn_mesg = "ImportError: relaxation curve fitting is unavailable, the corresponding C modules have not been compiled."

    # Show the full error.
    else:
        C_module_exp_fn_mesg = "ImportError: " + message[0] + "\nRelaxation curve fitting is unavailable, try compiling the C modules."

    # Set the flag.
    C_module_exp_fn = False
