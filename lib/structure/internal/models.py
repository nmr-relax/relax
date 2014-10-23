0##############################################################################
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
"""The objects representing models in the internal structural object."""

# Python module imports.
from re import match

# relax module import.
from lib.errors import RelaxError, RelaxFromXMLNotEmptyError
from lib.structure.internal.molecules import MolList
from lib.xml import fill_object_contents


class ModelList(list):
    """List type data container for the different structural models.

    Here different models are defined as the same molecule but with different conformations.
    """

    def __init__(self):
        """Set up the class."""

        # Execute the base class method.
        super(ModelList, self).__init__()

        # The current model list (used for speed).
        self.current_models = []


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        text = "Models.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Model number") + "\n"
        for i in range(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].num) + "\n"
        return text


    def add_item(self, model_num=None):
        """Append an empty ModelContainer to the ModelList.

        @keyword model_num: The model number.
        @type model_num:    int
        @return:            The model container.
        @rtype:             ModelContainer instance
        """

        # If no model data exists, replace the empty first model with this model (just a renumbering).
        if len(self) and self.is_empty():
            self[0].num = model_num

        # Otherwise append an empty ModelContainer.
        else:
            # Test if the model number already exists.
            if model_num in self.current_models:
                raise RelaxError("The model '" + repr(model_num) + "' already exists.")

            # Append an empty ModelContainer.
            self.append(ModelContainer(model_num))

        # Update the current model list.
        self.current_models.append(model_num)

        # Return the model container.
        return self[-1]


    def delete_model(self, model_num=None):
        """Delete the given model from the list.

        @keyword model_num: The model to delete.
        @type model_num:    int
        """

        # Sanity check.
        if model_num not in self.current_models:
            raise RelaxError("The model %s does not exist." % model_num)

        # Remove the model from the lists (self and the current models).
        index = self.current_models.index(model_num)
        self.pop(index)
        self.current_models.pop(index)


    def is_empty(self):
        """Method for testing if this ModelList object is empty.

        @return:    True if this list only has one ModelContainer and the model name has not
                    been set, False otherwise.
        @rtype:     bool
        """

        # No ModelContainers.
        if len(self) == 0:
            return True

        # There is only one ModelContainer and it is empty.
        if len(self) == 1 and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def from_xml(self, model_nodes, file_version=1):
        """Recreate a model list data structure from the XML model nodes.

        @param model_nodes:     The model XML nodes.
        @type model_nodes:      xml.dom.minicompat.NodeList instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError(self.__class__.__name__)

        # Loop over the models.
        for model_node in model_nodes:
            # Get the model details and add the model to the ModelList structure.
            num = eval(model_node.getAttribute('num'))
            if num == 'None':
                num = None
            self.add_item(model_num=num)

            # Get the molecule nodes.
            mol_nodes = model_node.getElementsByTagName('mol_cont')

            # Recreate the molecule data structures for the current model.
            self[-1].mol.from_xml(mol_nodes, file_version=file_version)


    def to_xml(self, doc, element):
        """Create XML elements for each model.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the model XML elements to.
        @type element:  XML element object
        """

        # Loop over the models.
        for i in range(len(self)):
            # Create an XML element for this model and add it to the higher level element.
            model_element = doc.createElement('model')
            element.appendChild(model_element)

            # Set the model attributes.
            model_element.setAttribute('desc', 'Model container')
            model_element.setAttribute('num', str(self[i].num))

            # Add all simple python objects within the ModelContainer to the XML element.
            fill_object_contents(doc, model_element, object=self[i], blacklist=['num', 'mol'] + list(self[i].__class__.__dict__.keys()))

            # Add the molecule data.
            self[i].mol.to_xml(doc, model_element)



class ModelContainer(object):
    """Class containing all the model specific data."""

    def __init__(self, model_num=None):
        """Set up the default objects of the model data container."""

        # The model number.
        self.num = model_num

        # The empty molecule list.
        self.mol = MolList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing the data for model %s.\n" % self.num

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Molecule list.
            if name == 'mol':
                text = text + "  mol: The list of %s molecules within the model.\n" % len(self.mol)
                continue

            # Skip the ModelContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + repr(getattr(self, name)) + "\n"

        return text


    def is_empty(self):
        """Method for testing if this ModelContainer object is empty.

        @return:    True if this container is empty and the model number has not been set, False
                    otherwise.
        @rtype:     bool
        """

        # The model num has been set.
        if self.num != None:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'num' or name == 'mol':
                continue

            # Skip the ModelContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The molecule list is not empty.
        if not self.mol.is_empty():
            return False

        # The ModelContainer is unmodified.
        return True


    def mol_loop(self):
        """Generator method to loop over the molecules of this model.

        @return:    The molecules of this model.
        @rtype:     MolContainer instance
        """

        # Loop over all molecules.
        for mol in self.mol:
            # No data, so do not yield the molecule.
            if mol.is_empty():
                continue

            # Yield the molecule.
            yield mol
