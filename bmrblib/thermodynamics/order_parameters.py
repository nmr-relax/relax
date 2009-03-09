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
"""The Heteronuclear NOE data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.misc import no_missing, translate
from bmrblib.tag_category import TagCategory
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class OrderParameterSaveframe:
    """The Order parameters data saveframe class."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, res_nums=None, res_names=None, atom_names=None):
        """Add relaxation data to the data nodes.

        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the model-free data')
        no_missing(res_names, 'residue names of the model-free data')
        no_missing(atom_names, 'atom names of the model-free data')

        # Place the args into the namespace.
        self.res_nums = translate(res_nums)
        self.res_names = translate(res_names)
        self.atom_names = translate(atom_names)

        # Initialise the save frame.
        self.frame = SaveFrame(title='order_parameters')

        # Create the tag categories.
        self.order_parameter_list.create()
        self.order_parameter_experiment.create()
        self.order_parameter_software.create()
        self.order_parameter.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.order_parameter_list = OrderParameterList(self)
        self.order_parameter_experiment = OrderParameterExperiment(self)
        self.order_parameter_software = OrderParameterSoftware(self)
        self.order_parameter = OrderParameter(self)


class OrderParameterList(TagCategory):
    """Base class for the OrderParameterList tag category."""

    def create(self):
        """Create the OrderParameterList tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfCategory']], tagvalues=[['S2_parameters']]))

        # NOE ID number.
        if self.tag_names.has_key('OrderParameterListID'):
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['OrderParameterListID']], tagvalues=[['1']]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))


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


class OrderParameterExperiment(TagCategory):
    """Base class for the OrderParameterExperiment tag category."""

    def create(self):
        """Create the OrderParameterExperiment tag category."""

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


class OrderParameterSoftware(TagCategory):
    """Base class for the OrderParameterSoftware tag category."""

    def create(self):
        """Create the OrderParameterSoftware tag category."""


class OrderParameter(TagCategory):
    """Base class for the OrderParameter tag category."""

    def create(self):
        """Create the OrderParameter tag category."""

        # The relaxation tag names.
        tag_names = []
        missing = []
        for key in ['SeqID', 'CompID', 'AtomID']:
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

        # Add the data.
        table = TagTable(tagnames=tag_names, tagvalues=tag_values)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


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
