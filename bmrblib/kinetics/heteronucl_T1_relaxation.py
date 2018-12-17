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
"""The Heteronuclear T1 data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T1_relaxation.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class HeteronuclT1Saveframe(BaseSaveframe):
    """The Heteronuclear T1 data saveframe class."""



class HeteronuclT1List(TagCategoryFree):
    """Base class for the HeteronuclT1List tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1List tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1List, self).__init__(sf)

        # Add the tag info.
        self.add(key='EntryID',                     var_name='entry_id',                format='str')
        self.add(key='HeteronuclT1ListID',          var_name='count_str',               format='int')
        self.add(key='DataFileName',                var_name='data_file_name',          format='str')
        self.add(key='SampleConditionListID',       var_name='sample_cond_list_id',     format='int')
        self.add(key='SampleConditionListLabel',    var_name='sample_cond_list_label',  format='str',  default='$conditions_1')
        self.add(key='SpectrometerFrequency1H',     var_name='frq',                     format='float')
        self.add(key='T1CoherenceType',             var_name='coherence',               format='str',  default='Nz')
        self.add(key='T1ValUnits',                  var_name='units',                   format='str',  default='1/s')
        self.add(key='Details',                     var_name='details',                 format='str')
        self.add(key='TextDataFormat',              var_name='text_data_format',        format='str')
        self.add(key='TextData',                    var_name='text_data',               format='str')



class HeteronuclT1Experiment(TagCategory):
    """Base class for the HeteronuclT1Experiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Experiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Experiment, self).__init__(sf)

        # Add the tag info.
        self.add(key='ExperimentID',        var_name='experiment_id',           format='int')
        self.add(key='ExperimentName',      var_name='experiment_name',         format='str')
        self.add(key='SampleID',            var_name='sample_id',               format='int')
        self.add(key='SampleLabel',         var_name='sample_label',            format='str',    default='$sample_1')
        self.add(key='SampleState',         var_name='sample_state',            format='str')
        self.add(key='EntryID',             var_name='entry_id',                format='str')
        self.add(key='HeteronuclT1ListID',  var_name='heteronucl_t1_list_id',   format='int')



class HeteronuclT1Software(TagCategory):
    """Base class for the HeteronuclT1Software tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Software tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Software, self).__init__(sf)

        # Add the tag info.
        self.add(key='SoftwareID',          var_name='software_id',             format='int')
        self.add(key='SoftwareLabel',       var_name='software_label',          format='str')
        self.add(key='MethodID',            var_name='method_id',               format='int')
        self.add(key='MethodLabel',         var_name='method_label',            format='str')
        self.add(key='EntryID',             var_name='entry_id',                format='str')
        self.add(key='HeteronuclT1ListID',  var_name='heteronucl_t1_list_id',   format='int')



class T1(TagCategory):
    """Base class for the T1 tag category."""

    def __init__(self, sf):
        """Setup the T1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(T1, self).__init__(sf)

        # Add the tag info.
        self.add(key='RxID',                    var_name='data_ids',                format='int')
        self.add(key='AssemblyAtomID',          var_name='assembly_atom_ids',       format='int')
        self.add(key='EntityAssemblyID',        var_name='entity_assembly_ids',     format='int')
        self.add(key='EntityID',                var_name='entity_ids',              format='int')
        self.add(key='CompIndexID',             var_name='res_nums',                format='int')
        self.add(key='SeqID',                   var_name='seq_id',                  format='int')
        self.add(key='CompID',                  var_name='res_names',               format='str')
        self.add(key='AtomID',                  var_name='atom_names',              format='str')
        self.add(key='AtomType',                var_name='atom_types',              format='str')
        self.add(key='AtomIsotopeNumber',       var_name='isotope',                 format='int')
        self.add(key='Val',                     var_name='data',                    format='float')
        self.add(key='ValErr',                  var_name='errors',                  format='float')
        self.add(key='ResonanceID',             var_name='resonance_id',            format='int')
        self.add(key='AuthEntityAssemblyID',    var_name='auth_entity_assembly_id', format='str')
        self.add(key='AuthSeqID',               var_name='auth_seq_id',             format='str')
        self.add(key='AuthCompID',              var_name='auth_comp_id',            format='str')
        self.add(key='AuthAtomID',              var_name='auth_atom_id',            format='str')
        self.add(key='EntryID',                 var_name='entry_id',                format='str')
        self.add(key='HeteronuclT1ListID',      var_name='heteronucl_t1_list_id',   format='int')
