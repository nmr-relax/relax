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


class ExperimentSaveframe(BaseSaveframe):
    """The Order parameters saveframe class."""

    # Class variables.
    sf_label = 'experiment_list'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(ExperimentList(self))
        self.tag_categories.append(Experiment(self))


class ExperimentList(TagCategoryFree):
    """Base class for the ExperimentList tag category."""

    def __init__(self, sf):
        """Setup the ExperimentList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ExperimentList, self).__init__(sf)

        # Add the tag info.
        self.add(key='ExperimentListID',    tag_name='ID',      var_name='count_str',   format='int')
        self.add(key='Details',             tag_name='Details', var_name='details',     format='str')



class Experiment(TagCategory):
    """Base class for the Experiment tag category."""

    def __init__(self, sf):
        """Setup the Experiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Experiment, self).__init__(sf)

        # Add the tag info.
        self.add(key='ExperimentID',                tag_name='ID',                              var_name='data_ids',            format='int')
        self.add(key='Name',                        tag_name='Name',                            var_name='name',        format='str')
        self.add(key='RawDataFlag',                 tag_name='Raw_data_flag',                   var_name='data_flag',             format='str', default='yes')
        self.add(key='NMRSpecExptID',               tag_name='NMR_spec_expt_ID',                var_name='nmr_spec_expt_id',             format='int')
        self.add(key='NMRSpecExptLabel',            tag_name='NMR_spec_expt_label',             var_name='nmr_spec_expt_label',             format='str')
        self.add(key='SampleID',                    tag_name='Sample_ID',                       var_name='sample_id',             format='int', default=1)
        self.add(key='SampleLabel',                 tag_name='Sample_label',                    var_name='sample_label',             format='str', default='$sample_1')
        self.add(key='SampleState',                 tag_name='Sample_state',                    var_name='sample_state',             format='str')
        self.add(key='SampleVolume',                tag_name='Sample_volume',                   var_name='sample_volume',             format='float')
        self.add(key='SampleVolumeUnits',           tag_name='Sample_volume_units',             var_name='sample_volume_units',             format='str')
        self.add(key='SampleConditionListID',       tag_name='Sample_condition_list_ID',        var_name='sample_cond_list_id',             format='int', default=1)
        self.add(key='SampleConditionListLabel',    tag_name='Sample_condition_list_label',     var_name='sample_cond_list_label',             format='str', default='$conditions_1')
        self.add(key='Sample_spinning_rate ',       tag_name='SampleSpinningRate',              var_name='sample_spin_rate',             format='float')
        self.add(key='SampleAngle',                 tag_name='Sample_angle',                    var_name='sample_angle',             format='float')
        self.add(key='NMRTubeType',                 tag_name='NMR_tube_type',                   var_name='nmr_tube_type',             format='str')
        self.add(key='NMRSpectrometerID',           tag_name='NMR_spectrometer_ID',             var_name='spectrometer_ids',             format='int')
        self.add(key='NMRSpectrometerLabel',        tag_name='NMR_spectrometer_label',          var_name='spectrometer_labels',             format='str')
        self.add(key='NMRSpectrometerProbeID',      tag_name='NMR_spectrometer_probe_ID',       var_name='NMR_spectrometer_probe_ID',             format='int')
        self.add(key='NMRSpectrometerProbeLabel',   tag_name='NMR_spectrometer_probe_label',    var_name='NMR_spectrometer_probe_label',             format='str')
        self.add(key='NMRSpectralProcessingID',     tag_name='NMR_spectral_processing_ID',      var_name='NMR_spectral_processing_ID',             format='int')
        self.add(key='NMRSpectralProcessingLabel',  tag_name='NMR_spectral_processing_label',   var_name='NMR_spectral_processing_label',             format='str')
        self.add(key='ExperimentListID',            tag_name='Experiment_list_ID',              var_name='count_str', format='int')
