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
from bmrblib.misc import no_missing, translate
from bmrblib.tag_category import TagCategory
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class HeteronuclT1Saveframe:
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


    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the ' + `int(frq*1e-6)` + ' MHz NOE data')
        no_missing(res_names, 'residue names of the ' + `int(frq*1e-6)` + ' MHz NOE data')
        no_missing(atom_names, 'atom names of the ' + `int(frq*1e-6)` + ' MHz NOE data')

        # Place the args into the namespace.
        self.frq = frq
        self.res_nums = translate(res_nums)
        self.res_names = translate(res_names)
        self.atom_names = translate(atom_names)
        self.data = translate(data)
        self.errors = translate(errors)

        # Set up the R1 specific variables.
        self.r1_inc = self.r1_inc + 1

        # Initialise the save frame.
        self.frame = SaveFrame(title='heteronuclear_'+self.label+'_list_'+`self.r1_inc`)

        # Create the tag categories.
        self.heteronuclT1list.create()
        self.heteronuclT1experiment.create()
        self.heteronuclT1software.create()
        self.T1.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.heteronuclT1list = HeteronuclT1List(self)
        self.heteronuclT1experiment = HeteronuclT1Experiment(self)
        self.heteronuclT1software = HeteronuclT1Software(self)
        self.T1 = T1(self)


    def loop(self):
        """Loop over the T1 saveframes, yielding the relaxation data.

        @return:    The relaxation data consisting of the proton frequency, residue numbers, residue
                    names, atom names, values, and errors.
        @rtype:     tuple of float, list of int, list of str, list of str, list of float, list of
                    float
        """

        # Loop over all datanodes.
        for datanode in self.datanodes:
            # Find the Heteronuclear T1 saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.heteronuclT1list.create_tag_label(self.heteronuclT1list.tag_names['SfCategory']):
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == self.label+'_relaxation':
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Get general info.
            frq = self.heteronuclT1list.read(datanode.tagtables[0])

            # Get the T1 info.
            res_nums, res_names, atom_names, values, errors = self.T1.read(datanode.tagtables[1])

            # Yield the data.
            yield frq, res_nums, res_names, atom_names, values, errors


class HeteronuclT1List(TagCategory):
    """Base class for the HeteronuclT1List tag category."""

    def create(self):
        """Create the HeteronuclT1List tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfCategory']], tagvalues=[[self.sf.label+'_relaxation']]))

        # T1 ID number.
        if self.tag_names.has_key('HeteronuclT1ListID'):
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['HeteronuclT1ListID']], tagvalues=[[str(self.sf.r1_inc)]]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SpectrometerFrequency1H']], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['T1CoherenceType']], tagvalues=[[self.variables['coherence']]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['T1ValUnits']], tagvalues=[['1/s']]))


    def read(self, tagtable):
        """Extract the HeteronuclT1List tag category info.

        @param tagtable:    The HeteronuclT1List tagtable.
        @type tagtable:     Tagtable instance
        @return:            The proton frequency in Hz.
        @rtype:             float
        """

        # The general info.
        frq = float(tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['SpectrometerFrequency1H'])][0]) * 1e6

        # Return the data.
        return frq


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
        self.tag_names['SampleConditionListLabel'] = 'Sample_conditions_label'
        self.tag_names['SpectrometerFrequency1H'] = 'Spectrometer_frequency_1H'
        self.tag_names['T1CoherenceType'] = 'T1_coherence_type'
        self.tag_names['T1ValUnits'] = 'T1_value_units'

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


class T1(TagCategory):
    """Base class for the T1 tag category."""

    def create(self):
        """Create the T1 tag category."""

        # The relaxation tag names.
        tag_names = []
        missing = []
        for key in ['SeqID', 'CompID', 'AtomID', 'Val', 'ValErr']:
            if not self.tag_names.has_key(key):
                missing.append(key)
            else:
                tag_names.append(self.tag_names_full[key])

        # The tag values.
        tag_values = []
        if 'SeqID' not in missing:
            tag_values.append(self.sf.res_nums)
        if 'CompID' not in missing:
            tag_values.append(self.sf.res_names)
        if 'AtomID' not in missing:
            tag_values.append(self.sf.atom_names)
        if 'Val' not in missing:
            tag_values.append(self.sf.data)
        if 'ValErr' not in missing:
            tag_values.append(self.sf.errors)

        # Add the data.
        table = TagTable(tagnames=tag_names, tagvalues=tag_values)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def read(self, tagtable):
        """Extract the T1 tag category info.

        @param tagtable:    The T1 tagtable.
        @type tagtable:     Tagtable instance
        @return:            The residue numbers, residue names, atom names, values, and errors.
        @rtype:             tuple of list of int, list of str, list of str, list of float, list of
                            float
        """

        # The entity info.
        res_nums = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['SeqID'])]
        res_names = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['CompID'])]
        atom_names = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['AtomID'])]
        values = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['Val'])]
        errors = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['ValErr'])]

        # Convert the residue numbers to ints and the values and errors to floats.
        for i in range(len(res_nums)):
            res_nums[i] = int(res_nums[i])
            values[i] = float(res_nums[i])
            errors[i] = float(res_nums[i])

        # Return the data.
        return res_nums, res_names, atom_names, values, errors


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
        self.tag_names['SeqID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['Val'] = self.sf.label+'_value'
        self.tag_names['ValErr'] = self.sf.label+'_value_error'
