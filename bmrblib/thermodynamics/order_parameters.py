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
"""The order parameter saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#order_parameters
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class OrderParameterSaveframe(BaseSaveframe):
    """The Order parameters saveframe class."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, res_nums=None, res_names=None, atom_names=None, s2=None, s2_err=None, s2f=None, s2f_err=None, s2s=None, s2s_err=None, te=None, te_err=None, tf=None, tf_err=None, ts=None, ts_err=None, rex=None, rex_err=None, rex_frq=None, chi2=None):
        """Add relaxation data to the data nodes.

        Note that units of 1/s are actually rad/s in NMR.  This is the hidden radian unit, which if
        not present would mean that the units would be Hz.  For more details, see
        https://mail.gna.org/public/relax-users/2009-01/msg00000.html.


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
        @keyword te:            The te values (in rad/s units).
        @type te:               list of float
        @keyword te_err:        The te errors (in rad/s units).
        @type te_err:           list of float
        @keyword tf:            The tf values (in rad/s units).
        @type tf:               list of float
        @keyword tf_err:        The tf errors (in rad/s units).
        @type tf_err:           list of float
        @keyword ts:            The ts values (in rad/s units).
        @type ts:               list of float
        @keyword ts_err:        The ts errors (in rad/s units).
        @type ts_err:           list of float
        @keyword rex:           The Rex values (in rad/s units for the field strength specified in
                                rex_frq).
        @type rex:              list of float
        @keyword rex_err:       The Rex errors (in rad/s units for the field strength specified in
                                rex_frq).
        @type rex_err:          list of float
        @keyword rex_frq:       The 1H spectrometer frequency in Hz that the Rex values are reported
                                in.
        @type rex_frq:          float
        @keyword chi2:          The optimised chi-squared value.
        @type chi2:             float
        """

        # Set up the version specific variables.
        self.specific_setup()

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the model-free data')
        no_missing(res_names, 'residue names of the model-free data')
        no_missing(atom_names, 'atom names of the model-free data')

        # The Rex frequency in MHz.
        if rex:
            # Check.
            if not rex_frq:
                raise NameError("The rex_frq arg must be supplied if the rex values are supplied.")

            # Convert to MHz.
            self.rex_frq = str(rex_frq / 1e6)

        # No Rex.
        else:
            self.rex_frq = None

        # Number of elements.
        N = len(res_nums)

        # Object names.
        names = ['res_nums', 'res_names', 'atom_names', 's2', 's2_err', 's2f', 's2f_err', 's2s', 's2s_err', 'te', 'te_err', 'tf', 'tf_err', 'ts', 'ts_err', 'rex', 'rex_err', 'chi2']

        # Loop over the objects.
        for name in names:
            # Get the object.
            obj = locals()[name]

            # None objects.
            if obj == None:
                obj = [None] * N

            # Check the length.
            if len(obj) != N:
                raise NameError("The number of elements in the '%s' arg does not match that of 'res_nums'." % name)

            # Place the args into the namespace, translating for BMRB.
            setattr(self, name, translate(obj))

        # The ID numbers.
        self.generate_data_ids(N)

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


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = ['S2_parameters']


class OrderParameterList(TagCategory):
    """Base class for the OrderParameterList tag category."""

    def create(self):
        """Create the OrderParameterList tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # Model-free analysis ID number.
        if 'OrderParameterListID' in self.tag_names:
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
            ['OrderParamID',    'data_ids'],
            ['CompIndexID',     'res_nums'],
            ['CompID',          'res_names'],
            ['AtomID',          'atom_names'],
            ['S2Val',           's2'],
            ['S2ValErr',        's2_err'],
            ['S2fVal',          's2f'],
            ['S2fValErr',       's2f_err'],
            ['S2sVal',          's2s'],
            ['S2sValErr',       's2s_err'],
            ['TauEVal',         'te'],
            ['TauEValErr',      'te_err'],
            ['TauFVal',         'tf'],
            ['TauFValErr',      'tf_err'],
            ['TauSVal',         'ts'],
            ['TauSValErr',      'ts_err'],
            ['RexVal',          'rex'],
            ['RexValErr',       'rex_err'],
            ['ChiSquaredVal',   'chi2']
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
        self.tag_names['OrderParamID'] = None
        self.tag_names['CompIndexID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['S2Val'] = 'S2_value'
        self.tag_names['S2ValErr'] = 'S2_value_fit_error'
        self.tag_names['TauEVal'] = 'Tau_e_value'
        self.tag_names['TauEValErr'] = 'Tau_e_value_fit_error'
        self.tag_names['TauFVal'] = 'Tau_f_value'
        self.tag_names['TauFValErr'] = 'Tau_f_value_fit_error'
        self.tag_names['TauSVal'] = 'Tau_s_value'
        self.tag_names['TauSValErr'] = 'Tau_s_value_fit_error'
        self.tag_names['RexVal'] = None
        self.tag_names['RexValErr'] = None
        self.tag_names['S2fVal'] = 'S2f_value'
        self.tag_names['S2fValErr'] = 'S2f_value_fit_error'
        self.tag_names['S2sVal'] = 'S2s_value'
        self.tag_names['S2sValErr'] = 'S2s_value_fit_error'
        self.tag_names['ChiSquaredVal'] = 'Chi_squared_val'
