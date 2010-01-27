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
from relax_xml import xml_to_object


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


    def from_xml(self, gui_node):
        """Recreate the element data structure from the XML element node.

        @param gui_node:    The element XML node.
        @type gui_node:     xml.dom.minicompat.Element instance
        """

        # Add the analysis list object.
        self.analyses = Analyses()

        # Get the analyses node.
        analyses_nodes = gui_node.getElementsByTagName('analyses')

        # Recreate the analyses structure.
        self.analyses.from_xml(analyses_nodes)

        # Recreate all the other data structures.
        xml_to_object(gui_node, self, blacklist=['analyses'])



class Analyses(RelaxListType):
    """A list object for holding all the GUI info specific to a certain analysis type."""

    def __init__(self):
        """Initialise some class variables."""

        # Execute the base class __init__() method.
        super(Analyses, self).__init__()

        # Some generic initial names.
        self.list_name = 'analyses'
        self.list_desc = 'GUI information specific to relax analysis types'


    def add(self, type=None):
        """Add a new analysis type.

        @keyword type:  The analysis type.  This can be currently one of 'noe', 'r1', 'r2', or 'model-free'.
        @type type:     str
        @return:        The data container added to the list.
        @rtype:         Element instance
        """

        # Append an empty element.
        self.append(Element(name='analysis', desc='GUI information for a relax analysis'))

        # Set the analysis type.
        self[-1].analysis_type = type

        # Return the container.
        return self[-1]
