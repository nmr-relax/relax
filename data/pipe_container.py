###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from re import match
import xml.dom.ext
import xml.dom.minidom

# relax module imports.
from data_classes import Element
from diff_tensor import DiffTensorData
from mol_res_spin import MoleculeList
from prototype import Prototype



class PipeContainer(Prototype):
    """Class containing all the program data."""

    def __init__(self):
        """Set up all the PipeContainer data structures."""

        # The molecule-residue-spin object.
        self.mol = MoleculeList()

        # The data pipe type.
        self.pipe_type = None

        # Hybrid models.
        self.hybrid_pipes = []


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The data pipe storage object.\n"

        # Special objects/methods (to avoid the getattr() function call on).
        spec_obj = ['mol', 'diff_tensor', 'structure']

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Molecular list.
            if name == 'mol':
                text = text + "  mol: The molecule list (for the storage of the spin system specific data)\n"

            # Diffusion tensor.
            if name == 'diff_tensor':
                text = text + "  diff_tensor: The Brownian rotational diffusion tensor data object\n"

            # Molecular structure.
            if name == 'structure':
                text = text + "  structure: The 3D molecular data object\n"

            # Skip the PipeContainer methods.
            if name in self.__class__.__dict__.keys():
                continue

            # Skip certain objects.
            if match("^_", name) or name in spec_obj:
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        # Return the text representation.
        return text


    def is_empty(self):
        """Method for testing if the data pipe is empty.

        @return:    True if the data pipe is empty, False otherwise.
        @rtype:     bool
        """

        # Is the molecule structure data object empty?
        if hasattr(self, 'structure') and not self.structure.is_empty():
            return False

        # Is the molecule/residue/spin data object empty?
        if not self.mol.is_empty():
            return False

        # Tests for the initialised data (the pipe type can be set in an empty data pipe, so this isn't checked).
        if self.hybrid_pipes:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'mol' or name == 'pipe_type' or name == 'hybrid_pipes':
                continue

            # Skip the PipeContainer methods.
            if name in self.__class__.__dict__.keys():
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The data pipe is empty.
        return True


    def xml_write(self, file):
        """Create a XML document representation of the current data pipe.

        @param file:        The open file object.
        @type file:         file
        """

        # Create the XML document object.
        xmldoc = xml.dom.minidom.Document()

        # Create the top level element.
        top_elem = create_top_level(xmldoc)

        # Create the data pipe element.
        pipe_elem = create_pipe_elem(xmldoc, top_elem)

        # Add all simple python objects within the PipeContainer to the global element.
        global_elem = xmldoc.createElement('global')
        pipe_elem.appendChild(global_elem)
        global_elem.setAttribute('desc', 'Global data located in the top level of the data pipe')
        fill_object_contents(xmldoc, global_elem, object=self, blacklist=['diff_tensor', 'hybrid_pipes', 'is_empty', 'mol', 'pipe_type', 'structure'])

        # Hybrid info.
        create_hybrid_elem(xmldoc, pipe_elem)

        # Add the diffusion tensor data.
        if hasattr(cdp, 'diff_tensor'):
            create_diff_elem(xmldoc, pipe_elem)

        # Add the structural data, if it exists.
        if hasattr(cdp, 'structure'):
            create_str_elem(xmldoc, pipe_elem)

        # Write out the XML file.
        xml.dom.ext.PrettyPrint(xmldoc, file)

        # Print out.
        print self
        print "\n\nXML:"
        xml.dom.ext.PrettyPrint(xmldoc)
