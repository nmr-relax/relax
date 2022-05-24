###############################################################################
#                                                                             #
# Copyright (C) 2008-2010,2012,2014 Edward d'Auvergne                         #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Module docstring.
"""Module for checking relax dependencies.

If essential dependencies are missing, then an error message is printed and the program terminated.
"""

# Python modules.
import platform
from os import F_OK, access, environ, sep
from re import sub
import sys


def version_comparison(version1, version2):
    """Compare software versions.

    This will return:

        - When version 1 is older, -1,
        - When both versions are equal, 0,
        - When version 1 is newer, 1.


    @param version1:    The first version number.
    @type version1:     str
    @param version2:    The second version number.
    @type version2:     str
    @return:            The comparison result of the Python cmp() function applied to two lists of integers.  This will be one of [-1, 0, 1].
    @rtype:             int
    """

    # Strip out trailing after release candidate.
    version1 = sub(r'(rc\d)', '', version1)
    version2 = sub(r'(rc\d)', '', version2)

    # Strip out trailing zeros.
    version1 = sub(r'(\.0+)*$', '', version1)
    version2 = sub(r'(\.0+)*$', '', version2)

    # Convert to a list of numbers.
    version1 = [int(val) for val in version1.split('.')]
    version2 = [int(val) for val in version2.split('.')]

    # Return the comparison.
    return (version1 > version2) - (version1 < version2)


# Essential packages.
#####################

# numpy.
try:
    import numpy
    if version_comparison(numpy.version.version, '1.6') == -1:
        sys.stderr.write("Version %s of the 'numpy' dependency is not supported, numpy >= 1.6 is required.\n" % numpy.version.version)
        sys.exit(1)
except ImportError:
    sys.stderr.write("The dependency 'numpy' has not been installed.\n")
    sys.exit(1)

# Command line option parser.
try:
    import optparse
except ImportError:
    sys.stderr.write("The dependency 'Optik' has not been installed.\n")
    sys.exit(1)

# Minfx python package check.
try:
    import minfx
    min_version = '1.0.11'
    if not minfx.__version__ == 'trunk' and version_comparison(minfx.__version__, min_version) == -1:
        sys.stderr.write("Version %s of the 'minfx' dependency is too old, minfx >= %s is required.\n" % (minfx.__version__, min_version))
        sys.exit(1)
except ImportError:
    sys.stderr.write("The dependency 'minfx' has not been installed (see https://sourceforge.net/projects/minfx/).\n")
    sys.exit(1)

# Optional packages.
####################
# Bmrblib python package check.
try:
    import bmrblib
    bmrblib_module = True
except ImportError:
    bmrblib_module = False

# wx module (detecting the Phoenix).
wx_classic = True
wx_stable = True
try:
    import wx
    wx_module = True
    if version_comparison("%i.%i.%i" % (wx.VERSION[0], wx.VERSION[1], wx.VERSION[2]), "3.0.3") != -1:
        wx_classic = False
        if version_comparison("%i.%i.%i" % (wx.VERSION[0], wx.VERSION[1], wx.VERSION[2]), "4.1.0") != 1:
            wx_stable = False
except ImportError:
    wx_module = False
    message = sys.exc_info()[1]
    wx_module_message = message.args[0]

# epydoc module.
try:
    import epydoc
    epydoc_module = True
except ImportError:
    epydoc_module = False

# Readline module (avoiding the damned ^[[?1034h escape code on Linux systems).
try:
    import os
    if 'TERM' in os.environ and os.environ['TERM'] == 'xterm':
        os.environ['TERM'] = 'linux'
    import readline
    readline_module = True
except ImportError:
    readline_module = False

# matplotlib module.
try:
    import matplotlib
    matplotlib_module = True
    if not "DISPLAY" in environ:
        # Force matplotlib to not use any Xwindows backend.
        matplotlib.use('Agg')
except ImportError:
    matplotlib_module = False

# runpy module.
try:
    import runpy
    runpy_module = True
except ImportError:
    runpy_module = False

# profile module (python development packages required).
try:
    import profile
    profile_module = True
except ImportError:
    profile_module = False

# profile C module (python development packages required).
try:
    import cProfile
    cprofile_module = True
except ImportError:
    cprofile_module = False

# BZ2 compression module.
try:
    import bz2
    bz2_module = True
except ImportError:
    message = sys.exc_info()[1]
    bz2_module = False
    bz2_module_message = message.args[0]

# Gzip compression module.
try:
    import gzip
    gzip_module = True
except ImportError:
    message = sys.exc_info()[1]
    gzip_module = False
    gzip_module_message = message.args[0]

# IO module.
try:
    import io
    io_module = True
except ImportError:
    message = sys.exc_info()[1]
    io_module = False
    io_module_message = message.args[0]

# Scipy import.
try:
    import scipy
    scipy_module = True
except:
    scipy_module = False

# VMD module imports.
try:
    from Scientific.Visualization import VMD    # This requires Numeric to be installed (at least in Scientific 2.7.8).
    del VMD
    vmd_module = True
except:
    vmd_module = False

# mpi4py.
try:
    import mpi4py
    mpi4py_module = True
except ImportError:
    message = sys.exc_info()[1]
    mpi4py_module = False

    # The error message.
    mpi4py_message = """The dependency 'mpi4py' has not been installed. You should either:

1. Run without multiprocessor support i.e. remove the --multi mpi4py flag from the command line.

2. Install mpi4py.

3. Choose another multi processor method to give to the --multi command line flag.\n
    """

# PyMOL.
try:
    import pymol
    pymol_module = True
except ImportError:
    message = sys.exc_info()[1]
    pymol_module = False

# XML.
try:
    import xml
    xml_module = True
except ImportError:
    message = sys.exc_info()[1]
    xml_module = False
if xml_module:
    # The XML version mess!
    if hasattr(xml, '_MINIMUM_XMLPLUS_VERSION'):
        xml_version = "%s.%s.%s" % xml._MINIMUM_XMLPLUS_VERSION
        xml_type = 'internal'
    elif hasattr(xml, '__version__'):
        xml_version = xml.__version__
        xml_type = 'PyXML'
    else:
        xml_version = ''
        xml_type = ''

# subprocess module.
try:
    import subprocess
    subprocess_module = True
except ImportError:
    message = sys.exc_info()[1]
    subprocess_module = False
    subprocess_module_message = message.args[0]

# NMRPipe showApod
if subprocess_module:
    try:
        # Call function.
        Temp = subprocess.Popen('showApod', stdout=subprocess.PIPE)

        # Communicate with program, and get output and error output.
        (output, errput) = Temp.communicate()

        # Wait for finish and get return code.
        return_value = Temp.wait()

        # Split the output into lines.
        line_split = output.splitlines()

        # The first line, decoding Python 3 byte arrays.
        line = line_split[0]
        if hasattr(line, 'decode'):
            line = line.decode()

        # Now make test.
        if line == 'showApod: Show Effect of Processing on Noise and Linewidth.':
            showApod_software = True
        else:
            showApod_software = False

    # If software not available.
    except OSError:
        showApod_software = False

# If subprocess module not available, then do not allow showApod.
else:
    showApod_software = False

# ctypes module.
try:
    import ctypes
    ctypes_module = True
except ImportError:
    message = sys.exc_info()[1]
    ctypes_module = False
    ctypes_module_message = message.args[0]
try:
    from ctypes import Structure
    ctypes_structure_module = True
except ImportError:
    message = sys.exc_info()[1]
    ctypes_structure_module = False
    ctypes_structure_module_message = message.args[0]




# Compiled C modules.
#####################

# Relaxation curve fitting.
try:
    from target_functions import relax_fit
    from target_functions.relax_fit import setup
    del setup
    C_module_exp_fn = True
except ImportError:
    # The OS.
    system = platform.system()

    # Does the compiled file exist.
    file = 'relax_fit.so'
    if system == 'Windows' or system == 'Microsoft':
        file = 'relax_fit.pyd'
    if not access('target_functions' + sep + file, F_OK):
        C_module_exp_fn_mesg = "ImportError: relaxation curve fitting is unavailable, the corresponding C modules have not been compiled."

    # Show the full error.
    else:
        message = sys.exc_info()[1]
        C_module_exp_fn_mesg = "ImportError: " + repr(message) + "\nRelaxation curve fitting is unavailable, try compiling the C modules."

    # Set the flag.
    C_module_exp_fn = False
