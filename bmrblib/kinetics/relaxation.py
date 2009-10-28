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
"""The relaxation data BMRB API interface."""


# relax module imports.
from bmrblib.kinetics.general_relaxation import GeneralRelaxationSaveframe
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1
from bmrblib.kinetics.heteronucl_NOEs_v3_2 import HeteronuclNOESaveframe_v3_2
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe
from bmrblib.kinetics.heteronucl_T1_relaxation_v3_1 import HeteronuclT1Saveframe_v3_1
from bmrblib.kinetics.heteronucl_T2_relaxation import HeteronuclT2Saveframe
from bmrblib.kinetics.heteronucl_T2_relaxation_v3_1 import HeteronuclT2Saveframe_v3_1


class Relaxation:
    """Class for the relaxation data part of the BMRB API."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Initialise the kinetic saveframe supergroups.
        self.heteronucl_NOEs = HeteronuclNOESaveframe(datanodes)
        self.heteronucl_T1_relaxation = HeteronuclT1Saveframe(datanodes)
        self.heteronucl_T2_relaxation = HeteronuclT2Saveframe(datanodes)


    def add(self, data_type=None, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', frq=None, details=None, assembly_atom_ids=None, entity_assembly_ids=None, entity_ids=None, res_nums=None, seq_id=None, res_names=None, atom_names=None, atom_types=None, isotope=None, assembly_atom_ids_2=None, entity_assembly_ids_2=None, entity_ids_2=None, res_nums_2=None, seq_id_2=None, res_names_2=None, atom_names_2=None, atom_types_2=None, isotope_2=None, data=None, errors=None, temp_calibration=None, temp_control=None):
        """Add relaxation data to the data nodes.

        @keyword data_type:                 The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:                    str
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
        @keyword temp_calibration:          The temperature calibration method (unused).
        @type temp_calibration:             str
        @keyword temp_control:              The temperature control method (unused).
        @type temp_control:                 str
        """

        # Pack specific the data.
        if data_type == 'R1':
            self.heteronucl_T1_relaxation.add(frq=frq,
                                              entity_ids=entity_ids,
                                              res_nums=res_nums,
                                              res_names=res_names,
                                              atom_names=atom_names,
                                              isotope=isotope,
                                              data=data,
                                              errors=errors)
        elif data_type == 'R2':
            self.heteronucl_T2_relaxation.add(frq=frq,
                                              entity_ids=entity_ids,
                                              res_nums=res_nums,
                                              res_names=res_names,
                                              atom_names=atom_names,
                                              isotope=isotope,
                                              data=data,
                                              errors=errors)
        elif data_type == 'NOE':
            self.heteronucl_NOEs.add(sample_cond_list_id=sample_cond_list_id,
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


    def loop(self):
        """Generator method for looping over and returning all relaxation data."""

        # The NOE data.
        for frq, entity_ids, res_nums, res_names, spin_names, val, err in self.heteronucl_NOEs.loop():
            yield "NOE", frq, entity_ids, res_nums, res_names, spin_names, val, err

        # The R1 data.
        for frq, entity_ids, res_nums, res_names, spin_names, val, err in self.heteronucl_T1_relaxation.loop():
            yield "R1", frq, entity_ids, res_nums, res_names, spin_names, val, err

        # The R2 data.
        for frq, entity_ids, res_nums, res_names, spin_names, val, err in self.heteronucl_T2_relaxation.loop():
            yield "R2", frq, entity_ids, res_nums, res_names, spin_names, val, err


class Relaxation_v3_0(Relaxation):
    """Class for the relaxation data part of the BMRB API (v3.0)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Execute the base class __init__() method.
        Relaxation.__init__(self, datanodes)


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


class Relaxation_v3_2(Relaxation_v3_1):
    """Class for the relaxation data part of the BMRB API (v3.2)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Execute the base class __init__() method.
        Relaxation_v3_1.__init__(self, datanodes)

        # Initialise the kinetic saveframe supergroups.
        self.heteronucl_NOEs = HeteronuclNOESaveframe_v3_2(datanodes)
        self.general_relaxation = GeneralRelaxationSaveframe(datanodes)


    def add(self, data_type=None, sample_cond_list_id=None, sample_cond_list_label='$conditions_1', frq=None, details=None, assembly_atom_ids=None, entity_assembly_ids=None, entity_ids=None, res_nums=None, seq_id=None, res_names=None, atom_names=None, atom_types=None, isotope=None, assembly_atom_ids_2=None, entity_assembly_ids_2=None, entity_ids_2=None, res_nums_2=None, seq_id_2=None, res_names_2=None, atom_names_2=None, atom_types_2=None, isotope_2=None, data=None, errors=None, temp_calibration=None, temp_control=None):
        """Add relaxation data to the data nodes.

        @keyword data_type:                 The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:                    str
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

        # Pack specific the data.
        if data_type in ['R1', 'R2']:
            self.general_relaxation.add(data_type=data_type,
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
                                        data=data,
                                        errors=errors,
                                        temp_calibration=temp_calibration,
                                        temp_control=temp_control)
        elif data_type == 'NOE':
            self.heteronucl_NOEs.add(sample_cond_list_id=sample_cond_list_id,
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
                                     errors=errors,
                                     temp_calibration=temp_calibration,
                                     temp_control=temp_control)


    def loop(self):
        """Generator method for looping over and returning all relaxation data."""

        # The NOE data.
        for frq, entity_ids, res_nums, res_names, spin_names, val, err in self.heteronucl_NOEs.loop():
            yield "NOE", frq, entity_ids, res_nums, res_names, spin_names, val, err

        # The R1 and R2 data.
        for data in self.general_relaxation.loop():
            yield data
