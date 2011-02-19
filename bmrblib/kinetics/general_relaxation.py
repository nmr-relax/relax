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
"""The General Relaxation data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.2html/SaveFramePage.html#general_relaxation.
"""

# relax module imports.
from bmrblib.base_classes import TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.kinetics.relax_base import HeteronuclRxList, RelaxSaveframe, Rx
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class GeneralRelaxationSaveframe(RelaxSaveframe):
    """The General Relaxation data saveframe class."""

    # Saveframe variables.
    label = 'general_relaxation'

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.rx_inc = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, data_type=None, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', temp_calibration=None, temp_control=None, frq=None, details=None, assembly_atom_ids=None, entity_assembly_ids=None, res_nums=None, seq_id=None, res_names=None, atom_names=None, atom_types=None, isotope=None, data=None, errors=None, rex_val=None, rex_err=None):
        """Add relaxation data to the data nodes.

        Note that units of 1/s are actually rad/s in NMR.  This is the hidden radian unit, which if not present would mean that the units would be Hz.  For more details, see https://mail.gna.org/public/relax-users/2009-01/msg00000.html.


        @keyword sample_cond_list_id:       The sample conditions list ID number.
        @type sample_cond_list_id:          str
        @keyword sample_cond_list_label:    The sample conditions list label.
        @type sample_cond_list_label:       str
        @keyword data_type:                 The relaxation data type (one of 'R1' or 'R2').
        @type data_type:                    str
        @keyword frq:                       The spectrometer proton frequency, in Hz.
        @type frq:                          float
        @keyword assembly_atom_ids:         The assembly atom ID numbers.
        @type assembly_atom_ids:            list of int
        @keyword entity_assembly_ids:       The entity assembly ID numbers.
        @type entity_assembly_ids:          list of int
        @keyword entity_id:                 The entity ID number.
        @type entity_id:                    int
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
        @keyword temp_calibration:          The temperature calibration method.
        @type temp_calibration:             str
        @keyword temp_control:              The temperature control method.
        @type temp_control:                 str
        @keyword details:                   The details tag.
        @type details:                      None or str
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the %s MHz %s relaxation data' % (int(frq*1e-6), data_type))
        no_missing(res_names, 'residue names of the %s MHz %s relaxation data' % (int(frq*1e-6), data_type))
        no_missing(atom_names, 'atom names of the %s MHz %s relaxation data' % (int(frq*1e-6), data_type))

        # Check the args.
        if not temp_calibration:
            raise NameError("The temperature calibration method has not been specified.")
        if not temp_control:
            raise NameError("The temperature control method has not been specified.")

        # The number of elements.
        N = len(res_nums)

        # Place the args into the namespace.
        self.sample_cond_list_id = translate(sample_cond_list_id)
        self.sample_cond_list_label = translate(sample_cond_list_label)
        self.temp_calibration = translate(temp_calibration)
        self.temp_control = translate(temp_control)
        self.frq = frq
        self.details = translate(details)

        # Convert to lists and check the lengths.
        for name in ['assembly_atom_ids', 'entity_assembly_ids', 'res_nums', 'seq_id', 'res_names', 'atom_names', 'atom_types', 'isotope', 'data', 'errors', 'rex_val', 'rex_err']:
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

        # Set up the Rx specific variables.
        self.rx_inc = self.rx_inc + 1
        self.rx_inc_list = translate([self.rx_inc] * N)
        self.generate_data_ids(N)

        # The operators of the relaxation superoperator.
        if data_type == 'R1':
            self.GeneralRelaxationlist.variables['coherence'] = 'Iz'
            self.GeneralRelaxationlist.variables['coherence_common_name'] = 'R1'
        elif data_type == 'R2':
            self.GeneralRelaxationlist.variables['coherence'] = 'I+'
            self.GeneralRelaxationlist.variables['coherence_common_name'] = 'R2'
        else:
            raise NameError("The data type '%s' is not one of ['R1', 'R2']." % data_type)

        # Set up the version specific variables.
        self.specific_setup()

        # Initialise the save frame.
        self.frame = SaveFrame(title=self.label+'_list_'+repr(self.rx_inc))

        # Create the tag categories.
        self.GeneralRelaxationlist.create()
        self.GeneralRelaxationexperiment.create()
        self.GeneralRelaxationsoftware.create()
        self.GeneralRelaxation.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.GeneralRelaxationlist = GeneralRelaxationList(self)
        self.GeneralRelaxationexperiment = GeneralRelaxationExperiment(self)
        self.GeneralRelaxationsoftware = GeneralRelaxationSoftware(self)
        self.GeneralRelaxation = GeneralRelaxation(self)


    def loop(self):
        """Loop over the GeneralRelaxation saveframes, yielding the relaxation data.

        @return:    The relaxation data consisting of the proton frequency, residue numbers, residue
                    names, atom names, values, and errors.
        @rtype:     tuple of float, list of int, list of str, list of str, list of float, list of
                    float
        """

        # Set up the version specific variables.
        self.specific_setup()

        # Get the saveframe name.
        sf_name = getattr(self, 'cat_name')[0]

        # Loop over all datanodes.
        for datanode in self.datanodes:
            # Find the GeneralRelaxation saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.GeneralRelaxationlist.create_tag_label(self.GeneralRelaxationlist.tag_names['SfCategory']):
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == sf_name:
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Get general info.
            data_type, frq = self.GeneralRelaxationlist.read(datanode.tagtables[0])

            # Get the Rx info.
            res_nums, res_names, atom_names, values, errors = self.GeneralRelaxation.read(datanode.tagtables[1])

            # Yield the data.
            yield data_type, frq, res_nums, res_names, atom_names, values, errors



class GeneralRelaxationList(HeteronuclRxList):
    """Base class for the GeneralRelaxationList tag category."""

    def create(self):
        """Create the GeneralRelaxationList tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # GeneralRelaxation ID number.
        if 'GeneralRelaxationListID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['GeneralRelaxationListID']], tagvalues=[[str(self.sf.rx_inc)]]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListID']], tagvalues=[[self.sf.sample_cond_list_id]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[[self.sf.sample_cond_list_label]]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TempCalibrationMethod']], tagvalues=[[self.sf.temp_calibration]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TempControlMethod']], tagvalues=[[self.sf.temp_control]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SpectrometerFrequency1H']], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['RelaxationCoherenceType']], tagvalues=[[self.variables['coherence']]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['RelaxationTypeCommonName']], tagvalues=[[self.variables['coherence_common_name']]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['RelaxationValUnits']], tagvalues=[['s-1']]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Details']], tagvalues=[[self.sf.details]]))


    def read(self, tagtable):
        """Extract the GeneralRelaxationList tag category info.

        @param tagtable:    The GeneralRelaxationList tagtable.
        @type tagtable:     Tagtable instance
        @return:            The relaxation data type and the proton frequency in Hz.
        @rtype:             str, float
        """

        # The general info.
        coherence = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['RelaxationCoherenceType'])][0]
        frq = float(tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['SpectrometerFrequency1H'])][0]) * 1e6

        # Determine the data type.
        if coherence == 'Iz':
            data_type = 'R1'
        elif coherence == 'I+':
            data_type = 'R2'
        else:
            raise NameError("The coherence type '%s' is unknown." % coherence)

        # Return the data.
        return data_type, frq


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='General_Relaxation_list', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['GeneralRelaxationListID'] = 'ID'
        self.tag_names['TempCalibrationMethod'] = 'Temp_calibration_method'
        self.tag_names['TempControlMethod'] = 'Temp_control_method'
        self.tag_names['SampleConditionListID'] = 'Sample_condition_list_ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'
        self.tag_names['SpectrometerFrequency1H'] = 'Spectrometer_frequency_1H'
        self.tag_names['RelaxationCoherenceType'] = 'Relaxation_coherence_type'
        self.tag_names['RelaxationTypeCommonName'] = 'Relaxation_type_common_name'
        self.tag_names['RelaxationValUnits'] = 'Relaxation_val_units'
        self.tag_names['Details'] = 'Details'



class GeneralRelaxationExperiment(TagCategory):
    """Base class for the GeneralRelaxationExperiment tag category."""

    def create(self, frame=None):
        """Create the GeneralRelaxationExperiment tag category."""

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
        TagCategory.tag_setup(self, tag_category_label='General_Relaxation_experiment', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SampleLabel'] = 'Sample_label'


class GeneralRelaxationSoftware(TagCategory):
    """Base class for the GeneralRelaxationSoftware tag category."""

    def create(self):
        """Create the GeneralRelaxationSoftware tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='General_Relaxation_software', sep=sep)


class GeneralRelaxation(Rx):
    """Base class for the GeneralRelaxation tag category."""

    def create(self):
        """Create the Rx tag category."""

        # Keys and objects.
        info = [
            ['RxID',                    'data_ids'],
            ['AssemblyAtomID',          'assembly_atom_ids'],
            ['EntityAssemblyID',        'entity_assembly_ids'],
            ['CompIndexID',             'res_nums'],
            ['SeqID',                   'seq_id'],
            ['CompID',                  'res_names'],
            ['AtomID',                  'atom_names'],
            ['AtomType',                'atom_types'],
            ['AtomIsotopeNumber',       'isotope'],
            ['Val',    'data'],
            ['ValErr', 'errors'],
            ['RexVal',                  'rex_val'],
            ['RexErr',                  'rex_err'],
            ['GeneralRelaxationListID', 'rx_inc_list']
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
        Rx.tag_setup(self, tag_category_label='General_Relaxation', sep=sep)

        # Tag names for the general relaxation data.
        self.tag_names['RxID'] = 'ID'
        self.tag_names['AssemblyAtomID'] = 'Assembly_atom_ID'
        self.tag_names['EntityAssemblyID'] = 'Entity_assembly_ID'
        self.tag_names['EntityID'] = 'Entity_ID'
        self.tag_names['CompIndexID'] = 'Comp_index_ID'
        self.tag_names['SeqID'] = 'Seq_ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['AtomID'] = 'Atom_ID'
        self.tag_names['AtomType'] = 'Atom_type'
        self.tag_names['AtomIsotopeNumber'] = 'Atom_isotope_number'
        self.tag_names['Val'] = 'General_relaxation_val'
        self.tag_names['ValErr'] = 'General_relaxation_val_err'
        self.tag_names['RexVal'] = 'Rex_val'
        self.tag_names['RexErr'] = 'Rex_err'
        self.tag_names['GeneralRelaxationListID'] = 'General_relaxation_list_ID'
