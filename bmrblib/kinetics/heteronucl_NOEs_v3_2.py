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
"""The v3.2 Heteronuclear NOE data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.2html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.misc import translate
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1, HeteronuclNOEList_v3_1, HeteronuclNOEExperiment_v3_1, HeteronuclNOESoftware_v3_1, HeteronuclNOE_v3_1
from bmrblib.pystarlib.TagTable import TagTable


class HeteronuclNOESaveframe_v3_2(HeteronuclNOESaveframe_v3_1):
    """The v3.2 Heteronuclear NOE data saveframe class."""

    def add(self, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', frq=None, details=None, assembly_atom_ids=None, entity_assembly_ids=None, entity_ids=None, res_nums=None, seq_id=None, res_names=None, atom_names=None, atom_types=None, isotope=None, assembly_atom_ids_2=None, entity_assembly_ids_2=None, entity_ids_2=None, res_nums_2=None, seq_id_2=None, res_names_2=None, atom_names_2=None, atom_types_2=None, isotope_2=None, data=None, errors=None, temp_calibration=None, temp_control=None):
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
        @keyword assembly_atom_ids_2:       The assembly atom ID numbers.  This is for the second atom used in the heteronuclear NOE.
        @type assembly_atom_ids_2:          list of int
        @keyword entity_assembly_ids_2:     The entity assembly ID numbers.  This is for the second atom used in the heteronuclear NOE.
        @type entity_assembly_ids_2:        list of int
        @keyword entity_ids_2:              The entity ID numbers.  This is for the second atom used in the heteronuclear NOE.
        @type entity_ids_2:                 int
        @keyword res_nums_2:                The residue number list.  This is for the second atom used in the heteronuclear NOE.
        @type res_nums_2:                   list of int
        @keyword res_names_2:               The residue name list.  This is for the second atom used in the heteronuclear NOE.
        @type res_names_2:                  list of str
        @keyword atom_names_2:              The atom name list.  This is for the second atom used in the heteronuclear NOE.
        @type atom_names_2:                 list of str
        @keyword atom_types_2:              The atom types as IUPAC element abbreviations.  This is for the second atom used in the heteronuclear NOE.
        @type atom_types_2:                 list of str
        @keyword isotope_2:                 The isotope type list, ie 1 for '1H'.  This is for the second atom used in the heteronuclear NOE.
        @type isotope_2:                    list of int
        @keyword data:                      The relaxation data.
        @type data:                         list of float
        @keyword errors:                    The errors associated with the relaxation data.
        @type errors:                       list of float
        @keyword temp_calibration:          The temperature calibration method.
        @type temp_calibration:             str
        @keyword temp_control:              The temperature control method.
        @type temp_control:                 str
        """

        # Check the args.
        if not temp_calibration:
            raise NameError("The temperature calibration method has not been specified.")
        if not temp_control:
            raise NameError("The temperature control method has not been specified.")

        # Place the args into the namespace.
        self.temp_calibration = translate(temp_calibration)
        self.temp_control = translate(temp_control)

        # Execute the v3.1 add method.
        HeteronuclNOESaveframe_v3_1.add(self,
                                        sample_cond_list_id=sample_cond_list_id,
                                        sample_cond_list_label=sample_cond_list_label,
                                        frq=frq,
                                        details=details,
                                        assembly_atom_ids=assembly_atom_ids,
                                        entity_assembly_ids=entity_assembly_ids,
                                        entity_ids=entity_ids,
                                        res_nums=res_nums,
                                        seq_id=seq_id,
                                        res_names=res_names,
                                        atom_names=atom_names,
                                        atom_types=atom_types,
                                        isotope=isotope,
                                        assembly_atom_ids_2=assembly_atom_ids_2,
                                        entity_assembly_ids_2=entity_assembly_ids_2,
                                        entity_ids_2=entity_ids_2,
                                        res_nums_2=res_nums_2,
                                        seq_id_2=res_nums_2,
                                        res_names_2=res_names_2,
                                        atom_names_2=atom_names_2,
                                        atom_types_2=atom_types_2,
                                        isotope_2=isotope_2,
                                        data=data,
                                        errors=errors)


    def add_tag_categories(self):
        """Create the v3.2 tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclNOEList_v3_2(self)
        self.heteronuclRxexperiment = HeteronuclNOEExperiment_v3_1(self)
        self.heteronuclRxsoftware = HeteronuclNOESoftware_v3_1(self)
        self.Rx = HeteronuclNOE_v3_1(self)



class HeteronuclNOEList_v3_2(HeteronuclNOEList_v3_1):
    """v3.1 HeteronuclNOEList tag category."""

    def create(self):
        """Create the HeteronuclNOEList tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfFramecode']], tagvalues=[[self.sf.sf_label]]))

        # NOE ID number.
        if 'HeteronuclNOEListID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['HeteronuclNOEListID']], tagvalues=[[str(self.sf.noe_inc)]]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListID']], tagvalues=[[self.sf.sample_cond_list_id]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TempCalibrationMethod']], tagvalues=[[self.sf.temp_calibration]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['TempControlMethod']], tagvalues=[[self.sf.temp_control]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SpectrometerFrequency1H']], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Details']], tagvalues=[[self.sf.details]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Set up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        HeteronuclNOEList_v3_1.tag_setup(self, tag_category_label='Heteronucl_NOE_list', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['TempCalibrationMethod'] = 'Temp_calibration_method'
        self.tag_names['TempControlMethod'] = 'Temp_control_method'



