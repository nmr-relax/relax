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


    def add(self, res_nums=None, res_names=None, atom_names=None, s2=None, s2_err=None, s2f=None, s2f_err=None, s2s=None, s2s_err=None, te=None, te_err=None, tf=None, tf_err=None, ts=None, ts_err=None, rex=None, rex_err=None):
        """Add relaxation data to the data nodes.

        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword s2:            The S2 values.
        @type s2:               list of float
        @keyword s2_err:        The S2 errors.
        @type s2_err:           list of float
        @keyword s2f:           The S2f values.
        @type s2f:              list of float
        @keyword s2f_err:       The S2f errors.
        @type s2f_err:          list of float
        @keyword s2s:           The S2s values.
        @type s2s:              list of float
        @keyword s2s_err:       The S2s errors.
        @type s2s_err:          list of float
        @keyword te:            The te values.
        @type te:               list of float
        @keyword te_err:        The te errors.
        @type te_err:           list of float
        @keyword tf:            The tf values.
        @type tf:               list of float
        @keyword tf_err:        The tf errors.
        @type tf_err:           list of float
        @keyword ts:            The ts values.
        @type ts:               list of float
        @keyword ts_err:        The ts errors.
        @type ts_err:           list of float
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the model-free data')
        no_missing(res_names, 'residue names of the model-free data')
        no_missing(atom_names, 'atom names of the model-free data')

        # Object names.
        names = ['res_nums', 'res_names', 'atom_names', 's2', 's2_err', 's2f', 's2f_err', 's2s', 's2s_err', 'te', 'te_err', 'tf', 'tf_err', 'ts', 'ts_err', 'rex', 'rex_err']

        # Number of elements.
        N = len(res_nums)

        # Loop over the objects.
        for name in names:
            # Get the object.
            obj = locals()[name]

            # None objects.
            if obj == None:
                obj = [None] * N

            # Check the length.
            if len(obj) != N:
                raise NameError, "The number of elements in the '%s' arg does not match that of 'res_nums'." % name

            # Place the args into the namespace, translating for BMRB.
            setattr(self, name, translate(obj))

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

        # Keys and objects.
        info = [
            ['SeqID',               'res_nums'],
            ['CompID',              'res_names'],
            ['AtomID',              'atom_names'],
            ['OrderParamVal',       's2'],
            ['OrderParamValErr',    's2_err'],
            ['TauEVal',             'te'],
            ['TauEValErr',          'te_err'],
            ['TauFVal',             'tf'],
            ['TauFValErr',          'tf_err'],
            ['TauSVal',             'ts'],
            ['TauSValErr',          'ts_err'],
            ['RexVal',              'rex'],
            ['RexValErr',           'rex_err'],
            ['Sf2Val',              's2f'],
            ['Sf2ValErr',           's2f_err'],
            ['Ss2Val',              's2s'],
            ['Ss2ValErr',           's2s_err']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

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
        self.tag_names['OrderParamVal'] = 'S2_value'
        self.tag_names['OrderParamValErr'] = 'S2_value_fit_error'
        self.tag_names['TauEVal'] = 'Tau_e_value'
        self.tag_names['TauEValErr'] = 'Tau_e_value_fit_error'
        self.tag_names['TauFVal'] = 'Tau_f_value'
        self.tag_names['TauFValErr'] = 'Tau_f_value_fit_error'
        self.tag_names['TauSVal'] = 'Tau_s_value'
        self.tag_names['TauSValErr'] = 'Tau_s_value_fit_error'
        self.tag_names['RexVal'] = None
        self.tag_names['RexValErr'] = None
        self.tag_names['Sf2Val'] = 'S2f_value'
        self.tag_names['Sf2ValErr'] = 'S2f_value_fit_error'
        self.tag_names['Ss2Val'] = 'S2s_value'
        self.tag_names['Ss2ValErr'] = 'S2s_value_fit_error'
