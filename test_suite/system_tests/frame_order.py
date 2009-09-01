###############################################################################
#                                                                             #
# Copyright (C) 2006-2009 Edward d'Auvergne                                   #
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

# Python module imports.
from math import pi
import platform
import numpy
from re import search
from os import sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from physical_constants import N15_CSA, NH_BOND_LENGTH
from relax_io import DummyFileObject, open_read_file


# Get the platform information.
SYSTEM = platform.system()
RELEASE = platform.release()
VERSION = platform.version()
WIN32_VER = platform.win32_ver()
DIST = platform.dist()
ARCH = platform.architecture()
MACH = platform.machine()
PROC = platform.processor()
PY_VER = platform.python_version()

# Windows system name pain.
if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
    # Set the system to 'Windows' no matter what.
    SYSTEM = 'Windows'



class Frame_order(TestCase):
    """TestCase class for the functional tests of the frame order theories."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('test', 'frame order')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def mesg_opt_debug(self, spin):
        """Method for returning a string to help debug the minimisation.

        @param spin:    The SpinContainer of the optimised spin.
        @type spin:     SpinContainer instance
        @return:        The debugging string.
        @rtype:         str
        """

        # Initialise the string.
        string = 'Optimisation failure.\n\n'

        # Create the string.
        string = string + "System: " + SYSTEM + "\n"
        string = string + "Release: " + RELEASE + "\n"
        string = string + "Version: " + VERSION + "\n"
        string = string + "Win32 version: " + WIN32_VER[0] + " " + WIN32_VER[1] + " " + WIN32_VER[2] + " " + WIN32_VER[3] + "\n"
        string = string + "Distribution: " + DIST[0] + " " + DIST[1] + " " + DIST[2] + "\n"
        string = string + "Architecture: " + ARCH[0] + " " + ARCH[1] + "\n"
        string = string + "Machine: " + MACH + "\n"
        string = string + "Processor: " + PROC + "\n"
        string = string + "Python version: " + PY_VER + "\n"
        string = string + "numpy version: " + numpy.__version__ + "\n"


        # Minimisation info.
        string = string + "\n\n%-10s%10.16f" % ('s2:', spin.s2)
        string = string + "\n%-10s%10.13f" % ('te:', spin.te * 1e12)
        string = string + "\n%-10s%10.17f" % ('rex:', spin.rex * (2.0 * pi * spin.frq[0])**2)
        string = string + "\n%-10s%10.17g" % ('chi2:', spin.chi2)
        string = string + "\n%-10s%-10i" % ('iter:', spin.iter)
        string = string + "\n%-10s%-10i" % ('f_count:', spin.f_count)
        string = string + "\n%-10s%-10i" % ('g_count:', spin.g_count)
        string = string + "\n%-10s%-10i" % ('h_count:', spin.h_count)
        string = string + "\n%-10s%-10s" % ('warning:', spin.warning)

        # Return the string.
        return string


    def test_rigid_no_rot(self):
        """Test the 'rigid' model for unrotated tensors with no motion."""

        # Execute the script.
        self.relax.interpreter.run(script_file=sys.path[-1] + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order_rigid_no_rot.py')

        # Test the values.
        self.assertEqual(cdp.iter, 92)
        self.assertEqual(cdp.chi2, 0.0)
        self.assertEqual(cdp.alpha, 0.0)
        self.assertEqual(cdp.beta, 0.0)
        self.assertEqual(cdp.gamma, 0.0)
