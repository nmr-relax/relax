###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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
"""Package containing the relax data storage object."""


# Python module imports.
from re import search
from string import split
from time import asctime
import xml.dom.minidom

# relax module imports.
from pipe_container import PipeContainer
from relax_errors import RelaxPipeError
from version import version


__all__ = [ 'data_classes',
            'diff_tensor',
            'diff_tensor_auto_objects',
            'main' ]


class Relax_data_store(dict):
    """The relax data storage object."""

    # The current data pipe.
    current_pipe = None

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs): 
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            self.instance = dict.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance

    
    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The relax data storage object.\n"

        # The data pipes.
        text = text + "\n"
        text = text + "Data pipes:\n"
        pipes = self.instance.keys()
        if pipes:
            for pipe in pipes:
                text = text + "  %s\n" % repr(pipe)
        else:
            text = text + "  None\n"

        # Data store objects.
        text = text + "\n"
        text = text + "Data store objects:\n"
        names = self.__class__.__dict__.keys()
        names.sort()
        for name in names:
            # The object.
            obj = getattr(self, name)

            # The text.
            if obj == None or type(obj) == str:
                text = text + "  %s %s: %s\n" % (name, type(obj), obj)
            else:
                text = text + "  %s %s: %s\n" % (name, type(obj), split(obj.__doc__, '\n')[0])

        # dict methods.
        text = text + "\n"
        text = text + "Inherited dictionary methods:\n"
        for name in dir(dict):
            # Skip special methods.
            if search("^_", name):
                continue

            # Skip overwritten methods.
            if name in self.__class__.__dict__.keys():
                continue

            # The object.
            obj = getattr(self, name)

            # The text.
            text = text + "  %s %s: %s\n" % (name, type(obj), split(obj.__doc__, '\n')[0])

        # Return the text.
        return text


    def __reset__(self):
        """Delete all the data from the relax data storage object.

        This method is to make the current single instance of the Data object identical to a newly
        created instance of Data, hence resetting the relax program state.
        """

        # Loop over the keys of self.__dict__ and delete the corresponding object.
        for key in self.__dict__.keys():
            # Delete the object.
            del self.__dict__[key]

        # Remove all items from the dictionary.
        self.instance.clear()


    def add(self, pipe_name, pipe_type):
        """Method for adding a new data pipe container to the dictionary.

        This method should be used rather than importing the PipeContainer class and using the
        statement 'D[pipe] = PipeContainer()', where D is the relax data storage object and pipe is
        the name of the data pipe.

        @param pipe:    The name of the new data pipe.
        @type pipe:     str
        """

        # Test if the pipe already exists.
        if pipe_name in self.instance.keys():
            raise RelaxPipeError(pipe_name)

        # Create a new container.
        self[pipe_name] = PipeContainer()

        # Add the data pipe type string to the container.
        self[pipe_name].pipe_type = pipe_type

        # Change the current data pipe.
        self.instance.current_pipe = pipe_name


    def from_xml(self, file, dir=None, verbosity=1):
        """Parse a XML document representation of a data pipe, and load it into the relax data store.

        @param file:        The open file object.
        @type file:         file
        @keyword dir:       The name of the directory containing the results file.
        @type dir:          str
        @keyword verbosity: A flag specifying the amount of information to print.  The higher the value,
                            the greater the verbosity.
        @type verbosity:    int
        """

        # Create the XML document from the file.
        doc = xml.dom.minidom.parse(file)

        # Get the relax node.
        relax_node = doc.childNodes[0]

        # Get the relax version of the XML file.
        relax_version = str(relax_node.getAttribute('version'))

        # Fill the pipe.
        self[self.instance.current_pipe].from_xml(relax_node, dir=dir)


    def to_xml(self, file):
        """Create a XML document representation of the current data pipe.

        This method creates the top level XML document including all the information needed
        about relax, calls the PipeContainer.xml_write() method to fill in the document contents,
        and writes the XML into the file object.

        @param file:        The open file object.
        @type file:         file
        """

        # Create the XML document object.
        xmldoc = xml.dom.minidom.Document()

        # Create the top level element, including the relax URL.
        top_element = xmldoc.createElementNS('http://nmr-relax.com', 'relax')

        # Append the element.
        xmldoc.appendChild(top_element)

        # Set the relax version number, and add a creation time.
        top_element.setAttribute('version', version)
        top_element.setAttribute('time', asctime())

        # Create the pipe XML element and add it to the top level XML element.
        pipe_element = xmldoc.createElement('pipe')
        top_element.appendChild(pipe_element)

        # Set the data pipe attributes.
        pipe_element.setAttribute('desc', 'The contents of a relax data pipe')
        pipe_element.setAttribute('name', self.instance.current_pipe)
        pipe_element.setAttribute('type', self[self.instance.current_pipe].pipe_type)

        # Fill the data pipe XML element.
        self[self.instance.current_pipe].to_xml(xmldoc, pipe_element)

        # Write out the XML file.
        file.write(xmldoc.toprettyxml(indent='    '))
