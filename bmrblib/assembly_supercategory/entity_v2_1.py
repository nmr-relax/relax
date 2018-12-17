#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The v2.1 entity saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/htmldocs/nmr_star/dictionary_files/complete_form_v21.txt.
"""

# relax module imports.
from bmrblib.assembly_supercategory.entity import EntitySaveframe, Entity, EntityCompIndex


class EntitySaveframe_v2_1(EntitySaveframe):
    """The v2.1 entity saveframe class."""

    # Class variables.
    sf_label = 'monomeric_polymer'

    def add_tag_categories(self):
        """Create the v2.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(Entity_v2_1(self))
        self.tag_categories.append(EntityCompIndex_v2_1(self))



class Entity_v2_1(Entity):
    """v2.1 Entity tag category."""

    def __init__(self, sf):
        """Setup the Entity tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Entity_v2_1, self).__init__(sf)

        # Change tag names.
        self['SfCategory'].tag_name =               'Saveframe_category'
        self['Name'].tag_name =                     'Name_common'
        self['Type'].tag_name =                     'Mol_type'
        self['PolymerType'].tag_name =              'Mol_polymer_class'
        self['ThiolState'].tag_name =               'Mol_thiol_state'
        self['PolymerSeqOneLetterCode'].tag_name =  'Mol_residue_sequence'
        self['FormulaWeight'].tag_name =            'Molecular_mass'
        self['DBQueryDate'].tag_name =              'Sequence_homology_query_date'
        self['DBQueryRevisedLastDate'].tag_name =   'Sequence_homology_query_revised_last_date'



class EntityCompIndex_v2_1(EntityCompIndex):
    """v2.1 EntityCompIndex tag category."""

    def __init__(self, sf):
        """Setup the EntityCompIndex_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(EntityCompIndex_v2_1, self).__init__(sf)

        # Change tag names.
        self['EntityCompIndexID'].tag_name =    'Residue_seq_code'
        self['CompID'].tag_name =               'Residue_label'
