###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Special relax data storage for nmrglue data."""

# Python module imports.
from base64 import b64encode, decodestring
from numpy import float32, frombuffer
from re import search

# relax module imports.
from data_store.data_classes import Element, RelaxDictType
from lib.xml import fill_object_contents, xml_to_object


class Nmrglue(Element):
    """Container for the global GUI data structures."""

    def __repr__(self):
        # Data structures.
        text = "\n"
        for name in dir(self):
            # Skip Nmrglue and derived class methods.
            if name in Element.__dict__ or name in Nmrglue.__dict__ or name in self.__class__.__dict__:
                continue

            # Skip special objects.
            if search("^_", name):
                continue

            # Get the object.
            obj = getattr(self, name)

            # The objects to add.
            if name == 'data':
                name = "data.shape"
                obj = obj.shape
            elif name in ['dic', 'udic']:
                pass
            else:
                continue

            # Generate the text.
            text = text + "%-25s %-100s\n" % (name, repr(obj))

        # Return the lot.
        return text


    def __init__(self, dic=None, udic=None, data=None):
        """Initialise the container info.

        @keyword dic:           The dic structure from nmrglue.
        @type dic:              dict
        @keyword udic:          The dic structure from nmrglue.
        @type udic:             dict
        @keyword data:          The type of data depending on called function.
        @type data:             depend on function
        """

        # Execute the base class __init__() method.
        super(Nmrglue, self).__init__()

        # Initialise the data.
        self.dic = dic
        self.udic = udic
        self.data = data
        self.element_name = 'nmrglue_container'


    def from_xml(self, nmrglue_node, file_version=1):
        """Recreate the nmrglue data structure from the XML gui node.

        @param gui_node:        The gui XML node.
        @type gui_node:         xml.dom.minicompat.Element instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Get the data node.
        data_nodes = nmrglue_node.getElementsByTagName('data')

        # Loop over the info nodes of the Python object.
        for sub_node in nmrglue_node.childNodes:
            # Get the numpy data.
            if sub_node.localName == 'data':
                # Get the value node.
                value_node = sub_node.getElementsByTagName('value')[0]

                # Convert from Base64 to numpy.float32.
                value = value_node.childNodes[0].nodeValue.strip()
                buffer = decodestring(value)
                self.data = frombuffer(buffer, dtype=float32)

                # The shape attribute.
                shape = eval(sub_node.getAttribute('shape'))

                # Reshape the data.
                self.data = self.data.reshape(shape)

        # Recreate all the other data structures.
        xml_to_object(nmrglue_node, self, file_version=file_version, blacklist=['data'])


    def to_xml(self, doc, element):
        """Create an XML element for the container.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the data container XML element to.
        @type element:  XML element object
        """

        # Create an XML element for the numpy data.
        data_elem = doc.createElement('data')
        element.appendChild(data_elem)

        # Convert the data into a Base64 string.
        string = b64encode(self.data)

        # Store the value as the string.
        val_elem = doc.createElement('value')
        data_elem.appendChild(val_elem)
        val_elem.appendChild(doc.createTextNode(string))

        # Set the type and shape as attributes.
        data_elem.setAttribute('type', 'base64, numpy.float32')
        data_elem.setAttribute('shape', repr(self.data.shape))

        # Add all simple Python objects within the container to the XML element.
        fill_object_contents(doc, element, object=self, blacklist=['name', 'desc', 'blacklist', 'data', 'is_empty', 'element_name'] + list(Nmrglue.__dict__.keys()) + list(self.__class__.__dict__.keys()))



class Nmrglue_dict(RelaxDictType):
    """The main storage structure for all nmrglue data."""

    def __init__(self):
        """Initialise the class."""

        # Call the base class method.
        super(Nmrglue_dict, self).__init__()

        # The metadata.
        self.dict_name = 'nmrglue'
        self.dict_desc = 'main storage for nmrglue data'
        self.element_name = 'nmrglue_container'
        self.element_desc = 'nmrglue container'

        # Blacklist.
        self.blacklist.append('nmrglue_container')


    def from_xml(self, super_node, file_version=1):
        """Recreate the data structure from the XML node.

        @param super_node:      The XML nodes.
        @type super_node:       xml.dom.minicompat.Element instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Recreate all the data structures.
        xml_to_object(super_node, self, file_version=file_version, blacklist=self.blacklist)

        # Get the individual elements.
        nodes = super_node.getElementsByTagName(self.element_name)

        # Loop over the child nodes (each element).
        for node in nodes:
            # Get the key.
            key = str(node.getAttribute('key'))
            key = key.strip("'")

            # Create a new element.
            self[key] = Nmrglue()

            # Recreate from the XML.
            self[key].from_xml(node, file_version=file_version)
