###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
"""The molecule-residue-spin containers."""

# Python module imports.
from copy import deepcopy
from re import match

# relax module imports.
from prototype import Prototype
from relax_errors import RelaxError
from relax_xml import fill_object_contents



# The spin system data.
#######################

class SpinContainer(Prototype):
    """Class containing all the spin system specific data."""

    def __init__(self, spin_name=None, spin_num=None, select=True):
        """Set up the default objects of the spin system data container."""

        # The spin system name and number.
        self.name = spin_name
        self.num = spin_num
        self.select = select


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the spin system specific data.\n\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Skip the SpinContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


    def is_empty(self):
        """Method for testing if this SpinContainer object is empty.

        @return:    True if this container is empty and the spin number and name have not been set,
                    False otherwise.
        @rtype:     bool
        """

        # The spin number or spin name has been set.
        if self.num != None or self.name != None:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'num' or name == 'name' or name == 'select':
                continue

            # Skip the SpinContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The SpinContainer is unmodified.
        return True


class SpinList(list):
    """List type data container for spin system specific data."""

    def __init__(self):
        """Set up the first spin system data container."""

        # Add the initial spin system container at index 0.
        self.append(SpinContainer())


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Spin systems.\n\n"

        # Residue data.
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s%-8s%-10s" % (i, `self[i].num`, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i].res[j].spin[k]', where D is the relax data storage object.\n"

        return text


    def add_item(self, spin_name=None, spin_num=None, select=True):
        """Function for appending an empty container to the list."""

        # If no spin data exists, replace the empty first spin with this spin.
        if self.is_empty():
            self[0].num = spin_num
            self[0].name = spin_name
            self[0].select = select

        # Otherwise append a new SpinContainer.
        else:
            # Test if the spin number (or name if unnumbered) already exists.
            for i in xrange(len(self)):
                # Spin number has been supplied.
                if spin_num != None:
                    if self[i].num == spin_num:
                        raise RelaxError, "The spin number '" + `spin_num` + "' already exists."

                # No spin numbers.
                else:
                    if self[i].name == spin_name:
                        raise RelaxError, "The unnumbered spin name '" + `spin_name` + "' already exists."

            # Append a new SpinContainer.
            self.append(SpinContainer(spin_name, spin_num, select))


    def is_empty(self):
        """Method for testing if this SpinList object is empty.

        @return:    True if this list only has one SpinContainer and the spin number and name have
                    not been set, False otherwise.
        @rtype:     bool
        """

        # There is only one SpinContainer and it is empty.
        if len(self) == 1 and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def xml_create_element(self, doc, element):
        """Create XML elements for each spin.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the spin XML elements to.
        @type element:  XML element object
        """

        # Loop over the spins.
        for i in xrange(len(self)):
            # Create an XML element for this spin and add it to the higher level element.
            spin_element = doc.createElement('spin')
            element.appendChild(spin_element)

            # Set the spin attributes.
            spin_element.setAttribute('name', self[i].name)
            spin_element.setAttribute('num', str(self[i].num))
            spin_element.setAttribute('index', `i`)
            spin_element.setAttribute('desc', 'Spin')

            # Add all simple python objects within the SpinContainer to the XML element.
            fill_object_contents(doc, spin_element, object=self[i], blacklist=['name', 'num', 'spin'] + self[i].__class__.__dict__.keys())



# The residue data.
###################

class ResidueContainer(Prototype):
    """Class containing all the residue specific data."""

    def __init__(self, res_name=None, res_num=None):
        """Set up the default objects of the residue data container."""

        # The residue name and number.
        self.name = res_name
        self.num = res_num

        # The empty spin system list.
        self.spin = SpinList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the residue specific data.\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Spin systems.
            if name == 'spin':
                text = text + "  spin: The list of spin systems of the residues\n"
                continue

            # Skip the ResidueContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


    def is_empty(self):
        """Method for testing if this ResidueContainer object is empty.

        @return:    True if this container is empty and the residue number and name have not been
                    set, False otherwise.
        @rtype:     bool
        """

        # The residue number or residue name have been set.
        if self.num != None or self.name != None:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'num' or name == 'name' or name == 'spin':
                continue

            # Skip the ResidueContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The spin list is not empty.
        if not self.spin.is_empty():
            return False

        # The ResidueContainer is unmodified.
        return True


class ResidueList(list):
    """List type data container for residue specific data."""

    def __init__(self):
        """Set up the first residue data container."""

        # Add the initial residue container at index 0.
        self.append(ResidueContainer())


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Residues.\n\n"

        # Residue data.
        text = text + "%-8s%-8s%-8s" % ("Index", "Number", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s%-8s" % (i, `self[i].num`, self[i].name) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i].res[j]', where D is the relax data storage object.\n"

        return text


    def add_item(self, res_name=None, res_num=None):
        """Append an empty ResidueContainer to the ResidueList."""

        # If no residue data exists, replace the empty first residue with this residue.
        if self.is_empty():
            self[0].num = res_num
            self[0].name = res_name

        # Otherwise append a new ResidueContainer.
        else:
            # Test if the residue number (or name if unnumbered) already exists.
            for i in xrange(len(self)):
                # Residue number has been supplied.
                if res_num != None:
                    if self[i].num == res_num:
                        raise RelaxError, "The residue number '" + `res_num` + "' already exists in the sequence."

                # No residue numbers.
                else:
                    if self[i].name == res_name:
                        raise RelaxError, "The unnumbered residue name '" + `res_name` + "' already exists."

            # Append a new ResidueContainer.
            self.append(ResidueContainer(res_name, res_num))


    def is_empty(self):
        """Method for testing if this ResidueList object is empty.

        @return:    True if this list only has one ResidueContainer and the residue number and name
                    have not been set, False otherwise.
        @rtype:     bool
        """

        # There is only one ResidueContainer and it is empty.
        if len(self) == 1 and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def xml_create_element(self, doc, element):
        """Create XML elements for each residue.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the residue XML elements to.
        @type element:  XML element object
        """

        # Loop over the residues.
        for i in xrange(len(self)):
            # Create an XML element for this residue and add it to the higher level element.
            res_element = doc.createElement('res')
            element.appendChild(res_element)

            # Set the residue attributes.
            res_element.setAttribute('name', self[i].name)
            res_element.setAttribute('num', str(self[i].num))
            res_element.setAttribute('index', `i`)
            res_element.setAttribute('desc', 'Residue')

            # Add all simple python objects within the ResidueContainer to the XML element.
            fill_object_contents(doc, res_element, object=self[i], blacklist=['name', 'num', 'spin'] + self[i].__class__.__dict__.keys())

            # Add the residue data.
            self[i].spin.xml_create_element(doc, res_element)



# The molecule data.
###################

class MoleculeContainer(Prototype):
    """Class containing all the molecule specific data."""

    def __init__(self, mol_name=None):
        """Set up the default objects of the molecule data container."""

        # The name of the molecule, corresponding to that of the structure file if specified.
        self.name = mol_name

        # The empty residue list.
        self.res = ResidueList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the molecule specific data.\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Residue list.
            if name == 'res':
                text = text + "  res: The list of the residues of the molecule\n"
                continue

            # Skip the MoleculeContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


    def is_empty(self):
        """Method for testing if this MoleculeContainer object is empty.

        @return:    True if this container is empty and the molecule name has not been set, False
                    otherwise.
        @rtype:     bool
        """

        # The molecule name has been set.
        if self.name != None:
            return False

        # An object has been added to the container.
        for name in dir(self):
            # Skip the objects initialised in __init__().
            if name == 'name' or name == 'res':
                continue

            # Skip the MoleculeContainer methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The residue list is not empty.
        if not self.res.is_empty():
            return False

        # The MoleculeContainer is unmodified.
        return True


class MoleculeList(list):
    """List type data container for the molecule specific data."""

    def __init__(self):
        """Set up the first molecule data container."""

        # Add the initial molecule container at index 0.
        self.append(MoleculeContainer())


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        text = "Molecules.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].name) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i]', where D is the relax data storage object.\n"
        return text


    def add_item(self, mol_name=None):
        """Append an empty MoleculeContainer to the MoleculeList."""

        # If no molecule data exists, replace the empty first molecule with this molecule (just a renaming).
        if self.is_empty():
            self[0].name = mol_name

        # Otherwise append an empty MoleculeContainer.
        else:
            # Test if the molecule name already exists.
            for i in xrange(len(self)):
                if self[i].name == mol_name:
                    raise RelaxError, "The molecule '" + `mol_name` + "' already exists in the sequence."

            # Append an empty MoleculeContainer.
            self.append(MoleculeContainer(mol_name))


    def is_empty(self):
        """Method for testing if this MoleculeList object is empty.

        @return:    True if this list only has one MoleculeContainer and the molecule name has not
                    been set, False otherwise.
        @rtype:     bool
        """

        # There is only one MoleculeContainer and it is empty.
        if len(self) == 1 and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def xml_create_element(self, doc, element):
        """Create XML elements for each molecule.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the molecule XML elements to.
        @type element:  XML element object
        """

        # Loop over the molecules.
        for i in xrange(len(self)):
            # Create an XML element for this molecule and add it to the higher level element.
            mol_element = doc.createElement('mol')
            element.appendChild(mol_element)

            # Set the molecule attributes.
            mol_element.setAttribute('name', self[i].name)
            mol_element.setAttribute('index', `i`)
            mol_element.setAttribute('desc', 'Molecule')

            # Add all simple python objects within the MoleculeContainer to the XML element.
            fill_object_contents(doc, mol_element, object=self[i], blacklist=['name', 'res'] + self[i].__class__.__dict__.keys())

            # Add the residue data.
            self[i].res.xml_create_element(doc, mol_element)
