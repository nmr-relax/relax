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

# relax module imports.
from data_store.data_classes import Element
from lib.xml import object_to_xml, xml_to_object


class Nmrglue(Element):
    """Container for the global GUI data structures."""

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
        for sub_node in node.childNodes:
            # Get the value.
            if sub_node.localName == 'value':
                # Convert from Base64 to numpy.float32.
                buffer = decodestring(sub_node.childNodes[0])
                self.data = frombuffer(buffer, dtype=np.float32)

                # The shape attribute.
                shape = eval(node.getAttribute('shape'))

                # Reshape the data.
                self.data.reshape(shape)

        # Recreate all the other data structures.
        xml_to_object(gui_node, self, file_version=file_version, blacklist=['data'])


    def to_xml(self, doc, element):
        """Create an XML element for the container.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the data container XML element to.
        @type element:  XML element object
        """

        # Call the parent class method for all but the data variable.
        self.blacklist.append('data')
        super(Nmrglue, self).to_xml(doc, element)

        # Convert the data into a Base64 string.
        string = b64encode(self.data)

        # Store the value as the string.
        val_elem = doc.createElement('value')
        element.appendChild(val_elem)
        val_elem.appendChild(doc.createTextNode(string))

        # Set the type and shape as attributes.
        element.setAttribute('type', 'base64, numpy.float32')
        element.setAttribute('shape', repr(self.data.shape))
