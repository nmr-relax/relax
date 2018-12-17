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
"""The v3.1 entity saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#entity.
"""

# relax module imports.
from bmrblib.assembly_supercategory.entity import EntitySaveframe, Entity, EntityCompIndex


class EntitySaveframe_v3_1(EntitySaveframe):
    """The v3.1 entity saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(Entity_v3_1(self))
        self.tag_categories.append(EntityCompIndex_v3_1(self))



class Entity_v3_1(Entity):
    """v3.1 Entity tag category."""

    def __init__(self, sf):
        """Setup the Entity tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Entity_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Entity'

        # Change tag names.
        self['SfCategory'].tag_name =                       'Sf_category'
        self['SfFramecode'].tag_name =                      'Sf_framecode'
        self['EntityID'].tag_name =                         'ID'
        self['BMRBCode'].tag_name =                         'BMRB_code'
        self['Name'].tag_name =                             'Name'
        self['Type'].tag_name =                             'Type'
        self['PolymerCommonType'].tag_name =                'Polymer_common_type'
        self['PolymerType'].tag_name =                      'Polymer_type'
        self['PolymerTypeDetails'].tag_name =               'Polymer_type_details'
        self['PolymerStrandID'].tag_name =                  'Polymer_strand_ID'
        self['PolymerSeqOneLetterCodeCan'].tag_name =       'Polymer_seq_one_letter_code_can'
        self['PolymerSeqOneLetterCode'].tag_name =          'Polymer_seq_one_letter_code'
        self['TargetIdentifier'].tag_name =                 'Target_identifier'
        self['PolymerAuthorDefinedSeq'].tag_name =          'Polymer_author_defined_seq'
        self['PolymerAuthorSeqDetails'].tag_name =          'Polymer_author_seq_details'
        self['AmbiguousConformationalStates'].tag_name =    'Ambiguous_conformational_states'
        self['AmbiguousChemCompSites'].tag_name =           'Ambiguous_chem_comp_sites'
        self['NstdMonomer'].tag_name =                      'Nstd_monomer'
        self['NstdChirality'].tag_name =                    'Nstd_chirality'
        self['NstdLinkage'].tag_name =                      'Nstd_linkage'
        self['NonpolymerCompID'].tag_name =                 'Nonpolymer_comp_ID'
        self['NonpolymerCompLabel'].tag_name =              'Nonpolymer_comp_label'
        self['NumberOfMonomers'].tag_name =                 'Number_of_monomers'
        self['NumberOfNonpolymerComponents'].tag_name =     'Number_of_nonpolymer_components'
        self['Paramagnetic'].tag_name =                     'Paramagnetic'
        self['ThiolState'].tag_name =                       'Thiol_state'
        self['SrcMethod'].tag_name =                        'Src_method'
        self['ParentEntityID'].tag_name =                   'Parent_entity_ID'
        self['Fragment'].tag_name =                         'Fragment'
        self['Mutation'].tag_name =                         'Mutation'
        self['ECNumber'].tag_name =                         'EC_number'
        self['CalcIsoelectricPoint'].tag_name =             'Calc_isoelectric_point'
        self['FormulaWeight'].tag_name =                    'Formula_weight'
        self['FormulaWeightExptl'].tag_name =               'Formula_weight_exptl'
        self['FormulaWeightExptlMeth'].tag_name =           'Formula_weight_exptl_meth'
        self['Details'].tag_name =                          'Details'
        self['DBQueryDate'].tag_name =                      'DB_query_date'
        self['DBQueryRevisedLastDate'].tag_name =           'DB_query_revised_last_date'



class EntityCompIndex_v3_1(EntityCompIndex):
    """v3.1 EntityCompIndex tag category."""

    def __init__(self, sf):
        """Setup the EntityCompIndex_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(EntityCompIndex_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Entity_comp_index'

        # Change tag names.
        self['EntityCompIndexID'].tag_name =    'ID'
        self['AuthSeqID'].tag_name =            'Auth_seq_ID'
        self['CompID'].tag_name =               'Comp_ID'
        self['CompLabel'].tag_name =            'Comp_label'
        self['EntityID'].tag_name =             'Entity_ID'
