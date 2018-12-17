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
"""The model_free saveframe category (used to be called order_parameters).

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#order_parameters
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class ModelFreeSaveframe(BaseSaveframe):
    """The Order parameters saveframe class."""

    # Class variables.
    sf_label = 'S2_parameters'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(ModelFreeList(self))
        self.tag_categories.append(ModelFreeExperiment(self))
        self.tag_categories.append(ModelFreeSoftware(self))
        self.tag_categories.append(ModelFree(self))


class ModelFreeList(TagCategoryFree):
    """Base class for the ModelFreeList tag category."""

    def __init__(self, sf):
        """Setup the ModelFreeList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeList, self).__init__(sf)

        # Add the tag info.
        self.add(key='ModelFreeListID',               tag_name='id',                            var_name='count_str',               format='int')
        self.add(key='SampleConditionListID',         tag_name='Sample_condition_list_ID',      var_name='sample_cond_list_id')
        self.add(key='SampleConditionListLabel',      tag_name='Sample_conditions_label',       var_name='sample_cond_list_label',  default='$conditions_1')
        self.add(key='TaueValUnits',                  tag_name='Tau_e_value_units',             var_name='te_units',                default='s')
        self.add(key='TaufValUnits',                  tag_name='Tau_f_value_units',             var_name='tf_units',                default='s')
        self.add(key='TausValUnits',                  tag_name='Tau_s_value_units',             var_name='ts_units',                default='s')
        self.add(key='GlobalChiSquaredFitVal',        tag_name='Global_chi_squared_fit_val',    var_name='global_chi2',             format='float')
        self.add(key='Details',                       tag_name='Details',                       var_name='details')



class ModelFreeExperiment(TagCategory):
    """Base class for the ModelFreeExperiment tag category."""

    def __init__(self, sf):
        """Setup the ModelFreeExperiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeExperiment, self).__init__(sf)

        # Add the tag info.
        self.add(key='SampleLabel', tag_name='Sample_label',    var_name='sample_label',    default='$sample_1')



class ModelFreeSoftware(TagCategory):
    """Base class for the ModelFreeSoftware tag category."""

    # The category name.
    tag_category_label = 'Model_free_software'

    def __init__(self, sf):
        """Setup the ModelFreeSoftware tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeSoftware, self).__init__(sf)

        # Add the tag info.
        self.add(key='SoftwareID',      tag_name='Software_ID',         var_name='software_ids')
        self.add(key='SoftwareLabel',   tag_name='Software_label',      var_name='software_labels')
        self.add(key='ModelFreeListID', tag_name='Model_free_list_ID',  var_name='count_str',       format='int')



class ModelFree(TagCategory):
    """Base class for the ModelFree tag category."""

    def __init__(self, sf):
        """Setup the ModelFree tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFree, self).__init__(sf)

        # The list of allowed model-free models.
        allowed_models = ['',
                          'Rex',
                          'S2',
                          'S2, te',
                          'S2, Rex',
                          'S2, te, Rex',
                          'S2f, S2, ts',
                          'S2f, S2s, ts',
                          'S2f, tf, S2, ts',
                          'S2f, tf, S2s, ts',
                          'S2f, S2, ts, Rex',
                          'S2f, S2s, ts, Rex',
                          'S2f, tf, S2, ts, Rex',
                          'S2f, tf, S2s, ts, Rex'
                          'tm',
                          'tm, Rex',
                          'tm, S2',
                          'tm, S2, te',
                          'tm, S2, Rex',
                          'tm, S2, te, Rex',
                          'tm, S2f, S2, ts',
                          'tm, S2f, S2s, ts',
                          'tm, S2f, tf, S2, ts',
                          'tm, S2f, tf, S2s, ts',
                          'tm, S2f, S2, ts, Rex',
                          'tm, S2f, S2s, ts, Rex',
                          'tm, S2f, tf, S2, ts, Rex',
                          'tm, S2f, tf, S2s, ts, Rex'
        ]

        # Add the tag info.
        self.add(key='ModelFreeID',         tag_name='id',                          var_name='data_ids',            format='int')
        self.add(key='AssemblyAtomID',      tag_name='Assembly_atom_ID',            var_name='assembly_atom_ids')
        self.add(key='EntityAssemblyID',    tag_name='Entity_assembly_ID',          var_name='entity_assembly_ids')
        self.add(key='EntityID',            tag_name='Entity_ID',                   var_name='entity_ids',          format='int',   missing=False)
        self.add(key='CompIndexID',         tag_name='Residue_seq_code',            var_name='res_nums',            format='int',   missing=False)
        self.add(key='CompID',              tag_name='Residue_label',               var_name='res_names',           missing=False)
        self.add(key='AtomID',              tag_name='Atom_name',                   var_name='atom_names',          missing=False)
        self.add(key='AtomType',            tag_name='Atom_type',                   var_name='atom_types')
        self.add(key='AtomIsotopeNumber',   tag_name='Atom_isotope_number',         var_name='isotope',             format='int')
        self.add(key='BondLengthVal',       tag_name=None,                          var_name=None,                  format='float')
        self.add(key='S2Val',               tag_name='S2_value',                    var_name='s2',                  format='float')
        self.add(key='S2ValErr',            tag_name='S2_value_fit_error',          var_name='s2_err',              format='float')
        self.add(key='S2fVal',              tag_name='S2f_value',                   var_name='s2f',                 format='float')
        self.add(key='S2fValErr',           tag_name='S2f_value_fit_error',         var_name='s2f_err',             format='float')
        self.add(key='S2sVal',              tag_name='S2s_value',                   var_name='s2s',                 format='float')
        self.add(key='S2sValErr',           tag_name='S2s_value_fit_error',         var_name='s2s_err',             format='float')
        self.add(key='LocalTauCVal',        tag_name=None,                          var_name=None,                  format='float')
        self.add(key='LocalTauCValErr',     tag_name=None,                          var_name=None,                  format='float')
        self.add(key='TauEVal',             tag_name='Tau_e_value',                 var_name='te',                  format='float')
        self.add(key='TauEValErr',          tag_name='Tau_e_value_fit_error',       var_name='te_err',              format='float')
        self.add(key='TauFVal',             tag_name='Tau_f_value',                 var_name='tf',                  format='float')
        self.add(key='TauFValErr',          tag_name='Tau_f_value_fit_error',       var_name='tf_err',              format='float')
        self.add(key='TauSVal',             tag_name='Tau_s_value',                 var_name='ts',                  format='float')
        self.add(key='TauSValErr',          tag_name='Tau_s_value_fit_error',       var_name='ts_err',              format='float')
        self.add(key='RexVal',              tag_name='Rex_value',                   var_name='rex',                 format='float')
        self.add(key='RexValErr',           tag_name='Rex_error',                   var_name='rex_err',             format='float')
        self.add(key='ChiSquaredVal',       tag_name='SSE_val',                     var_name='chi2',                format='float')
        self.add(key='ModelFit',            tag_name='Model_fit',                   var_name='model_fit',           allowed=allowed_models)
