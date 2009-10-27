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
"""The Heteronuclear T1 data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T1_relaxation.
"""

# relax module imports.
from bmrblib.base_classes import TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.kinetics.relax_base import HeteronuclRxList, RelaxSaveframe, Rx
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class HeteronuclT1Saveframe(RelaxSaveframe):
    """The Heteronuclear T1 data saveframe class."""

    # Saveframe variables.
    label = 'T1'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.r1_inc = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', frq=None, details=None, assembly_atom_ids=None, entity_assembly_ids=None, entity_ids=None, res_nums=None, seq_id=None, res_names=None, atom_names=None, atom_types=None, isotope=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword sample_cond_list_id:       The sample conditions list ID number.
        @type sample_cond_list_id:          str
        @keyword sample_cond_list_label:    The sample conditions list label.
        @type sample_cond_list_label:       str
        @keyword frq:                       The spectrometer proton frequency, in Hz.
        @type frq:                          float
        @keyword details:                   The details tag.
        @type details:                      None or str
        @keyword assembly_atom_ids:         The assembly atom ID numbers.
        @type assembly_atom_ids:            list of int
        @keyword entity_assembly_ids:       The entity assembly ID numbers.
        @type entity_assembly_ids:          list of int
        @keyword entity_ids:                The entity ID numbers.
        @type entity_ids:                   int
        @keyword res_nums:                  The residue number list.
        @type res_nums:                     list of int
        @keyword res_names:                 The residue name list.
        @type res_names:                    list of str
        @keyword atom_names:                The atom name list.
        @type atom_names:                   list of str
        @keyword atom_types:                The atom types as IUPAC element abbreviations.
        @type atom_types:                   list of str
        @keyword isotope:                   The isotope type list, ie 15 for '15N'.
        @type isotope:                      list of int
        @keyword data:                      The relaxation data.
        @type data:                         list of float
        @keyword errors:                    The errors associated with the relaxation data.
        @type errors:                       list of float
        """

        # Check the ID info.
        no_missing(entity_ids, 'entity ID numbers of the ' + repr(int(frq*1e-6)) + ' MHz R1 data')
        no_missing(res_nums, 'residue numbers of the ' + repr(int(frq*1e-6)) + ' MHz R1 data')
        no_missing(res_names, 'residue names of the ' + repr(int(frq*1e-6)) + ' MHz R1 data')
        no_missing(atom_names, 'atom names of the ' + repr(int(frq*1e-6)) + ' MHz R1 data')

        # The number of elements.
        self.N = len(res_nums)

        # Place the args into the namespace.
        self.sample_cond_list_id = translate(sample_cond_list_id)
        self.sample_cond_list_label = translate(sample_cond_list_label)
        self.frq = frq
        self.details = translate(details)

        # Convert to lists and check the lengths.
        for name in ['assembly_atom_ids', 'entity_assembly_ids', 'entity_ids', 'res_nums', 'seq_id', 'res_names', 'atom_names', 'atom_types', 'isotope', 'data', 'errors']:
            # Get the object.
            obj = locals()[name]

            # None objects.
            if obj == None:
                obj = [None] * self.N

            # Check the length.
            if len(obj) != self.N:
                raise NameError("The number of elements in the '%s' arg does not match that of 'res_nums'." % name)

            # Place the args into the namespace, translating for BMRB.
            setattr(self, name, translate(obj))

        # Set up the R1 specific variables.
        self.r1_inc = self.r1_inc + 1
        self.rx_inc_list = translate([self.r1_inc] * self.N)
        self.generate_data_ids(self.N)

        # Set up the version specific variables.
        self.specific_setup()

        # Initialise the save frame.
        self.frame = SaveFrame(title='heteronuclear_'+self.label+'_list_'+repr(self.r1_inc))

        # Create the tag categories.
        self.heteronuclRxlist.create()
        self.heteronuclRxexperiment.create()
        self.heteronuclRxsoftware.create()
        self.Rx.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclT1List(self)
        self.heteronuclRxexperiment = HeteronuclT1Experiment(self)
        self.heteronuclRxsoftware = HeteronuclT1Software(self)
        self.Rx = T1(self)


class HeteronuclT1List(HeteronuclRxList):
    """Base class for the HeteronuclT1List tag category."""

    def create(self):
        """Create the HeteronuclT1List tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # T1 ID number.
        if 'HeteronuclT1ListID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['HeteronuclT1ListID']], tagvalues=[[str(self.sf.r1_inc)]]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListID']], tagvalues=[[self.sf.sample_cond_list_id]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SpectrometerFrequency1H']], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['T1CoherenceType']], tagvalues=[[self.variables['coherence']]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['T1ValUnits']], tagvalues=[['1/s']]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Details']], tagvalues=[[self.sf.details]]))


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
        self.tag_names['SampleConditionListID'] = 'Sample_condition_list_ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_conditions_label'
        self.tag_names['SpectrometerFrequency1H'] = 'Spectrometer_frequency_1H'
        self.tag_names['T1CoherenceType'] = 'T1_coherence_type'
        self.tag_names['T1ValUnits'] = 'T1_value_units'
        self.tag_names['Details'] = 'Details'

        # Class variables.
        self.variables['coherence'] = 'Nz'



class HeteronuclT1Experiment(TagCategory):
    """Base class for the HeteronuclT1Experiment tag category."""

    def create(self, frame=None):
        """Create the HeteronuclT1Experiment tag category."""

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleLabel']], tagvalues=[['$sample_1']]))


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
        self.tag_names['SampleLabel'] = 'Sample_label'


class HeteronuclT1Software(TagCategory):
    """Base class for the HeteronuclT1Software tag category."""

    def create(self):
        """Create the HeteronuclT1Software tag category."""


class T1(Rx):
    """Base class for the T1 tag category."""

