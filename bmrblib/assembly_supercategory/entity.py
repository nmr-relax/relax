###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""The entity saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#entity.
"""

# relax module imports.
from bmrblib.misc import translate
from bmrblib.tag_category import TagCategory
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class EntitySaveframe:
    """The entity saveframe class."""

    # Saveframe variables.
    label = 'entity'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, frq=None, mol_name=None, mol_type='polymer', res_nums=None, res_names=None, atom_names=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword mol_name:      The molecule name.
        @type mol_name:         str
        @keyword mol_type:      The molecule type.
        @type mol_type:         str
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Place the args into the namespace.
        self.frq = frq
        self.mol_name = mol_name
        self.mol_type = mol_type
        self.res_names = translate(res_names)
        self.atom_names = translate(atom_names)
        self.data = translate(data)
        self.errors = translate(errors)

        # Initialise the save frame.
        self.frame = SaveFrame(title=mol_name)

        # Create the tag categories.
        self.entity.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.entity = Entity(self)


class Entity(TagCategory):
    """Base class for the Entity tag category."""

    def create(self):
        """Create the Entity tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['SfCategory'])], tagvalues=[['entity']]))

        # The entity name.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['Name'])], tagvalues=[[self.sf.mol_name]]))

        # The entity type.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['Type'])], tagvalues=[[self.sf.mol_type]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Saveframe_category'
        self.tag_names['Name'] = 'Name'
        self.tag_names['Type'] = 'Type'
