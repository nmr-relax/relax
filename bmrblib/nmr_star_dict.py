#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The base classes for the NMR-STAR dictionary support within relax.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.
"""

# relax module imports.
from bmrblib.pystarlib.File import File


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


    def read(self):
        """Read the data from a BMRB NMR-STAR formatted file."""

        # Read the contents of the STAR formatted file.
        self.data.read()


    def write(self):
        """Write the data to a BMRB NMR-STAR formatted file."""

        # Write the contents to the STAR formatted file.
        self.data.write()
