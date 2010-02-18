###############################################################################
#                                                                             #
# Copyright (C) 2007-2009 Edward d'Auvergne                                   #
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
from warnings import warn

# relax module imports.
from align_tensor import AlignTensorList
from diff_tensor import DiffTensorData
from exp_info import ExpInfo
import generic_fns
from mol_res_spin import MoleculeList
from prototype import Prototype
from relax_errors import RelaxFromXMLNotEmptyError
from relax_xml import fill_object_contents, node_value_to_python, xml_to_object
from relax_warnings import RelaxWarning


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
        spec_obj = ['exp_info', 'mol', 'diff_tensor', 'structure']

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

            # The experimental info data container.
            if name == 'exp_info':
                text = text + "  exp_info: The data container for experimental information\n"

            # Skip the PipeContainer methods.
            if name in list(self.__class__.__dict__.keys()):
                continue

            # Skip certain objects.
            if match("^_", name) or name in spec_obj:
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + repr(getattr(self, name)) + "\n"

        # Return the text representation.
        return text


    def from_xml(self, pipe_node, dir=None):
        """Read a pipe container XML element and place the contents into this pipe.

        @param pipe_node:   The data pipe XML node.
        @type pipe_node:    xml.dom.minidom.Element instance
        @keyword dir:       The name of the directory containing the results file (needed for
                            loading external files).
        @type dir:          str
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError(self.__class__.__name__)

        # Get the global data node, and fill the contents of the pipe.
        global_node = pipe_node.getElementsByTagName('global')[0]
        xml_to_object(global_node, self)

        # Get the hybrid node (and its sub-node), and recreate the hybrid object.
        hybrid_node = pipe_node.getElementsByTagName('hybrid')[0]
        pipes_node = hybrid_node.getElementsByTagName('pipes')[0]
        setattr(self, 'hybrid_pipes', node_value_to_python(pipes_node.childNodes[0]))

        # Get the experimental information data nodes and, if they exist, fill the contents.
        exp_info_nodes = relax_node.getElementsByTagName('exp_info')
        if exp_info_nodes:
            # Create the data container.
            self.exp_info = ExpInfo()

            # Fill its contents.
            self.exp_info.from_xml(exp_info_nodes[0])

        # Get the diffusion tensor data nodes and, if they exist, fill the contents.
        diff_tensor_nodes = pipe_node.getElementsByTagName('diff_tensor')
        if diff_tensor_nodes:
            # Create the diffusion tensor object.
            self.diff_tensor = DiffTensorData()

            # Fill its contents.
            self.diff_tensor.from_xml(diff_tensor_nodes[0])

        # Get the alignment tensor data nodes and, if they exist, fill the contents.
        align_tensor_nodes = pipe_node.getElementsByTagName('align_tensors')
        if align_tensor_nodes:
            # Create the alignment tensor object.
            self.align_tensors = AlignTensorList()

            # Fill its contents.
            self.align_tensors.from_xml(align_tensor_nodes[0])

        # Recreate the molecule, residue, and spin data structure.
        mol_nodes = pipe_node.getElementsByTagName('mol')
        self.mol.from_xml(mol_nodes)

        # Get the structural object nodes and, if they exist, fill the contents.
        str_nodes = pipe_node.getElementsByTagName('structure')
        if str_nodes:
            # Get the object type.
            parser = str(str_nodes[0].getAttribute('id'))

            # Create the structural object.
            fail = False
            if parser == 'scientific':
                self.structure = generic_fns.structure.scientific.Scientific_data()
            elif parser == 'internal':
                self.structure = generic_fns.structure.internal.Internal()
            else:
                warn(RelaxWarning("The structural file parser " + repr(parser) + " is unknown.  The structure will not be loaded."))
                fail = True

            # Fill its contents.
            if not fail:
                self.structure.from_xml(str_nodes[0], dir=dir, id=parser)


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
            if name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The data pipe is empty.
        return True


    def to_xml(self, doc, element):
        """Create a XML element for the current data pipe.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The XML element to add the pipe XML element to.
        @type element:  XML element object
        """

        # Add all simple python objects within the PipeContainer to the global element.
        global_element = doc.createElement('global')
        element.appendChild(global_element)
        global_element.setAttribute('desc', 'Global data located in the top level of the data pipe')
        fill_object_contents(doc, global_element, object=self, blacklist=['align_tensors', 'diff_tensor', 'exp_info', 'hybrid_pipes', 'mol', 'pipe_type', 'structure'] + list(self.__class__.__dict__.keys()))

        # Hybrid info.
        self.xml_create_hybrid_element(doc, element)

        # Add the experimental information.
        if hasattr(self, 'exp_info'):
            self.exp_info.to_xml(doc, element)

        # Add the diffusion tensor data.
        if hasattr(self, 'diff_tensor'):
            self.diff_tensor.to_xml(doc, element)

        # Add the alignment tensor data.
        if hasattr(self, 'align_tensors'):
            self.align_tensors.to_xml(doc, element)

        # Add the molecule-residue-spin data.
        self.mol.to_xml(doc, element)

        # Add the structural data, if it exists.
        if hasattr(self, 'structure'):
            self.structure.to_xml(doc, element)


    def xml_create_hybrid_element(self, doc, element):
        """Create an XML element for the data pipe hybridisation information.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the hybridisation info to.
        @type element:  XML element object
        """

        # Create the hybrid element and add it to the higher level element.
        hybrid_element = doc.createElement('hybrid')
        element.appendChild(hybrid_element)

        # Set the hybridisation attributes.
        hybrid_element.setAttribute('desc', 'Data pipe hybridisation information')

        # Create an element to store the pipes list.
        list_element = doc.createElement('pipes')
        hybrid_element.appendChild(list_element)

        # Add the pipes list.
        text_val = doc.createTextNode(str(self.hybrid_pipes))
        list_element.appendChild(text_val)
