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
"""The entity saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#entity.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class EntitySaveframe(BaseSaveframe):
    """The entity saveframe class."""

    # Class variables.
    label = 'entity'
    sf_label = 'entity'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Entity(self))
        self.tag_categories.append(EntityCompIndex(self))



class Entity(TagCategoryFree):
    """Base class for the Entity tag category."""

    def __init__(self, sf):
        """Setup the Entity tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Entity, self).__init__(sf)

        # Add the tag info.
        self.add(key='EntityID',                        var_name='count_str',                       format='int')
        self.add(key='BMRBCode',                        var_name='bmrb_code',                       format='str')
        self.add(key='Name',                            var_name='mol_name',                        format='str')
        self.add(key='Type',                            var_name='mol_type',                        format='str')
        self.add(key='PolymerCommonType',               var_name='polymer_common_type',             format='str')
        self.add(key='PolymerType',                     var_name='polymer_type',                    format='str',    allowed=['DNA/RNA hybrid', 'polydeoxyribonucleotide', 'polypeptide(D)', 'polypeptide(L)', 'polyribonucleotide', 'polysaccharide(D)', 'polysaccharide(L)'])
        self.add(key='PolymerTypeDetails',              var_name='polymer_type_details',            format='str')
        self.add(key='PolymerStrandID',                 var_name='polymer_strand_id',               format='str')
        self.add(key='PolymerSeqOneLetterCodeCan',      var_name='polymer_seq_one_letter_code_can', format='str')
        self.add(key='PolymerSeqOneLetterCode',         var_name='polymer_seq_one_letter_code',     format='str')
        self.add(key='TargetIdentifier',                var_name='target_identifier',               format='str')
        self.add(key='PolymerAuthorDefinedSeq',         var_name='polymer_author_defined_seq',      format='str')
        self.add(key='PolymerAuthorSeqDetails',         var_name='polymer_author_seq_details',      format='str')
        self.add(key='AmbiguousConformationalStates',   var_name='ambiguous_conformational_states', format='str')
        self.add(key='AmbiguousChemCompSites',          var_name='ambiguous_chem_comp_sites',       format='str')
        self.add(key='NstdMonomer',                     var_name='nstd_monomer',                    format='str')
        self.add(key='NstdChirality',                   var_name='nstd_chirality',                  format='str')
        self.add(key='NstdLinkage',                     var_name='nstd_linkage',                    format='str')
        self.add(key='NonpolymerCompID',                var_name='nonpolymer_comp_id',              format='str')
        self.add(key='NonpolymerCompLabel',             var_name='nonpolymer_comp_label',           format='str')
        self.add(key='NumberOfMonomers',                var_name='number_of_monomers',              format='int')
        self.add(key='NumberOfNonpolymerComponents',    var_name='number_of_nonpolymer_components', format='int')
        self.add(key='Paramagnetic',                    var_name='paramagnetic',                    format='str')
        self.add(key='ThiolState',                      var_name='thiol_state',                     format='str')
        self.add(key='SrcMethod',                       var_name='src_method',                      format='str')
        self.add(key='ParentEntityID',                  var_name='parent_entity_id',                format='int')
        self.add(key='Fragment',                        var_name='fragment',                        format='str')
        self.add(key='Mutation',                        var_name='mutation',                        format='str')
        self.add(key='ECNumber',                        var_name='ec_number',                       format='str')
        self.add(key='CalcIsoelectricPoint',            var_name='calc_isoelectric_point',          format='float')
        self.add(key='FormulaWeight',                   var_name='molecular_weight',                format='float')
        self.add(key='FormulaWeightExptl',              var_name='molecular_weight_exptl',          format='float')
        self.add(key='FormulaWeightExptlMeth',          var_name='molecular_weight_exptl_meth',     format='str')
        self.add(key='Details',                         var_name='details',                         format='str')
        self.add(key='DBQueryDate',                     var_name='db_query_date',                   format='str')
        self.add(key='DBQueryRevisedLastDate',          var_name='db_query_revised_last_date',      format='str')



class EntityCompIndex(TagCategory):
    """Base class for the EntityCompIndex tag category."""

    def __init__(self, sf):
        """Setup the Entity tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(EntityCompIndex, self).__init__(sf)

        # Add the tag info.
        self.add(key='EntityCompIndexID',   var_name='res_nums',    format='int')
        self.add(key='AuthSeqID',           var_name='seq_nums',    format='str')
        self.add(key='CompID',              var_name='res_names',   format='str')
        self.add(key='CompLabel',           var_name='chem_comp',   format='str')
        self.add(key='EntityID',            var_name='count_str',   format='int')
