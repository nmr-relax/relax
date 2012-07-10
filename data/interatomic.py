###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""The interatomic data containers."""

# Python module imports.
from re import match

# relax module imports.
import generic_fns
from prototype import Prototype
from relax_errors import RelaxError, RelaxFromXMLNotEmptyError, RelaxImplementError
from relax_xml import fill_object_contents, object_to_xml, xml_to_object
import specific_fns


class InteratomContainer(Prototype):
    """Class containing the interatomic data."""

    def __init__(self, spin_id1=None, spin_id2=None, select=True):
        """Set up the objects of the interatomic data container.

        @keyword spin_id1:  The spin ID string of the first atom.
        @type spin_id1:     str
        @keyword spin_id2:  The spin ID string of the second atom.
        @type spin_id2:     str
        @keyword select:    The selection flag.
        @type select:       bool
        """

        # Store the spin IDs.
        self.spin_id1 = spin_id1
        self.spin_id2 = spin_id2

        # Class variable defaults.
        self.dipole_pair = False
        self.select = select


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the interatomic specific data between spins %s and %s.\n\n" % (self.spin_id1, self.spin_id2)

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Skip the SpinContainer methods.
            if name in ['is_empty']:
                continue

            # Skip special objects.
            if match("^_", name):
                continue

            # Add the object's attribute to the text string.
            text += "  %s: %s\n" % (name, repr(getattr(self, name)))

        return text


    def is_empty(self):
        """Method for testing if this InteratomContainer object is empty.

        @return:    True if this container is empty, False otherwise.
        @rtype:     bool
        """

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name in ['dipole_pair', 'spin_id1', 'spin_id2', 'select']:
                continue

            # Skip the SpinContainer methods.
            if name in ['is_empty']:
                continue

            # Skip special objects.
            if match("^_", name):
                continue

            # An object has been added.
            return False

        # The SpinContainer is unmodified.
        return True



class InteratomList(list):
    """List type data container for interatomic specific data."""

    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Interatomic data.\n\n"

        # The data.
        text += "%-25s%-25s%-25s" % ("Index", "Spin ID 1", "Spin ID 2") + "\n"
        for i in xrange(len(self)):
            text += "%-25i%-25s%-25s\n\n" % (i, self[i].spin_id1, self[i].spin_id2)

        return text


    def add_item(self, spin_id1=None, spin_id2=None):
        """Append an empty container to the list.

        @keyword spin_id1:  The spin ID string of the first atom.
        @type spin_id1:     str
        @keyword spin_id2:  The spin ID string of the first atom.
        @type spin_id2:     str
        @return:            The new interatomic data container.
        @rtype:             InteratomContainer instance
        """

        # Append a new InteratomContainer.
        cont = InteratomContainer(spin_id1, spin_id2)
        self.append(cont)

        # Return the container.
        return cont


    def is_empty(self):
        """Method for testing if this InteratomList object is empty.

        @return:    True if this list contains no InteratomContainers, False otherwise.
        @rtype:     bool
        """

        # There are no InteratomContainers.
        if len(self) == 0:
            return True

        # Otherwise.
        return False


    def from_xml(self, interatom_nodes, file_version=None):
        """Recreate an interatomic list data structure from the XML spin nodes.

        @param interatom_nodes: The spin XML nodes.
        @type interatom_nodes:  xml.dom.minicompat.NodeList instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError(self.__class__.__name__)

        # Loop over the containers.
        for interatom_node in interatom_nodes:
            # Get the interatomic spin details and add a container to the InteratomList structure.
            spin_id1 = str(interatom_node.getAttribute('spin_id1'))
            spin_id2 = str(interatom_node.getAttribute('spin_id2'))
            self.add_item(spin_id1=spin_id1, spin_id2=spin_id2)

            # Recreate the current container.
            xml_to_object(interatom_node, self[-1], file_version=file_version)


    def to_xml(self, doc, element):
        """Create XML elements for each spin.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the spin XML elements to.
        @type element:  XML element object
        """

        # Get the specific functions.
        data_names = specific_fns.setup.get_specific_fn('data_names', generic_fns.pipes.get_type(), raise_error=False)
        return_data_desc = specific_fns.setup.get_specific_fn('return_data_desc', generic_fns.pipes.get_type(), raise_error=False)

        # Loop over the containers.
        for i in xrange(len(self)):
            # Create an XML element for this container and add it to the higher level element.
            interatom_element = doc.createElement('interatomic')
            element.appendChild(interatom_element)

            # Set the spin attributes.
            interatom_element.setAttribute('desc', 'Interatomic data container')
            interatom_element.setAttribute('spin_id1', str(self[i].spin_id1))
            interatom_element.setAttribute('spin_id2', str(self[i].spin_id2))

            # Get the specific object names and loop over them to get their descriptions.
            object_info = []
            try:
                for name in data_names(error_names=True, sim_names=True):
                    # Get the description.
                    if return_data_desc:
                        desc = return_data_desc(name)
                    else:
                        desc = None

                    # Append the two.
                    object_info.append([name, desc])
            except RelaxImplementError:
                pass

            # Add the ordered objects.
            blacklist = []
            for name, desc in object_info:
                # Add the name to the blacklist.
                blacklist.append(name)

                # Skip the object if it is missing from the InteratomContainer.
                if not hasattr(self[i], name):
                    continue

                # Create a new element for this object, and add it to the main element.
                sub_element = doc.createElement(name)
                interatom_element.appendChild(sub_element)

                # Add the object description.
                if desc:
                    sub_element.setAttribute('desc', desc)

                # Get the object.
                object = getattr(self[i], name)

                # Convert to XML.
                object_to_xml(doc, sub_element, value=object)

            # Add all simple python objects within the InteratomContainer to the XML element.
            fill_object_contents(doc, interatom_element, object=self[i], blacklist=['spin_id1', 'spin_id2'] + blacklist + list(self[i].__class__.__dict__.keys()))
