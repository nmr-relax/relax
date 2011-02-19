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
"""The chemical shift anisotropy data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#chem_shift_anisotropy
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class ChemShiftAnisotropySaveframe(BaseSaveframe):
    """The chemical shift anisotropy data saveframe class."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, atom_types=None, isotope=None, csa=None, units='ppm'):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword atom_types:    The atom types as IUPAC element abbreviations.
        @type atom_types:       list of str
        @keyword isotope:       The isotope type list, ie 15 for '15N'.
        @type isotope:          list of int
        @keyword csa:           The CSA values in ppm.
        @type csa:              list of float
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers')
        no_missing(res_names, 'residue names')
        no_missing(atom_names, 'atom names')

        # The number of elements.
        N = len(res_nums)

        # Place the args into the namespace.
        self.frq = frq
        self.units = units
        self.res_nums = translate(res_nums)
        self.res_names = translate(res_names)
        self.atom_names = translate(atom_names)
        self.atom_types = translate(atom_types)
        self.isotope = translate(isotope)
        self.csa = translate(csa)

        # Set up the CSA specific variables.
        self.generate_data_ids(N)

        # Set up the version specific variables.
        self.specific_setup()

        # Initialise the save frame.
        self.frame = SaveFrame(title='chem_shift_anisotropy')

        # Create the tag categories.
        self.Chem_shift_anisotropy.create()
        self.CS_anisotropy_experiment.create()
        self.CS_anisotropy_software.create()
        self.CS_anisotropy.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.Chem_shift_anisotropy = ChemShiftAnisotropy(self)
        self.CS_anisotropy_experiment = CSAnisotropyExperiment(self)
        self.CS_anisotropy_software = CSAnisotropySoftware(self)
        self.CS_anisotropy = CSAnisotropy(self)


    def loop(self):
        """Loop over the CSA saveframes, yielding the relaxation data.

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
            # Find the CSA saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.Chem_shift_anisotropy.create_tag_label(self.Chem_shift_anisotropy.tag_names['SfCategory']):
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == sf_name:
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Get general info.
            frq = self.Chem_shift_anisotropy.read(datanode.tagtables[0])

            # Get the CSA info.
            res_nums, res_names, atom_names, values, errors = self.CS_anisotropy.read(datanode.tagtables[1])

            # Yield the data.
            yield frq, res_nums, res_names, atom_names, values, errors


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = ['Chem_shift_anisotropy']



class ChemShiftAnisotropy(TagCategory):
    """Base class for the ChemShiftAnisotropy tag category."""

    def create(self):
        """Create the ChemShiftAnisotropy tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # CSA ID number.
        if 'ChemShiftAnisotropyID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['ChemShiftAnisotropyID']], tagvalues=[['1']]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['ValUnits']], tagvalues=[[self.sf.units]]))


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
        self.tag_names['ValUnits'] = 'Val_units'


class CSAnisotropyExperiment(TagCategory):
    """Base class for the CSAnisotropyExperiment tag category."""

    def create(self):
        """Create the CSAnisotropyExperiment tag category."""

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


class CSAnisotropySoftware(TagCategory):
    """Base class for the CSAnisotropySoftware tag category."""

    def create(self):
        """Create the CSAnisotropySoftware tag category."""


class CSAnisotropy(TagCategory):
    """Base class for the CSAnisotropy tag category."""

    def create(self):
        """Create the CSA tag category."""

        # Keys and objects.
        info = [
            ['CSAnisotropyID',      'data_ids'],
            ['CompIndexID',         'res_nums'],
            ['CompID',              'res_names'],
            ['AtomID',              'atom_names'],
            ['AtomType',            'atom_types'],
            ['AtomIsotopeNumber',   'isotope'],
            ['Val',                 'csa']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def read(self, tagtable):
        """Extract the CSA tag category info.

        @param tagtable:    The CSA tagtable.
        @type tagtable:     Tagtable instance
        @return:            The residue numbers, residue names, atom names, values, and errors.
        @rtype:             tuple of list of int, list of str, list of str, list of float, list of
                            float
        """

        # The entity info.
        res_nums = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['CompIndexID'])]
        res_names = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['CompID'])]
        atom_names = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['AtomID'])]
        values = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['Val'])]
        errors = tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['ValErr'])]

        # Convert the residue numbers to ints and the values and errors to floats.
        for i in range(len(res_nums)):
            res_nums[i] = int(res_nums[i])
            values[i] = float(values[i])
            errors[i] = float(errors[i])

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
        self.tag_names['CSAnisotropyID'] = None
        self.tag_names['CompIndexID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['AtomType'] = 'Atom_type'
        self.tag_names['AtomIsotopeNumber'] = 'Atom_isotope_number'
        self.tag_names['Val'] = 'value'
        self.tag_names['ValErr'] = 'value_error'
