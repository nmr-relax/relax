###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
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
"""Module containing generic functions for creation and parsing of XML representations of Python objects."""

# Python module imports (note that some of these are needed for the eval() function call).
import numpy
from numpy import set_printoptions, array, inf, nan, ndarray, zeros
from re import search

# Modify numpy for better output of numbers and structures.
set_printoptions(precision=15, threshold=nan)

# relax module imports.
import lib.arg_check
import lib.check_types
from lib.float import floatAsByteArray, packBytesAsPyFloat
from lib.errors import RelaxError


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
        if hasattr(object, '_mod_attr') and name not in object._mod_attr:
            continue

        # Create a new element for this object, and add it to the main element.
        sub_elem = doc.createElement(name)
        elem.appendChild(sub_elem)

        # Get the sub-object.
        subobj = getattr(object, name)

        # Convert to XML.
        object_to_xml(doc, sub_elem, value=subobj)


def node_value_to_python(elem):
    """Convert the node value to a python expression.

    @param elem:    The XML element.
    @type elem:     xml.dom.minidom.Element instance
    """

    # Remove whitespace.
    val = elem.nodeValue.strip()

    # Convert to python and return.
    return eval(val)


def object_to_xml(doc, elem, value=None):
    """Convert the given value into an XML form.

    @param doc:             The XML document object.
    @type doc:              xml.dom.minidom.Document instance
    @param elem:            The element to add the Python objects to.
    @type elem:             XML element object
    @keyword value:         The Python object to convert.
    @type value:            anything
    """

    # Add the text value to the sub element.
    val_elem = doc.createElement('value')
    elem.appendChild(val_elem)
    val_elem.appendChild(doc.createTextNode(repr(value)))

    # The object type.
    if value == None:
        py_type = 'None'
    elif isinstance(value, bool):
        py_type = 'bool'
    elif isinstance(value, str):
        py_type = 'str'
    elif isinstance(value, float):
        py_type = 'float'
    elif isinstance(value, int):
        py_type = 'int'
    elif isinstance(value, list):
        py_type = 'list'
    elif isinstance(value, dict):
        py_type = 'dict'
    elif isinstance(value, ndarray):
        py_type = repr(value.dtype)
    else:
        raise RelaxError("Unknown type for the value '%s'."  % value)

    # Store as an attribute.
    elem.setAttribute('type', py_type)

    # Store floats as IEEE-754 byte arrays (for full precision storage).
    if lib.check_types.is_float(value):
        val_elem = doc.createElement('ieee_754_byte_array')
        elem.appendChild(val_elem)
        val_elem.appendChild(doc.createTextNode(repr(floatAsByteArray(value))))

    # Store lists with floats as IEEE-754 byte arrays.
    elif (isinstance(value, list) or isinstance(value, ndarray)) and len(value) and lib.check_types.is_float(value[0]):
        # The converted list.
        ieee_obj = []
        conv = False
        for i in range(len(value)):
            # A float.
            if lib.check_types.is_float(value[i]):
                ieee_obj.append(floatAsByteArray(value[i]))
                conv = True

            # All other data.
            else:
                ieee_obj.append(value)

        # Store as XML.
        if conv:
            # The element.
            val_elem = doc.createElement('ieee_754_byte_array')
            elem.appendChild(val_elem)

            # Add the text.
            val_elem.appendChild(doc.createTextNode(repr(ieee_obj)))

    # Store dictionaries with floats as IEEE-754 byte arrays.
    elif py_type == 'dict':
        # The converted dict.
        ieee_obj = {}
        conv = False
        for key in list(value.keys()):
            if lib.check_types.is_float(value[key]):
                ieee_obj[key] = floatAsByteArray(value[key])
                conv = True

        # Store as XML.
        if conv:
            # The element.
            val_elem = doc.createElement('ieee_754_byte_array')
            elem.appendChild(val_elem)

            # Add the text.
            val_elem.appendChild(doc.createTextNode(repr(ieee_obj)))

    # Store matrices of floats as IEEE-754 byte arrays.
    elif lib.arg_check.is_float_matrix(value, none_elements=True, raise_error=False):
        # The converted list.
        ieee_obj = []
        for i in range(len(value)):
            # Handle None elements.
            if value[i] == None:
                ieee_obj.append(None)
                continue

            # A normal float list or numpy array.
            ieee_obj.append([])
            for j in range(len(value[i])):
                ieee_obj[-1].append(floatAsByteArray(value[i][j]))

        # The element.
        val_elem = doc.createElement('ieee_754_byte_array')
        elem.appendChild(val_elem)

        # Add the text.
        val_elem.appendChild(doc.createTextNode(repr(ieee_obj)))


def xml_to_object(elem, base_object=None, set_fn=None, file_version=1, blacklist=[]):
    """Convert the XML elements into python objects, and place these into the base object.

    @param elem:            The element to extract all python objects from.
    @type elem:             xml.dom.minidom.Element instance
    @keyword base_object:   The python class instance to place the objects into.
    @type base_object:      instance
    @keyword set_fn:        A function used to replace setattr for placing the object into the base
                            object.
    @type set_fn:           function
    @keyword file_version:  The relax XML version of the XML file.
    @type file_version:     int
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

        # The value - original file version.
        if file_version == 1:
            # IEEE-754 floats (for full precision restoration).
            ieee_array = node.getAttribute('ieee_754_byte_array')
            if ieee_array:
                value = packBytesAsPyFloat(eval(ieee_array))

            # Get the node contents.
            else:
                value = node_value_to_python(node.childNodes[0])

        # The value - second file version.
        elif file_version == 2:
            # Get the type.
            py_type = node.getAttribute('type')
            if not search('dtype', py_type):
                py_type = eval(py_type)

            # Loop over the info nodes of the Python object.
            ieee_value = None
            for sub_node in node.childNodes:
                # Get the value.
                if sub_node.localName == 'value':
                    value = node_value_to_python(sub_node.childNodes[0])

                # IEEE-754 floats (for full precision restoration).
                if sub_node.localName == 'ieee_754_byte_array':
                    ieee_value = node_value_to_python(sub_node.childNodes[0])

            # Use IEEE-754 floats when possible.
            if ieee_value:
                # Simple float.
                if py_type == float:
                    value = packBytesAsPyFloat(ieee_value)

                # Convert dictionaries.
                elif py_type == dict:
                    for key in ieee_value:
                        value[key] = packBytesAsPyFloat(ieee_value[key])

                # Convert lists.
                elif py_type == list:
                    # Loop over the first dimension.
                    for i in range(len(value)):
                        # List of lists.
                        if isinstance(value[i], list) or isinstance(value[i], ndarray):
                            for j in range(len(value[i])):
                                value[i][j] = packBytesAsPyFloat(ieee_value[i][j])

                        # None values.
                        elif ieee_value[i] == None:
                            value[i] = None

                        # Normal list.
                        else:
                            value[i] = packBytesAsPyFloat(ieee_value[i])

                # Numpy types.
                elif search('dtype', py_type):
                    # The specific type.
                    numpy_type = getattr(numpy, py_type[7:-2])

                    # Build a new array of the correct type.
                    value = zeros(value.shape, numpy_type)

                    # A matrix.
                    if isinstance(value[0], ndarray):
                        for i in range(len(value)):
                            for j in range(len(value[i])):
                                value[i, j] = packBytesAsPyFloat(ieee_value[i][j])

                    # A vector.
                    else:
                        for i in range(len(value)):
                            value[i] = packBytesAsPyFloat(ieee_value[i])

        # Set the value.
        setattr(base_object, name, value)
