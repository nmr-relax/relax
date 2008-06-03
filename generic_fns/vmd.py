###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
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
module_avail = False
try:
    from Scientific.Visualization import VMD    # This requires Numeric to be installed (at least in Scientific 2.7.8).
except ImportError:
    module_avail = False

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxNoPdbError


# The relax data storage object.



class Vmd:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax


    def view(self, run):
        """Function for viewing the collection of molecules using VMD."""

        # Test if the module is available.
        if not module_avail:
            print "VMD is not available (cannot import Scientific.Visualization.VMD due to missing Numeric dependency)."
            return

        # Test if the PDB file has been loaded.
        if not ds.pdb.has_key(run):
            raise RelaxNoPdbError, run

        # Create an empty scene.
        ds.vmd_scene = VMD.Scene()

        # Add the molecules to the scene.
        for i in xrange(len(ds.pdb[run].structures)):
            ds.vmd_scene.addObject(VMD.Molecules(ds.pdb[run].structures[i]))

        # View the scene.
        ds.vmd_scene.view()
