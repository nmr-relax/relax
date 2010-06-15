###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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
import __main__
from math import pi
import platform
import numpy
from re import search
from os import sep
import sys

# relax module imports.
from base_classes import SystemTestCase
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
NUMPY_VER = numpy.__version__
LIBC_VER = platform.libc_ver()

# Windows system name pain.
if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
    # Set the system to 'Windows' no matter what.
    SYSTEM = 'Windows'



class Frame_order(SystemTestCase):
    """TestCase class for the functional tests of the frame order theories."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('test', 'frame order')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def mesg_opt_debug(self):
        """Method for returning a string to help debug the minimisation.

        @return:        The debugging string.
        @rtype:         str
        """

        # Initialise the string.
        string = 'Optimisation failure.\n\n'

        # Create the string.
        string = string + "%-18s%-25s\n" % ("System: ", SYSTEM)
        string = string + "%-18s%-25s\n" % ("Release: ", RELEASE)
        string = string + "%-18s%-25s\n" % ("Version: ", VERSION)
        string = string + "%-18s%-25s\n" % ("Win32 version: ", (WIN32_VER[0] + " " + WIN32_VER[1] + " " + WIN32_VER[2] + " " + WIN32_VER[3]))
        string = string + "%-18s%-25s\n" % ("Distribution: ", (DIST[0] + " " + DIST[1] + " " + DIST[2]))
        string = string + "%-18s%-25s\n" % ("Architecture: ", (ARCH[0] + " " + ARCH[1]))
        string = string + "%-18s%-25s\n" % ("Machine: ", MACH)
        string = string + "%-18s%-25s\n" % ("Processor: ", PROC)
        string = string + "%-18s%-25s\n" % ("Python version: ", PY_VER)
        string = string + "%-18s%-25s\n" % ("Numpy version: ", NUMPY_VER)
        string = string + "%-18s%-25s\n" % ("Libc version: ", (LIBC_VER[0] + " " + LIBC_VER[1]))


        # Minimisation info.
        string = string + "\n%-15s %30.17g\n" % ('alpha:',   cdp.alpha)
        string = string +   "%-15s %30.17g\n" % ('beta:',    cdp.beta)
        string = string +   "%-15s %30.17g\n" % ('gamma:',   cdp.gamma)
        string = string +   "%-15s %30.17g\n" % ('chi2:',    cdp.chi2)
        string = string +   "%-15s %30i\n" % ('iter:',    cdp.iter)
        string = string +   "%-15s %30i\n" % ('f_count:', cdp.f_count)
        string = string +   "%-15s %30i\n" % ('g_count:', cdp.g_count)
        string = string +   "%-15s %30i\n" % ('h_count:', cdp.h_count)
        string = string +   "%-15s %30s\n" % ('warning:', cdp.warning)

        # Return the string.
        return string


    def test_opendx_map(self):
        """Test the mapping of the Euler angle parameters for OpenDx viewing."""

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opendx_euler_angle_map.py')


    def test_opt_rigid_no_rot(self):
        """Test the 'rigid' model for unrotated tensors with no motion."""

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opt_rigid_no_rot.py')

        # Get the debugging message.
        self.mesg = self.mesg_opt_debug()

        # Test the values.
        self.assertEqual(cdp.iter, 92, msg=self.mesg)
        self.assertEqual(cdp.chi2, 0.0, msg=self.mesg)
        self.assertEqual(cdp.alpha, 0.0, msg=self.mesg)
        self.assertEqual(cdp.beta, 0.0, msg=self.mesg)
        self.assertEqual(cdp.gamma, 0.0, msg=self.mesg)


    def test_opt_rigid_rand_rot(self):
        """Test the 'rigid' model for randomly rotated tensors with no motion."""

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'opt_rigid_rand_rot.py')

        # Get the debugging message.
        self.mesg = self.mesg_opt_debug()

        # Test the values.
        self.assertAlmostEqual(cdp.chi2, 3.085356555118994e-26, msg=self.mesg)
        self.assertAlmostEqual(cdp.alpha, 5.0700283197712777, msg=self.mesg)
        self.assertAlmostEqual(cdp.beta, 2.5615753919522359, msg=self.mesg)
        self.assertAlmostEqual(cdp.gamma, 0.64895449611163691, msg=self.mesg)
