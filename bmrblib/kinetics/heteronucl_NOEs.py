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
"""The Heteronuclear NOE data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class HeteronuclNOESaveframe(BaseSaveframe):
    """The Heteronuclear NOE data saveframe class."""

    def pre_ops(self):
        """Perform some saveframe specific operations prior to XML creation."""

        # The saveframe description.
        self.sf_framecode = '%s MHz heteronuclear NOE %s' % (self.frq, self.count)



class HeteronuclNOEList(TagCategoryFree):
    """Base class for the HeteronuclNOEList tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEList, self).__init__(sf)

        # Add the tag info.
        self.add(key='EntryID',                  var_name='entry_id',                   format='str')
        self.add(key='HeteronuclNOEListID',      var_name='count_str',                  format='int')
        self.add(key='DataFileName',             var_name='data_file_name',             format='str')
        self.add(key='SampleConditionListID',    var_name='sample_cond_list_id',        format='int')
        self.add(key='SampleConditionListLabel', var_name='sample_cond_list_label',     format='str',  default='$conditions_1')
        self.add(key='SpectrometerFrequency1H',  var_name='frq',                        format='float')
        self.add(key='TempCalibrationMethod',    var_name='temp_calibration',           format='str',  missing=False)
        self.add(key='TempControlMethod',        var_name='temp_control',               format='str',  missing=False)
        self.add(key='HeteronuclearNOEValType',  var_name='peak_intensity_type',        format='str')
        self.add(key='NOERefVal',                var_name='noe_ref_val',                format='float')
        self.add(key='NOERefDescription',        var_name='noe_ref_description',        format='str')
        self.add(key='Details',                  var_name='details',                    format='str')
        self.add(key='TextDataFormat',           var_name='text_data_format',           format='str')
        self.add(key='TextData',                 var_name='text_data',                  format='str')



class HeteronuclNOEExperiment(TagCategory):
    """Base class for the HeteronuclNOEExperiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEExperiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEExperiment, self).__init__(sf)

        # Add the tag info.
        self.add(key='ExperimentID',        var_name='experiment_id',          format='int')
        self.add(key='ExperimentName',      var_name='experiment_name',        format='str')
        self.add(key='SampleID',            var_name='sample_id',              format='int')
        self.add(key='SampleLabel',         var_name='sample_label',           format='str', default='$sample_1')
        self.add(key='SampleState',         var_name='sample_state',           format='str')
        self.add(key='EntryID',             var_name='entry_id',               format='str')
        self.add(key='HeteronuclNOEListID', var_name='heteronucl_noe_list_id', format='int')



class HeteronuclNOESoftware(TagCategory):
    """Base class for the HeteronuclNOESoftware tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOESoftware tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOESoftware, self).__init__(sf)

        # Add the tag info.
        self.add(key='SoftwareID',          var_name='software_id',            format='int')
        self.add(key='SoftwareLabel',       var_name='software_label',         format='str')
        self.add(key='MethodID',            var_name='method_id',              format='int')
        self.add(key='MethodLabel',         var_name='method_label',           format='str')
        self.add(key='EntryID',             var_name='entry_id',               format='str')
        self.add(key='HeteronuclNOEListID', var_name='heteronucl_noe_list_id', format='int')


class HeteronuclNOE(TagCategory):
    """Base class for the HeteronuclNOE tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOE tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOE, self).__init__(sf)

        # Add the tag info.
        self.add(key='HeteronuclNOEID',       var_name='data_ids',                  format='int')
        self.add(key='AssemblyAtomID1',       var_name='assembly_atom_ids',         format='int')
        self.add(key='EntityAssemblyID1',     var_name='entity_assembly_ids',       format='int')
        self.add(key='EntityID1',             var_name='entity_ids',                format='int')
        self.add(key='CompIndexID1',          var_name='res_nums',                  format='int')
        self.add(key='SeqID1',                var_name='seq_id',                    format='int')
        self.add(key='CompID1',               var_name='res_names',                 format='str')
        self.add(key='AtomID1',               var_name='atom_names',                format='str')
        self.add(key='AtomType1',             var_name='atom_types',                format='str')
        self.add(key='AtomIsotopeNumber1',    var_name='isotope',                   format='int')
        self.add(key='AssemblyAtomID2',       var_name='assembly_atom_ids_2',       format='int')
        self.add(key='EntityAssemblyID2',     var_name='entity_assembly_ids_2',     format='int')
        self.add(key='EntityID2',             var_name='entity_ids_2',              format='int')
        self.add(key='CompIndexID2',          var_name='res_nums_2',                format='int')
        self.add(key='SeqID2',                var_name='seq_id_2',                  format='int')
        self.add(key='CompID2',               var_name='res_names_2',               format='str')
        self.add(key='AtomID2',               var_name='atom_names_2',              format='str')
        self.add(key='AtomType2',             var_name='atom_types_2',              format='str')
        self.add(key='AtomIsotopeNumber2',    var_name='isotope_2',                 format='int')
        self.add(key='Val',                   var_name='data',                      format='float')
        self.add(key='ValErr',                var_name='errors',                    format='float')
        self.add(key='ResonanceID1',          var_name='resonance_id',              format='int')
        self.add(key='ResonanceID2',          var_name='resonance_id_2',            format='int')
        self.add(key='AuthEntityAssemblyID1', var_name='auth_entity_assembly_id',   format='str')
        self.add(key='AuthSeqID1',            var_name='auth_seq_id',               format='str')
        self.add(key='AuthCompID1',           var_name='auth_comp_id',              format='str')
        self.add(key='AuthAtomID1',           var_name='auth_atom_id',              format='str')
        self.add(key='AuthEntityAssemblyID2', var_name='auth_entity_assembly_id_2', format='str')
        self.add(key='AuthSeqID2',            var_name='auth_seq_id_2',             format='str')
        self.add(key='AuthCompID2',           var_name='auth_comp_id_2',            format='str')
        self.add(key='AuthAtomID2',           var_name='auth_atom_id_2',            format='str')
        self.add(key='EntryID',               var_name='entry_id',                  format='str')
        self.add(key='HeteronuclNOEListID',   var_name='count_str',                 format='int')
