###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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

        # The free format file settings.
        self.free_file_format = Free_file_format()

        # Set the name and description.
        self.name = 'relax_gui'
        self.desc = 'The relax GUI information store.'


    def from_xml(self, gui_node):
        """Recreate the gui data structure from the XML gui node.

        @param gui_node:    The gui XML node.
        @type gui_node:     xml.dom.minicompat.Element instance
        """

        # Init.
        self.analyses = Analyses()
        self.free_file_format = Free_file_format()

        # Get the analyses node and recreate the analyses structure.
        analyses_nodes = gui_node.getElementsByTagName('analyses')
        self.analyses.from_xml(analyses_nodes[0])

        # Get the file settings node and recreate the structure.
        format_nodes = gui_node.getElementsByTagName('free_file_format')
        if format_nodes:
            self.free_file_format.from_xml(format_nodes[0])

        # Recreate all the other data structures.
        xml_to_object(gui_node, self, blacklist=['analyses', 'free_file_format'])



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
        @return:        The index of the data container added to the list.
        @rtype:         int
        """

        # Append an empty element.
        self.append(Element(name='analysis', desc='GUI information for a relax analysis'))

        # Set the analysis type.
        self[-1].analysis_type = type

        # Return the index of the container.
        return len(self)-1


    def from_xml(self, analyses_node):
        """Recreate the analyses data structure from the XML analyses node.

        @param analyses_node:   The analyses XML node.
        @type analyses_node:    xml.dom.minicompat.Element instance
        """

        # Get all the analysis nodes.
        analysis_nodes = analyses_node.getElementsByTagName('analysis')

        # Loop over the nodes.
        for node in analysis_nodes:
            # Add a blank analysis container.
            index = self.add()

            # Recreate the analysis container.
            self[index].from_xml(node)


class Free_file_format(Element):
    """Container for the free format file settings (column numbers, column separators, etc.)."""

    def __init__(self):
        """Set up the initial values."""

        # Execute the base class __init__() method.
        super(Free_file_format, self).__init__(name='free_file_format', desc='The column numbers and separator for the free format file.')

        # Reset.
        self.reset()


    def reset(self):
        """Reset all variables to the initial values."""

        # The default column numbers.
        self.spin_id_col =   None
        self.mol_name_col =  1
        self.res_num_col =   2
        self.res_name_col =  3
        self.spin_num_col =  4
        self.spin_name_col = 5
        self.data_col =      6
        self.err_col =       7

        # The column separator (set to None for white space).
        self.sep = None
