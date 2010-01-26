###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Data store objects for holding all the GUI specific variables."""

# relax module imports.
from data_classes import Element, RelaxListType


class Gui(Element):
    """Container for the global GUI data structures."""

    def __init__(self):
        """Initialise the container info."""

        # Execute the base class __init__() method.
        super(Gui, self).__init__()

        # Add the analysis list object.
        self.analyses = Analyses()

        # Set the name and description.
        self.name = 'relax_gui'
        self.desc = 'The relax GUI information store.'



class Analyses(RelaxListType):
    """A list object for holding all the GUI info specific to a certain analysis type."""

    def __init__(self):
        """Initialise some class variables."""

        # Execute the base class __init__() method.
        super(Analyses, self).__init__()

        # Some generic initial names.
        self.list_name = 'analyses'
        self.list_desc = 'List of relax analyses'
        self.element_name = 'analysis'
        self.element_desc = 'relax analysis'


    def add(self, type=None):
        """Add a new analysis type.

        @keyword type:  The analysis type.  This can be currently one of 'noe', 'r1', 'r2', or 'model-free'.
        @type type:     str
        """

        # Append an empty element.
        self.append(Element())

        # Set the analysis name.
        self.name = type
