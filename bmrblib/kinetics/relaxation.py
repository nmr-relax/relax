#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The relaxation data BMRB API interface.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.
"""


# relax module imports.
from bmrblib.kinetics.auto_relaxation_v3_1 import AutoRelaxationSaveframe_v3_1
from bmrblib.kinetics.heteronucl_NOEs_v2_1 import HeteronuclNOESaveframe_v2_1
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1
from bmrblib.kinetics.heteronucl_T1_relaxation_v2_1 import HeteronuclT1Saveframe_v2_1
from bmrblib.kinetics.heteronucl_T1_relaxation_v3_1 import HeteronuclT1Saveframe_v3_1
from bmrblib.kinetics.heteronucl_T2_relaxation_v2_1 import HeteronuclT2Saveframe_v2_1
from bmrblib.kinetics.heteronucl_T2_relaxation_v3_1 import HeteronuclT2Saveframe_v3_1


class Relaxation_v2_1:
    """Class for the relaxation data part of the BMRB API."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Initialise the kinetic saveframe supergroups.
        self.heteronucl_NOEs = HeteronuclNOESaveframe_v2_1(datanodes)
        self.heteronucl_T1_relaxation = HeteronuclT1Saveframe_v2_1(datanodes)
        self.heteronucl_T2_relaxation = HeteronuclT2Saveframe_v2_1(datanodes)


    def add(self, **keywords):
        """Distribute the relaxation data to the appropriate saveframes.

        @keyword data_type:                 The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:                    str
        @keyword sample_cond_list_id:       The sample conditions list ID number.
        @type sample_cond_list_id:          str
        @keyword sample_cond_list_label:    The sample conditions list label.
        @type sample_cond_list_label:       str
        @keyword temp_calibration:          The temperature calibration method (unused).
        @type temp_calibration:             str
        @keyword temp_control:              The temperature control method (unused).
        @type temp_control:                 str
        @keyword peak_intensity_type:       The peak intensity type - one of 'height' or 'volume'.
        @type peak_intensity_type:          str
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
        """

        # Pack specific the data.
        if keywords['data_type'] == 'R1':
            self.heteronucl_T1_relaxation.add(**keywords)
        elif keywords['data_type'] == 'R2':
            self.heteronucl_T2_relaxation.add(**keywords)
        elif keywords['data_type'] == 'NOE':
            self.heteronucl_NOEs.add(**keywords)


    def loop(self):
        """Generator method for looping over and returning all relaxation data."""

        # The NOE data.
        for data in self.heteronucl_NOEs.loop():
            data['data_type'] = 'NOE'
            yield data

        # The R1 data.
        for data in self.heteronucl_T1_relaxation.loop():
            data['data_type'] = 'R1'
            yield data

        # The R2 data.
        for data in self.heteronucl_T2_relaxation.loop():
            data['data_type'] = 'R2'
            yield data



class Relaxation_v3_0(Relaxation_v2_1):
    """Class for the relaxation data part of the BMRB API (v3.0)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Execute the base class __init__() method.
        Relaxation_v2_1.__init__(self, datanodes)



class Relaxation_v3_1(Relaxation_v3_0):
    """Class for the relaxation data part of the BMRB API (v3.1)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Execute the base class __init__() method.
        Relaxation_v3_0.__init__(self, datanodes)

        # Initialise the kinetic saveframe supergroups.
        self.heteronucl_NOEs = HeteronuclNOESaveframe_v3_1(datanodes)
        self.heteronucl_T1_relaxation = HeteronuclT1Saveframe_v3_1(datanodes)
        self.heteronucl_T2_relaxation = HeteronuclT2Saveframe_v3_1(datanodes)
        self.auto_relaxation = AutoRelaxationSaveframe_v3_1(datanodes)


    def add(self, **keywords):
        """Add relaxation data to the data nodes.

        @keyword data_type:                 The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:                    str
        @keyword sample_cond_list_id:       The sample conditions list ID number.
        @type sample_cond_list_id:          str
        @keyword sample_cond_list_label:    The sample conditions list label.
        @type sample_cond_list_label:       str
        @keyword temp_calibration:          The temperature calibration method.
        @type temp_calibration:             str
        @keyword temp_control:              The temperature control method.
        @type temp_control:                 str
        @keyword peak_intensity_type:       The peak intensity type - one of 'height' or 'volume'.
        @type peak_intensity_type:          str
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
        """

        # Pack specific the data.
        if keywords['data_type'] in ['R1', 'R2']:
            self.auto_relaxation.add(**keywords)
        elif keywords['data_type'] == 'NOE':
            self.heteronucl_NOEs.add(**keywords)


    def loop(self):
        """Generator method for looping over and returning all relaxation data."""

        # The NOE data.
        for data in self.heteronucl_NOEs.loop():
            data['data_type'] = 'NOE'
            yield data

        # The R1 data.
        for data in self.heteronucl_T1_relaxation.loop():
            data['data_type'] = 'R1'
            yield data

        # The R2 data.
        for data in self.heteronucl_T2_relaxation.loop():
            data['data_type'] = 'R2'
            yield data


        # The auto-relaxation data.
        for data in self.auto_relaxation.loop():
            data['data_type'] = data['coherence_common_name']
            yield data
