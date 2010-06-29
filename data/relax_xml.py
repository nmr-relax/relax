###############################################################################
#                                                                             #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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
"""Module containing generic fns for creation and parsing of XML representations of python objects."""

# Python module imports.
from numpy import array, float64
from re import search
from string import strip

# relax module imports.
from float import floatAsByteArray, packBytesAsPyFloat


def fill_object_contents(doc, elem, object=None, blacklist=[]):
    """Place all simple python objects into the XML element namespace.

    @param doc:         The XML document object.
    @type doc:          xml.dom.minidom.Document instance
    @param elem:        The element to add all python objects to.
    @type elem:         XML element object
    @keyword object:    The python class instance containing the objects to add.
    @type object:       instance
    @keyword blacklist: A list of object names to exclude.
    @type blacklist:    list of str
    """

    # Loop over the elements of the object.
    for name in dir(object):
        # Skip blacklisted objects.
        if name in blacklist:
            continue

        # Skip special objects.
        if search("^_", name):
            continue

        # Only pack objects in the __mod_attr__ list, if that list exists.
        if hasattr(object, '__mod_attr__') and name not in object.__mod_attr__:
            continue

        # Create a new element for this object, and add it to the main element.
        sub_elem = doc.createElement(name)
        elem.appendChild(sub_elem)

        # Get the sub-object.
        subobj = getattr(object, name)

        # Store floats as IEEE-754 byte arrays (for full precision storage).
        if isinstance(subobj, float) or isinstance(subobj, float64):
            sub_elem.setAttribute('ieee_754_byte_array', repr(floatAsByteArray(subobj)))

        # Add the text value to the sub element.
        text_val = doc.createTextNode(repr(subobj))
        sub_elem.appendChild(text_val)


def node_value_to_python(elem):
    """Convert the node value to a python expression.

    @param elem:    The XML element.
    @type elem:     xml.dom.minidom.Element instance
    """

    # Remove whitespace.
    val = strip(elem.nodeValue)

    # Convert to python and return.
    return eval(val)


def xml_to_object(elem, base_object=None, set_fn=None, blacklist=[]):
    """Convert the XML elements into python objects, and place these into the base object.

    @param elem:            The element to extract all python objects from.
    @type elem:             xml.dom.minidom.Element instance
    @keyword base_object:   The python class instance to place the objects into.
    @type base_object:      instance
    @keyword set_fn:        A function used to replace setattr for placing the object into the base
                            object.
    @type set_fn:           function
    @keyword blacklist:     A list of object names to exclude.
    @type blacklist:        list of str
    """

    # Loop over the nodes of the element
    for node in elem.childNodes:
        # Skip empty nodes.
        if node.localName == None:
            continue

        # The name of the python object to recreate.
        name = str(node.localName)

        # Skip blacklisted objects.
        if name in blacklist:
            continue

        # IEEE-754 floats (for full precision restoration).
        ieee_array = node.getAttribute('ieee_754_byte_array')
        if ieee_array:
            val = packBytesAsPyFloat(eval(ieee_array))

        # Get the node contents.
        else:
            val = node_value_to_python(node.childNodes[0])

        # Set the value.
        setattr(base_object, name, val)


