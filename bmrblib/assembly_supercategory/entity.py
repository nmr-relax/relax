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
from bmrblib.base_classes import TagCategory
from bmrblib.misc import translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


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

        # The number of entities.
        self.entity_num = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, mol_name=None, mol_type='polymer', polymer_type='polypeptide(L)', polymer_seq_code=None, thiol_state='all free', res_nums=None, res_names=None, atom_names=None):
        """Add relaxation data to the data nodes.

        @keyword mol_name:          The molecule name.
        @type mol_name:             str
        @keyword mol_type:          The molecule type.
        @type mol_type:             str
        @keyword polymer_type:      The type of polymer.  This is only allowed to be one of 'DNA/RNA hybrid', 'polydeoxyribonucleotide', 'polypeptide(D)', 'polypeptide(L)', 'polyribonucleotide', 'polysaccharide(D)', 'polysaccharide(L)'.
        @type polymer_type:         str
        @keyword polymer_seq_code:  The complete sequence of a protein or nucleic acid as it existed in the NMR tube expressed using the one-letter code for standard residues and an X for non-standard residues. Include residues for cloning tags, etc. and for all residues even when experimental data are not reported.  For example, 'HHHHHHAFGCRESWQAKCLPHNMVIXSDF'.
        @type polymer_seq_code:     str
        @keyword thiol_state:       The state of the thiol groups in the entity.  Can be one of 'all disulfide bound', 'all free', 'all other bound', 'disulfide and other bound', 'free and disulfide bound', 'free and other bound', 'free disulfide and other bound', 'not available', 'not present', 'not reported', 'unknown'.
        @type thiol_state:          str
        @keyword res_nums:          The residue number list.
        @type res_nums:             list of int
        @keyword res_names:         The residue name list.
        @type res_names:            list of str
        @keyword atom_names:        The atom name list.
        @type atom_names:           list of str
        """

        # Check the polymer type.
        allowed = ['DNA/RNA hybrid', 'polydeoxyribonucleotide', 'polypeptide(D)', 'polypeptide(L)', 'polyribonucleotide', 'polysaccharide(D)', 'polysaccharide(L)']
        if polymer_type not in allowed:
            raise NameError("The polymer type '%s' should be one of %s." % (polymer_type, allowed))
        allowed = ['all disulfide bound', 'all free', 'all other bound', 'disulfide and other bound', 'free and disulfide bound', 'free and other bound', 'free disulfide and other bound', 'not available', 'not present', 'not reported', 'unknown']

        # Check the polymer one letter code sequence.
        if not isinstance(polymer_seq_code, str):
            raise NameError("The polymer one letter code sequence '%s' should be a string." % polymer_seq_code)

        # Check the thiol state.
        if thiol_state not in allowed:
            raise NameError("The thiol state '%s' should be one of %s." % (thiol_state, allowed))

        # Place the args into the namespace.
        self.mol_name = mol_name
        self.mol_type = mol_type
        self.polymer_type = polymer_type
        self.polymer_seq_code = polymer_seq_code
        self.thiol_state = thiol_state
        self.res_names = translate(res_names)
        self.res_nums = translate(res_nums)
        self.atom_names = translate(atom_names)

        # Increment the number of entities.
        self.entity_num = self.entity_num + 1

        # The entity ID list.
        self.entity_ids = [str(self.entity_num)]*len(self.res_nums)

        # Initialise the save frame.
        self.frame = SaveFrame(title=mol_name)

        # Create the tag categories.
        self.entity.create()
        self.entity_comp_index.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.entity = Entity(self)
        self.entity_comp_index = EntityCompIndex(self)


    def loop(self):
        """Loop over the entity saveframes, yielding the entity info.

        @return:    The entity information consisting of the molecule name, molecule type, residue
                    numbers, and residue names.
        @rtype:     tuple of str, str, list of int, list of str
        """

        # Loop over all datanodes.
        for datanode in self.datanodes:
            # Find the Entity saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.entity.create_tag_label(self.entity.tag_names['SfCategory']):
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == 'entity':
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Get entity info.
            mol_name, mol_type = self.entity.read(datanode.tagtables[0])

            # Get the EntityCompIndex info.
            res_nums, res_names = self.entity_comp_index.read(datanode.tagtables[1])

            # Yield the data.
            yield mol_name, mol_type, res_nums, res_names


class Entity(TagCategory):
    """Base class for the Entity tag category."""

    def create(self):
        """Create the Entity tag category."""

        # The entity tags.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfCategory']], tagvalues=[['entity']]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['EntityID']], tagvalues=[[str(self.sf.entity_num)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Name']], tagvalues=[[self.sf.mol_name]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Type']], tagvalues=[[self.sf.mol_type]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['PolymerType']], tagvalues=[[self.sf.polymer_type]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['PolymerSeqOneLetterCode']], tagvalues=[[self.sf.polymer_seq_code]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['ThiolState']], tagvalues=[[self.sf.thiol_state]]))


    def read(self, tagtable):
        """Extract the Entity tag category info.

        @param tagtable:    The Entity tagtable.
        @type tagtable:     Tagtable instance
        @return:            The entity name and type.
        @rtype:             tuple of str, str
        """

        # The entity info.
        mol_name = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['Name'])][0]
        mol_type = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['Type'])][0]

        # Return the data.
        return mol_name, mol_type


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
        self.tag_names['EntityID'] = 'ID'
        self.tag_names['Name'] = 'Name'
        self.tag_names['Type'] = 'Type'
        self.tag_names['PolymerType'] = 'Polymer_type'
        self.tag_names['PolymerSeqOneLetterCode'] = 'Polymer_seq_one_letter_code'
        self.tag_names['ThiolState'] = 'Thiol_state'


class EntityCompIndex(TagCategory):
    """Base class for the EntityCompIndex tag category."""

    def create(self):
        """Create the Entity tag category."""

        # Keys and objects.
        info = [
            ['EntityCompIndexID',   'res_nums'],
            ['CompID',              'res_names'],
            ['EntityID',            'entity_ids']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def read(self, tagtable):
        """Extract the EntityCompIndex tag category info.

        @param tagtable:    The EntityCompIndex tagtable.
        @type tagtable:     Tagtable instance
        @return:            The residue numbers and names.
        @rtype:             tuple of list of int, list of str
        """

        # The entity info.
        res_nums = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['EntityCompIndexID'])]
        res_names = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['CompID'])]

        # Convert the residue numbers to ints.
        for i in range(len(res_nums)):
            res_nums[i] = int(res_nums[i])

        # Return the data.
        return res_nums, res_names


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
        self.tag_names['EntityCompIndexID'] = 'ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['EntityID'] = 'Entity_ID'

