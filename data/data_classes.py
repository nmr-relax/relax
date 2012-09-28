###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Basic objects used to build the relax data store."""

# Python module imports.
from re import search
from numpy import ndarray

# relax module imports.
from relax_xml import fill_object_contents, xml_to_object


class Element(object):
    """Empty data container."""

    def __init__(self, name='element', desc='container object'):
        """Initialise some class variables.

        @keyword name:  The name of the object.
        @type name:     str
        @keyword desc:  The description of the object.
        @type desc:     str
        """

        # Execute the base class __init__() method.
        super(Element, self).__init__()

        # Some generic initial names.
        self.name = name
        self.desc = desc

        # Blacklisted objects.
        self.blacklist = []


    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^_", name):
                continue

            # Get the object.
            obj = getattr(self, name)

            # Numpy matrices.
            if isinstance(obj, ndarray) and  isinstance(obj[0], ndarray):
                spacer = '\n'
            else:
                spacer = ''

            # Generate the text.
            text = text + "%-25s%s%-100s\n" % (name, spacer, repr(obj))

        # Return the lot.
        return text


    def from_xml(self, super_node, file_version=1):
        """Recreate the element data structure from the XML element node.

        @param super_node:      The element XML node.
        @type super_node:       xml.dom.minicompat.Element instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Recreate all the other data structures.
        xml_to_object(super_node, self, file_version=file_version)


    def is_empty(self):
        """Method for testing if the Element container is empty.

        @return:    True if the Element container is empty, False otherwise.
        @rtype:     bool
        """

        # An object has been added to the container.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^__", name):
                continue

            # An object has been added.
            return False

        # The Element container is empty.
        return True


    def to_xml(self, doc, element):
        """Create an XML element for the container.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the data container XML element to.
        @type element:  XML element object
        """

        # Create a new element for this container and add it to the higher level element.
        cont_element = doc.createElement(self.name)
        element.appendChild(cont_element)

        # Set the list attributes.
        cont_element.setAttribute('desc', self.desc)

        # Blacklisted objects.
        blacklist = ['name', 'desc', 'blacklist'] + list(Element.__dict__.keys() + self.__class__.__dict__.keys() + object.__dict__.keys())

        # Store and blacklist the objects which have to_xml() methods.
        to_xml_list = []
        for name in dir(self):
            # Skip blacklisted objects.
            if name in blacklist:
                continue

            # Skip special objects.
            if search('^_', name):
                continue

            # Execute any to_xml() methods, and add that object to the blacklist.
            obj = getattr(self, name)
            if hasattr(obj, 'to_xml'):
                to_xml_list.append(obj)
                blacklist = blacklist + [name]

        # Add all simple python objects within the container to the XML element.
        fill_object_contents(doc, cont_element, object=self, blacklist=blacklist)

        # Execute the object to_xml() methods.
        for obj in to_xml_list:
            obj.to_xml(doc, cont_element)



class RelaxListType(list):
    """An empty list type container."""

    def __init__(self):
        """Initialise some class variables."""

        # Execute the base class __init__() method.
        super(RelaxListType, self).__init__()

        # Some generic initial names.
        self.list_name = 'relax_list'
        self.list_desc = 'relax list container'
        self.element_name = 'relax_list_element'
        self.element_desc = 'relax container'

        # Blacklisted objects.
        self.blacklist = []


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

        # Loop over the child nodes.
        for node in nodes:
            # Add the data container.
            self.add_item(node.getAttribute('name'))

            # Recreate all the other data structures.
            xml_to_object(node, self[-1], file_version=file_version)


    def to_xml(self, doc, element):
        """Create an XML element for the list data structure.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the list data structure XML element to.
        @type element:  XML element object
        """

        # Create the element and add it to the higher level element.
        list_element = doc.createElement(self.list_name)
        element.appendChild(list_element)

        # Set the list attributes.
        list_element.setAttribute('desc', self.list_desc)

        # Blacklisted objects.
        blacklist = ['list_name', 'list_desc', 'element_name', 'element_desc', 'blacklist'] + list(self.__dict__.keys() + RelaxListType.__dict__.keys() + self.__class__.__dict__.keys() + list.__dict__.keys() + list.__dict__.keys())

        # Add all simple python objects within the list to the list element.
        fill_object_contents(doc, list_element, object=self, blacklist=blacklist)

        # Loop over the list.
        for i in xrange(len(self)):
            # The element has its own to_xml() method.
            if hasattr(self[i], 'to_xml'):
                self[i].to_xml(doc, list_element)

            # Normal element.
            else:
                # Create an XML element for each container.
                list_item_element = doc.createElement(self.element_name)
                list_element.appendChild(list_item_element)
                list_item_element.setAttribute('index', repr(i))
                list_item_element.setAttribute('desc', self.element_desc)

                # Blacklisted objects.
                blacklist = list(self[i].__class__.__dict__.keys())

                # Add objects which have to_xml() methods.
                for name in dir(self[i]):
                    # Skip blacklisted objects.
                    if name in blacklist:
                        continue

                    # Skip special objects.
                    if search('^_', name):
                        continue

                    # Execute any to_xml() methods, and add that object to the blacklist.
                    obj = getattr(self[i], name)
                    if hasattr(obj, 'to_xml'):
                        obj.to_xml(doc, list_item_element)
                        blacklist = blacklist + [name]

                # Add all simple python objects within the container to the XML element.
                fill_object_contents(doc, list_item_element, object=self[i], blacklist=blacklist)
