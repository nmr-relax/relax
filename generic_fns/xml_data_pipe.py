###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for the creation and parsing of an XML representation of a data pipe."""

# Python module imports.
from re import search
import xml.dom.ext
import xml.dom.minidom

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from version import version


def create_diff_elem(doc, elem):
    """Create an element for the diffusion tensor.

    @param doc:     The XML document object.
    @type doc:      xml.dom.minidom.Document instance
    @param elem:    The element to add the diffusion tensor element to.
    @type elem:     XML element object
    """

    # Create the diffusion tensor element and add it to the higher level element.
    tensor_elem = doc.createElement('diff_tensor')
    elem.appendChild(tensor_elem)

    # Set the diffusion tensor attributes.
    tensor_elem.setAttribute('desc', 'Diffusion tensor')
    tensor_elem.setAttribute('type', ds[ds.current_pipe].diff_tensor.type)

    # Add all simple python objects within the PipeContainer to the pipe element.
    fill_object_contents(doc, tensor_elem, object=ds[ds.current_pipe].diff_tensor, blacklist=['is_empty', 'type'])


def create_pipe_elem(doc, elem):
    """Create an element for the data pipe, and add data pipe info as attributes.

    @param doc:     The XML document object.
    @type doc:      xml.dom.minidom.Document instance
    @param elem:    The element to add the pipe element to.
    @type elem:     XML element object
    """

    # Create the pipe element and add it to the higher level element.
    pipe_elem = doc.createElement('pipe')
    elem.appendChild(pipe_elem)

    # Set the data pipe attributes.
    pipe_elem.setAttribute('name', ds.current_pipe)
    pipe_elem.setAttribute('type', ds[ds.current_pipe].pipe_type)

    # Return the pipe element.
    return pipe_elem


def create_top_level(doc):
    """Create the top level element including all the information needed about relax.
 
    @param doc:     The XML document object.
    @type doc:      xml.dom.minidom.Document instance
    """

    # Create the element, including the relax URL.
    top_elem = doc.createElementNS('http://nmr-relax.com', 'relax')

    # Append the element.
    doc.appendChild(top_elem)

    # Set the relax version number.
    top_elem.setAttribute('version', version)

    # Return the element.
    return top_elem


def fill_object_contents(doc, elem, object=None, blacklist=None):
    """Place all simple python objects into the element namespace.

    @param doc:         The XML document object.
    @type doc:          xml.dom.minidom.Document instance
    @param elem:        The element to add all python objects to.
    @type elem:         XML element object
    @param object:      The python class instance containing the objects to add.
    @type object:       instance
    @param blacklist:   A list of object names to exclude.
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

        # Add the text value to the sub element.
        text_val = doc.createTextNode(`getattr(object, name)`)
        sub_elem.appendChild(text_val)


def read(file, verbosity=1):
    """Parse a XML document representation of a data pipe, and load it into the relax data store.

    @param file:        The open file object.
    @type file:         file
    @keyword verbosity: A flag specifying the amount of information to print.  The higher the value,
                        the greater the verbosity.
    @type verbosity:    int
    """


def write(file):
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
    fill_object_contents(xmldoc, global_elem, object=ds[ds.current_pipe], blacklist=['diff_tensor', 'is_empty', 'mol', 'pipe_type', 'structure'])

    # Add the diffusion tensor data.
    create_diff_elem(xmldoc, pipe_elem)

    # Write out the XML file.
    xml.dom.ext.PrettyPrint(xmldoc, file)

    # Print out.
    print ds[ds.current_pipe].structure
    print "\n\nXML:"
    xml.dom.ext.PrettyPrint(xmldoc)
