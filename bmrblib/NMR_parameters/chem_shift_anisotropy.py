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
"""The chemical shift anisotropy data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#chem_shift_anisotropy
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class ChemShiftAnisotropySaveframe(BaseSaveframe):
    """The chemical shift anisotropy data saveframe class."""

    # Class variables.
    sf_label = 'chem_shift_anisotropy'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(ChemShiftAnisotropy(self))
        self.tag_categories.append(CSAnisotropyExperiment(self))
        self.tag_categories.append(CSAnisotropySoftware(self))
        self.tag_categories.append(CSAnisotropy(self))



class ChemShiftAnisotropy(TagCategoryFree):
    """Base class for the ChemShiftAnisotropy tag category."""

    def __init__(self, sf):
        """Setup the ChemShiftAnisotropy tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ChemShiftAnisotropy, self).__init__(sf)

        # Add the tag info.
        self.add(key='ChemShiftAnisotropyID',       tag_name='ID',                      var_name='count_str',               format='int')
        self.add(key='DataFileName',                tag_name='Data_file_name',          var_name='file_name')
        self.add(key='SampleConditionListLabel',    tag_name='Sample_conditions_label', var_name='sample_cond_list_label',  default='$conditions_1')
        self.add(key='ValUnits',                    tag_name='Val_units',               var_name='units',                   default='ppm')



class CSAnisotropyExperiment(TagCategory):
    """Base class for the CSAnisotropyExperiment tag category."""

    def __init__(self, sf):
        """Setup the CSAnisotropyExperiment tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(CSAnisotropyExperiment, self).__init__(sf)

        # Add the tag info.
        self.add(key='SampleLabel', tag_name='Sample_label',    var_name='sample_label',    default='$sample_1')



class CSAnisotropySoftware(TagCategory):
    """Base class for the CSAnisotropySoftware tag category."""



class CSAnisotropy(TagCategory):
    """Base class for the CSAnisotropy tag category."""

    def __init__(self, sf):
        """Setup the CSAnisotropy tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(CSAnisotropy, self).__init__(sf)

        # Add the tag info.
        self.add(key='CSAnisotropyID',          tag_name='ID',                          var_name='data_ids',            format='int')
        self.add(key='AssemblyAtomID',          tag_name='Assembly_atom_ID',            var_name='assembly_atom_ids')
        self.add(key='EntityAssemblyID',        tag_name='Entity_assembly_ID',          var_name='entity_assembly_ids')
        self.add(key='EntityID',                tag_name='Entity_ID',                   var_name='entity_ids',          format='int')
        self.add(key='CompIndexID',             tag_name='Residue_seq_code',            var_name='res_nums',            format='int')
        self.add(key='SeqID',                   tag_name='Seq_ID',                      var_name='seq_id')
        self.add(key='CompID',                  tag_name='Residue_label',               var_name='res_names')
        self.add(key='AtomID',                  tag_name='Atom_name',                   var_name='atom_names')
        self.add(key='AtomType',                tag_name='Atom_type',                   var_name='atom_types')
        self.add(key='AtomIsotopeNumber',       tag_name='Atom_isotope_number',         var_name='isotope',             format='int')
        self.add(key='Val',                     tag_name='value',                       var_name='csa',                 format='float')
        self.add(key='ValErr',                  tag_name='value_error',                 var_name='csa_error',           format='float')
        self.add(key='ChemShiftAnisotropyID',   tag_name='Chem_shift_anisotropy_ID',    var_name='count_str')
