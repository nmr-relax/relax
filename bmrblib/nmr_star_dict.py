###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""The base classes for the NMR-STAR dictionary support within relax.

The most up to date NMR-STAR dictionary relax uses is the v3.1 version documented at
http://www.bmrb.wisc.edu/dictionary/3.1html/SuperGroupPage.html.
"""

# relax module imports.
from bmrblib.assembly_supercategory.entity import EntitySaveframe
from bmrblib.NMR_parameters.chem_shift_anisotropy import ChemShiftAnisotropy
from bmrblib.thermodynamics.order_parameters import OrderParameterSaveframe
from pystarlib.File import File


class NMR_STAR:
    """The base object for the NMR-STAR dictionary."""

    # Class extension string.
    ext = ''


    def __init__(self, title, file_path):
        """Initialise the NMR-STAR dictionary object.

        @param title:       The title of the NMR-STAR data.
        @type title:        str
        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the pystarlib File object.
        self.data = File(title=title, filename=file_path)

        # Create the class objects.
        self.create_saveframes()


    def create_saveframes(self):
        """Create all the saveframe objects."""

        # Initialise the assembly_supercategory saveframe supergroup.
        self.entity = EntitySaveframe(self.data.datanodes)

        # Initialise the NMR parameters saveframe supergroup.
        self.chem_shift_anisotropy = ChemShiftAnisotropy(self.data.datanodes)

        # Initialise the kinetic saveframe supergroup API.
        self.relaxation = Relaxation(self.data.datanodes)

        # Initialise the thermodynamics saveframe supergroup.
        self.order_parameters = OrderParameterSaveframe(self.data.datanodes)


    def read(self):
        """Read the data from a BMRB NMR-STAR formatted file."""

        # Read the contents of the STAR formatted file.
        self.data.read()


    def write(self):
        """Write the data to a BMRB NMR-STAR formatted file."""

        # Write the contents to the STAR formatted file.
        self.data.write()
