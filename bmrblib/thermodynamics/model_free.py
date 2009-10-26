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
"""The model_free saveframe category (used to be called order_parameters).

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#order_parameters
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class ModelFreeSaveframe(BaseSaveframe):
    """The Order parameters saveframe class."""

    # Saveframe variables.
    title = 'order_parameters'

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', te_units='s', tf_units='s', ts_units='s', global_chi2=None, details=None, software_ids=None, software_labels=None, assembly_atom_ids=None, entity_assembly_ids=None, entity_id=None, res_nums=None, res_names=None, atom_names=None, atom_types=None, isotope=None, local_tc=None, local_tc_err=None, s2=None, s2_err=None, s2f=None, s2f_err=None, s2s=None, s2s_err=None, te=None, te_err=None, tf=None, tf_err=None, ts=None, ts_err=None, rex=None, rex_err=None, rex_frq=None, chi2=None, model_fit=None):
        """Add model-free data to the data nodes.

        Note the te, tf, and ts units include the hidden radian unit as these are angular correlation times, e.g. the default of 's' is really 's/rad', the average time it take to rotate 1 radian.

        The model_free argument is a string describing the model used for the spin.  For no internal model-free motions, it can be one of:

            - ''
            - 'Rex'

        For the original Lipari-Szabo model-free motions (Lipari and Szabo, 1982), plus additional parameters such as Rex, model_fit can be one of:

            - 'S2'
            - 'S2, te'
            - 'S2, Rex'
            - 'S2, te, Rex'

        For the extended model-free motions (Clore et al., 1990), plus additional parameters such as Rex, model_fit can be one of:

            - 'S2f, S2, ts'
            - 'S2f, S2s, ts'
            - 'S2f, tf, S2, ts'
            - 'S2f, tf, S2s, ts'
            - 'S2f, S2, ts, Rex'
            - 'S2f, S2s, ts, Rex'
            - 'S2f, tf, S2, ts, Rex'
            - 'S2f, tf, S2s, ts, Rex'


        @keyword sample_cond_list_id:       The sample conditions list ID number.
        @type sample_cond_list_id:          str
        @keyword sample_cond_list_label:    The sample conditions list label.
        @type sample_cond_list_label:       str
        @keyword te_units:                  The units of the te model-free parameters.
        @type te_units:                     str
        @keyword tf_units:                  The units of the tf model-free parameters.
        @type tf_units:                     str
        @keyword ts_units:                  The units of the ts model-free parameters.
        @type ts_units:                     str
        @keyword global_chi2:               The optimised global chi-squared value for the global model (the sum of the diffusion tensor together with the model-free models for all spins).
        @type global_chi2:                  None or float
        @keyword details:                   The details tag.
        @type details:                      str
        @keyword software_ids:              The software ID numbers for all software used in the model-free analysis.
        @type software_ids:                 list of int
        @keyword software_labels:           The names of all software used in the model-free analysis.
        @type software_labels:              list of str
        @keyword res_nums:                  The residue number for each spin.
        @keyword assembly_atom_ids:         The assembly atom ID numbers.
        @type assembly_atom_ids:            list of int
        @keyword entity_assembly_ids:       The entity assembly ID numbers.
        @type entity_assembly_ids:          list of int
        @keyword entity_id:                 The entity ID number.
        @type entity_id:                    int
        @type res_nums:                     list of int
        @keyword res_names:                 The residue name for each spin.
        @type res_names:                    list of str
        @keyword atom_names:                The atom name for each spin.
        @type atom_names:                   list of str
        @keyword atom_types:                The atom types as IUPAC element abbreviations for each spin.
        @type atom_types:                   list of str
        @keyword isotope:                   The isotope type list, ie 15 for '15N'.
        @type isotope:                      list of int
        @keyword local_tc:                  The spin specific diffusional correlation time.
        @type local_tc:                     lost of float
        @keyword local_tc_err:              The spin specific diffusional correlation time errors.
        @type local_tc_err:                 lost of float
        @keyword s2:                        The S2 values for each spin.
        @type s2:                           list of float
        @keyword s2_err:                    The S2 errors for each spin.
        @type s2_err:                       list of float
        @keyword s2f:                       The S2f values for each spin.
        @type s2f:                          list of float
        @keyword s2f_err:                   The S2f errors for each spin.
        @type s2f_err:                      list of float
        @keyword s2s:                       The S2s values for each spin.
        @type s2s:                          list of float
        @keyword s2s_err:                   The S2s errors for each spin.
        @type s2s_err:                      list of float
        @keyword te:                        The te values for each spin (in rad/s units).
        @type te:                           list of float
        @keyword te_err:                    The te errors for each spin (in rad/s units).
        @type te_err:                       list of float
        @keyword tf:                        The tf values for each spin (in rad/s units).
        @type tf:                           list of float
        @keyword tf_err:                    The tf errors for each spin (in rad/s units).
        @type tf_err:                       list of float
        @keyword ts:                        The ts values for each spin (in rad/s units).
        @type ts:                           list of float
        @keyword ts_err:                    The ts errors for each spin (in rad/s units).
        @type ts_err:                       list of float
        @keyword rex:                       The Rex values for each spin (in rad/s units for the field strength specified in
                                            rex_frq).
        @type rex:                          list of float
        @keyword rex_err:                   The Rex errors for each spin (in rad/s units for the field strength specified in
                                            rex_frq).
        @type rex_err:                      list of float
        @keyword rex_frq:                   The 1H spectrometer frequency in Hz that the Rex values are reported
                                            in.
        @type rex_frq:                      float
        @keyword chi2:                      The optimised chi-squared values for each spin.  This should be none if the global model was optimised.
        @type chi2:                         None or list of float
        @keyword model_free:                The model-free model fit.
        @type model_free:                   str
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

        # Check the model.
        allowed_models = ['',
                          'Rex',
                          'S2',
                          'S2, te',
                          'S2, Rex',
                          'S2, te, Rex',
                          'S2f, S2, ts',
                          'S2f, S2s, ts',
                          'S2f, tf, S2, ts',
                          'S2f, tf, S2s, ts',
                          'S2f, S2, ts, Rex',
                          'S2f, S2s, ts, Rex',
                          'S2f, tf, S2, ts, Rex',
                          'S2f, tf, S2s, ts, Rex'
                          'tm',
                          'tm, Rex',
                          'tm, S2',
                          'tm, S2, te',
                          'tm, S2, Rex',
                          'tm, S2, te, Rex',
                          'tm, S2f, S2, ts',
                          'tm, S2f, S2s, ts',
                          'tm, S2f, tf, S2, ts',
                          'tm, S2f, tf, S2s, ts',
                          'tm, S2f, S2, ts, Rex',
                          'tm, S2f, S2s, ts, Rex',
                          'tm, S2f, tf, S2, ts, Rex',
                          'tm, S2f, tf, S2s, ts, Rex'
         ]
        for model in model_fit:
            if model not in allowed_models:
                raise NameError("The model-free model '%s' is unknown.  It must be one of %s." % (model_fit, allowed_models))

        # Place the args into the namespace.
        self.sample_cond_list_id = translate(sample_cond_list_id)
        self.sample_cond_list_label = translate(sample_cond_list_label)
        self.te_units = translate(te_units)
        self.tf_units = translate(tf_units)
        self.ts_units = translate(ts_units)
        self.global_chi2 = translate(global_chi2)
        self.details = translate(details)
        self.software_ids = translate(software_ids)
        self.software_labels = translate(software_labels)

        # Number of elements.
        N = len(res_nums)

        # Convert and translate all the spin specific args.
        names = ['assembly_atom_ids', 'entity_assembly_ids', 'entity_id', 'res_nums', 'res_names', 'atom_names', 'atom_types', 'isotope', 'local_tc', 'local_tc_err', 's2', 's2_err', 's2f', 's2f_err', 's2s', 's2s_err', 'te', 'te_err', 'tf', 'tf_err', 'ts', 'ts_err', 'rex', 'rex_err', 'chi2', 'model_fit']
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

        # The model-free ID number.
        self.model_free_id = translate([1] * len(self.software_ids))

        # The ID numbers.
        self.generate_data_ids(N)

        # Initialise the save frame.
        self.frame = SaveFrame(title=self.title)

        # Create the tag categories.
        self.model_free_list.create()
        self.model_free_experiment.create()
        self.model_free_software.create()
        self.model_free.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.model_free_list = ModelFreeList(self)
        self.model_free_experiment = ModelFreeExperiment(self)
        self.model_free_software = ModelFreeSoftware(self)
        self.model_free = ModelFree(self)


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = ['S2_parameters']


class ModelFreeList(TagCategory):
    """Base class for the ModelFreeList tag category."""

    # Class variables.
    label = 'Model_free_list'

    def create(self):
        """Create the ModelFreeList tag category."""

        # Create all the tags.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))
        if 'ModelFreeListID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['ModelFreeListID']], tagvalues=[['1']]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListID']], tagvalues=[[self.sf.sample_cond_list_id]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[[self.sf.sample_cond_list_label]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TaueValUnits']], tagvalues=[[self.sf.te_units]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TaufValUnits']], tagvalues=[[self.sf.tf_units]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TausValUnits']], tagvalues=[[self.sf.ts_units]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['GlobalChiSquaredFitVal']], tagvalues=[[self.sf.global_chi2]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Details']], tagvalues=[[self.sf.details]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label=self.label

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the model-free data.
        self.tag_names['SfCategory'] = 'Saveframe_category'
        self.tag_names['SampleConditionListID'] = 'Sample_condition_list_ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_conditions_label'
        self.tag_names['TaueValUnits'] = 'Tau_e_val_units'
        self.tag_names['TaufValUnits'] = 'Tau_f_val_units'
        self.tag_names['TausValUnits'] = 'Tau_s_val_units'
        self.tag_names['GlobalChiSquaredFitVal'] = 'Global_chi_squared_fit_val'
        self.tag_names['Details'] = 'Details'


class ModelFreeExperiment(TagCategory):
    """Base class for the ModelFreeExperiment tag category."""

    def create(self):
        """Create the ModelFreeExperiment tag category."""

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

        # Tag names for the model-free data.
        self.tag_names['SampleLabel'] = 'Sample_label'


class ModelFreeSoftware(TagCategory):
    """Base class for the ModelFreeSoftware tag category."""

    # Class variables.
    label = "Model_free_software"

    def create(self):
        """Create the ModelFreeSoftware tag category."""

        # Keys and objects.
        info = [
            ['SoftwareID',      'software_ids'],
            ['SoftwareLabel',   'software_labels'],
            ['ModelFreeListID', 'model_free_id']
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

        # Category label.
        if not tag_category_label:
            tag_category_label=self.label

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the model-free data.
        self.tag_names['SoftwareID'] = 'Software_ID'
        self.tag_names['SoftwareLabel'] = 'Software_label'
        self.tag_names['ModelFreeListID'] = 'Model_free_list_ID'


class ModelFree(TagCategory):
    """Base class for the ModelFree tag category."""

    def create(self):
        """Create the ModelFree tag category."""

        # Keys and objects.
        info = [
            ['ModelFreeID',         'data_ids'],
            ['AssemblyAtomID',      'assembly_atom_ids'],
            ['EntityAssemblyID',    'entity_assembly_ids'],
            ['EntityID',            'entity_id'],
            ['CompIndexID',         'res_nums'],
            ['CompID',              'res_names'],
            ['AtomID',              'atom_names'],
            ['AtomType',            'atom_types'],
            ['AtomIsotopeNumber',   'isotope'],
            ['S2Val',               's2'],
            ['S2ValErr',            's2_err'],
            ['S2fVal',              's2f'],
            ['S2fValErr',           's2f_err'],
            ['S2sVal',              's2s'],
            ['S2sValErr',           's2s_err'],
            ['TauEVal',             'te'],
            ['TauEValErr',          'te_err'],
            ['TauFVal',             'tf'],
            ['TauFValErr',          'tf_err'],
            ['TauSVal',             'ts'],
            ['TauSValErr',          'ts_err'],
            ['RexVal',              'rex'],
            ['RexValErr',           'rex_err'],
            ['ChiSquaredVal',       'chi2'],
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

        # Tag names for the model-free data.
        self.tag_names['ModelFreeID'] = None
        self.tag_names['AssemblyAtomID'] = 'Assembly_atom_ID'
        self.tag_names['EntityAssemblyID'] = 'Entity_assembly_ID'
        self.tag_names['EntityID'] = 'Entity_ID'
        self.tag_names['CompIndexID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['AtomType'] = 'Atom_type'
        self.tag_names['AtomIsotopeNumber'] = 'Atom_isotope_number'
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
        self.tag_names['ChiSquaredVal'] = 'SSE_val'
        self.tag_names['ModelFit'] = 'Model_fit'
