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
"""Base classes for the relaxation data."""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory


class RelaxSaveframe(BaseSaveframe):
    """The heteronuclear Rx data saveframe baseclass."""

    def loop(self):
        """Loop over the Rx saveframes, yielding the relaxation data.

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
            # Find the Heteronuclear Rx saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.heteronuclRxlist.create_tag_label(self.heteronuclRxlist.tag_names['SfCategory']):
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == sf_name:
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Get general info.
            frq = self.heteronuclRxlist.read(datanode.tagtables[0])

            # Get the Rx info.
            res_nums, res_names, atom_names, values, errors = self.Rx.read(datanode.tagtables[1])

            # Yield the data.
            yield frq, res_nums, res_names, atom_names, values, errors


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = [self.label+'_relaxation']



class HeteronuclRxList(TagCategory):
    """Base class for the HeteronuclRxList tag categories."""

    def read(self, tagtable):
        """Extract the HeteronuclRxList tag category info.

        @param tagtable:    The HeteronuclRxList tagtable.
        @type tagtable:     Tagtable instance
        @return:            The proton frequency in Hz.
        @rtype:             float
        """

        # The general info.
        frq = float(tagtable.tagvalues[tagtable.tagnames.index(self.tag_names_full['SpectrometerFrequency1H'])][0]) * 1e6

        # Return the data.
        return frq


class Rx(TagCategory):
    """Base class for the Rx tag categories."""

    def create(self):
        """Create the Rx tag category."""

        # Keys and objects.
        info = [
            ['RxID',                'data_ids'],
            ['CompIndexID',         'res_nums'],
            ['CompID',              'res_names'],
            ['AtomID',              'atom_names'],
            ['AtomIsotopeNumber',   'isotope'],
            ['Val',                 'data'],
            ['ValErr',              'errors'],
            ['HeteronuclRxListID',  'rx_inc_list']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def read(self, tagtable):
        """Extract the Rx tag category info.

        @param tagtable:    The Rx tagtable.
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
        self.tag_names['RxID'] = None
        self.tag_names['CompIndexID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['AtomIsotopeNumber'] = 'Atom_isotope_number'
        self.tag_names['Val'] = self.sf.label+'_value'
        self.tag_names['ValErr'] = self.sf.label+'_value_error'
        self.tag_names['HeteronuclRxListID'] = 'Heteronucl_'+self.sf.label+'_list_ID'
