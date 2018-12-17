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
"""The Auto relaxation data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#auto_relaxation.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class AutoRelaxationSaveframe(BaseSaveframe):
    """The Auto relaxation data saveframe class."""

    # Class variables.
    name = 'auto'
    sf_label = 'auto_relaxation'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(AutoRelaxationList(self))
        self.tag_categories.append(AutoRelaxationExperiment(self))
        self.tag_categories.append(AutoRelaxationSoftware(self))
        self.tag_categories.append(AutoRelaxation(self))


    def pre_ops(self):
        """Perform some saveframe specific operations prior to XML creation."""

        # The operators of the relaxation superoperator.
        if self.data_type == 'R1':
            self.coherence = 'Iz'
            self.coherence_common_name = 'R1'
        elif self.data_type == 'R2':
            self.coherence = 'I+'
            self.coherence_common_name = 'R2'
        else:
            raise NameError("The data type '%s' is not one of ['R1', 'R2']." % data_type)

        # The saveframe description.
        self.sf_framecode = '%s MHz %s relaxation %s' % (self.frq, self.data_type, self.count)


class AutoRelaxationList(TagCategoryFree):
    """Base class for the AutoRelaxationList tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationList, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_list'

        # Add the tag info.
        self.add(key='EntryID',                  var_name='entry_id',               format='str')
        self.add(key='AutoRelaxationListID',     var_name='count_str',              format='int')
        self.add(key='DataFileName',             var_name='data_file_name',         format='str')
        self.add(key='SampleConditionListID',    var_name='sample_cond_list_id',    format='int')
        self.add(key='SampleConditionListLabel', var_name='sample_cond_list_label', format='str',   default='$conditions_1')
        self.add(key='TempCalibrationMethod',    var_name='temp_calibration',       format='str',   missing=False)
        self.add(key='TempControlMethod',        var_name='temp_control',           format='str',   missing=False)
        self.add(key='SpectrometerFrequency1H',  var_name='frq',                    format='float')
        self.add(key='CommonRelaxationTypeName', var_name='coherence_common_name',  format='str')
        self.add(key='RelaxationCoherenceType',  var_name='coherence',              format='str')
        self.add(key='RelaxationValUnits',       var_name='units',                  format='str',   default='s-1')
        self.add(key='RelaxationValType',        var_name='peak_intensity_type',    format='str',   missing=False)
        self.add(key='RexUnits',                 var_name='rex_units',              format='str')
        self.add(key='Details',                  var_name='details',                format='str')
        self.add(key='TextDataFormat',           var_name='text_data_format',       format='str')
        self.add(key='TextData',                 var_name='text_data',              format='str')



class AutoRelaxationExperiment(TagCategory):
    """Base class for the AutoRelaxationExperiment tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationExperiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationExperiment, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_experiment'

        # Add the tag info.
        self.add(key='ExperimentID',         var_name='experiment_id',         format='int')
        self.add(key='ExperimentName',       var_name='experiment_name',       format='str')
        self.add(key='SampleID',             var_name='sample_id',             format='int')
        self.add(key='SampleLabel',          var_name='sample_label',          format='str', default='$sample_1')
        self.add(key='SampleState',          var_name='sample_state',          format='str')
        self.add(key='EntryID',              var_name='entry_id',              format='str')
        self.add(key='AutoRelaxationListID', var_name='heteronucl_t1_list_id', format='int')



class AutoRelaxationSoftware(TagCategory):
    """Base class for the AutoRelaxationSoftware tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationSoftware tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationSoftware, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_software'

        # Add the tag info.
        self.add(key='SoftwareID',           var_name='software_id',           format='int')
        self.add(key='SoftwareLabel',        var_name='software_label',        format='str')
        self.add(key='MethodID',             var_name='method_id',             format='int')
        self.add(key='MethodLabel',          var_name='method_label',          format='str')
        self.add(key='EntryID',              var_name='entry_id',              format='str')
        self.add(key='AutoRelaxationListID', var_name='heteronucl_t1_list_id', format='int')



class AutoRelaxation(TagCategory):
    """Base class for the AutoRelaxation tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxation, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation'

        # Add the tag info.
        self.add(key='AutoRelaxationID',     var_name='data_ids',                format='int')
        self.add(key='AssemblyID',           var_name='assembly_ids',            format='int')
        self.add(key='AssemblyAtomID',       var_name='assembly_atom_ids',       format='int')
        self.add(key='EntityAssemblyID',     var_name='entity_assembly_ids',     format='int')
        self.add(key='EntityID',             var_name='entity_ids',              format='int',  missing=False)
        self.add(key='CompIndexID',          var_name='res_nums',                format='int',  missing=False)
        self.add(key='SeqID',                var_name='seq_id',                  format='int')
        self.add(key='CompID',               var_name='res_names',               format='str',  missing=False)
        self.add(key='AtomID',               var_name='atom_names',              format='str',  missing=False)
        self.add(key='AtomType',             var_name='atom_types',              format='str')
        self.add(key='AtomIsotopeNumber',    var_name='isotope',                 format='int')
        self.add(key='Val',                  var_name='data',                    format='float')
        self.add(key='ValErr',               var_name='errors',                  format='float')
        self.add(key='RexVal',               var_name='rex_val',                 format='float')
        self.add(key='RexErr',               var_name='rex_err',                 format='float')
        self.add(key='ResonanceID',          var_name='resonance_id',            format='int')
        self.add(key='AuthEntityAssemblyID', var_name='auth_entity_assembly_id', format='str')
        self.add(key='AuthSeqID',            var_name='auth_seq_id',             format='str')
        self.add(key='AuthCompID',           var_name='auth_atom_id',            format='str')
        self.add(key='AuthAtomID',           var_name='auth_atom_id',            format='str')
        self.add(key='EntryID',              var_name='entry_id',                format='str')
        self.add(key='AutoRelaxationListID', var_name='count_str',               format='int')
