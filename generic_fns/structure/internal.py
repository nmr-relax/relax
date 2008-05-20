###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
"""Module containing the internal relax structural object."""


# relax module imports.
from api_base import Base_struct_API
from relax_errors import RelaxError



class Internal(Base_struct_API):
    """The internal relax structural data object.

    The structural data object for this class is a dictionary of arrays.  The keys correspond to the
    'atom_id' strings.  The elements of the array are:

        0.  Atom number.
        1.  The record name (one of ATOM, HETATM, or TER).
        2.  Atom name.
        3.  Residue name.
        4.  Chain ID.
        5.  Residue number.
        6.  The x coordinate of the atom.
        7.  The y coordinate of the atom.
        8.  The z coordinate of the atom.
        9.  Segment ID.
        10.  Element symbol.
        11.  Bonded atom number 1.  Element 11 onwards correspond to the bonded atoms, this number
             being unlimited.
    """

    # Identification string.
    id = 'internal'


    def __init__(self):
        """Initialise the structural object."""

        # Reinitialise the data object to an empty dictionary.
        self.structural_data = {}


    def __get_chemical_name(self, hetID):
        """Method for returning the chemical name corresponding to the given residue ID.

        The following names are currently returned::
         ________________________________________________
         |        |                                     |
         | hetID  | Chemical name                       |
         |________|_____________________________________|
         |        |                                     |
         | TNS    | Tensor                              |
         | COM    | Centre of mass                      |
         | AXS    | Tensor axes                         |
         | SIM    | Monte Carlo simulation tensor axes  |
         |________|_____________________________________|


        @param res: The residue ID.
        @type res:  str
        @return:    The chemical name.
        @rtype:     str
        """

        # Tensor.
        if hetID == 'TNS':
            return 'Tensor'

        # Centre of mass.
        if hetID == 'COM':
            return 'Centre of mass'

        # Tensor axes.
        if hetID == 'AXS':
            return 'Tensor axes'

        # Monte Carlo simulation tensor axes.
        if hetID == 'SIM':
            return 'Monte Carlo simulation tensor axes'

        # Pivot point.
        if hetID == 'PIV':
            return 'Pivot point'

        # Cone object.
        if hetID == 'CON':
            return 'Cone'

        # Average vector.
        if hetID == 'AVE':
            return 'Average vector'

        # Unknown hetID.
        raise RelaxError, "The residue ID (hetID) " + `hetID` + " is not recognised."


    def atom_add(self, atom_id=None, record_name='', atom_name='', res_name='', chain_id='', res_num=None, pos=[None, None, None], segment_id='', element=''):
        """Method for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
        @type atom_id:      str
        @param record_name: The record name, e.g. 'ATOM', 'HETATM', or 'TER'.
        @type record_name:  str
        @param atom_name:   The atom name, e.g. 'H1'.
        @type atom_name:    str
        @param res_name:    The residue name.
        @type res_name:     str
        @param chain_id:    The chain identifier.
        @type chain_id:     str
        @param res_num:     The residue number.
        @type res_num:      int
        @param pos:         The position vector of coordinates.
        @type pos:          list (length = 3)
        @param segment_id:  The segment identifier.
        @type segment_id:   str
        @param element:     The element symbol.
        @type element:      str
        """

        # Initialise the key-value pair.
        self.structural_data[atom_id] = []

        # Fill the positions.
        self.structural_data[atom_id].append(len(self.structural_data))
        self.structural_data[atom_id].append(record_name)
        self.structural_data[atom_id].append(atom_name)
        self.structural_data[atom_id].append(res_name)
        self.structural_data[atom_id].append(chain_id)
        self.structural_data[atom_id].append(res_num)
        self.structural_data[atom_id].append(pos[0])
        self.structural_data[atom_id].append(pos[1])
        self.structural_data[atom_id].append(pos[2])
        self.structural_data[atom_id].append(segment_id)
        self.structural_data[atom_id].append(element)


    def atom_connect(self, atom_id=None, bonded_id=None):
        """Method for connecting two atoms within the data structure object.

        This method will find the atom number corresponding to both the atom_id and bonded_id.
        The bonded_id atom number will then be appended to the atom_id array.  Because the
        connections work both ways, the atom_id atom number will be appended to the bonded_id atom
        array as well.


        @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
        @type atom_id:      str
        @param bonded_id:   The second atom identifier.  This is used as the key within the
                            dictionary.
        @type bonded_id:    str
        """

        # Find the atom number corresponding to atom_id.
        if self.structural_data.has_key(atom_id):
            atom_num = self.structural_data[atom_id][0]
        else:
            raise RelaxError, "The atom corresponding to the atom_id " + `atom_id` + " doesn't exist."

        # Find the atom number corresponding to bonded_id.
        if self.structural_data.has_key(bonded_id):
            bonded_num = self.structural_data[bonded_id][0]
        else:
            raise RelaxError, "The atom corresponding to the bonded_id " + `bonded_id` + " doesn't exist."

        # Add the bonded_id to the atom_id array.
        self.structural_data[atom_id].append(bonded_num)

        # Add the atom_id to the bonded_id array.
        self.structural_data[bonded_id].append(atom_num)


    def terminate(self, atom_id_ext='', res_num=None):
        """Method for terminating the chain by adding a TER record to the structral data object.

        @param atom_id_ext:     The atom identifier extension.
        @type atom_id_ext:      str
        @param res_num:         The residue number.
        @type res_num:          int
        """

        # The name of the last residue.
        atomic_arrays = self.structural_data.values()
        atomic_arrays.sort()
        last_res = atomic_arrays[-1][3]

        # Add the TER 'atom'.
        self.atom_add(atom_id='TER' + atom_id_ext, record_name='TER', res_name=last_res, res_num=res_num)


    def write_pdb(self, file):
        """Method for the creation of a PDB file from the structural data.

        A number of PDB records including HET, HETNAM, FORMUL, HETATM, TER, CONECT, MASTER, and END
        are created.  To create the non-standard residue records HET, HETNAM, and FORMUL, the data
        structure 'het_data' is created.  It is an array of arrays where the first dimension
        corresponds to a different residue and the second dimension has the elements:

            0.  Residue number.
            1.  Residue name.
            2.  Chain ID.
            3.  Total number of atoms in the residue.
            4.  Number of H atoms in the residue.
            5.  Number of C atoms in the residue.


        @param file:        The PDB file object.  This object must be writable.
        @type file:         file object
        """

        # Sort the atoms.
        #################

        # Convert the self.structural_data structure from a dictionary of arrays to an array of arrays and sort it by atom number.
        atomic_arrays = self.structural_data.values()
        atomic_arrays.sort()


        # Collect the non-standard residue info.
        ########################################

        # Initialise some data.
        H_count = 0
        C_count = 0
        het_data = []

        # Loop over the atomic data.
        for array in atomic_arrays:
            # Skip all ATOM and TER records.
            if array[1] != 'HETATM':
                continue

            # The residue number and element.
            res_num = array[5]
            element = array[10]

            # If the residue is not already stored initialise a new het_data element.
            # (residue number, residue name, chain ID, number of atoms, number of H, number of C, number of N).
            if not het_data or not res_num == het_data[-1][0]:
                het_data.append([array[5], array[3], array[4], 0, 0, 0, 0])

            # Total atom count.
            het_data[-1][3] = het_data[-1][3] + 1

            # Proton count.
            if element == 'H':
                het_data[-1][4] = het_data[-1][4] + 1

            # Carbon count.
            elif element == 'C':
                het_data[-1][5] = het_data[-1][5] + 1

            # Nitrogen count.
            elif element == 'N':
                het_data[-1][6] = het_data[-1][6] + 1

            # Unsupported element type.
            else:
                raise RelaxError, "The element " + `element` + " was expected to be one of ['H', 'C', 'N']."


        # The HET records.
        ##################

        # Print out.
        print "Creating the HET records."

        # Write the HET records.
        for het in het_data:
            file.write("%-6s %3s  %1s%4s%1s  %5s     %-40s\n" % ('HET', het[2], het[1], het[0], '', het[3], ''))


        # The HETNAM records.
        #####################

        # Print out.
        print "Creating the HETNAM records."

        # Loop over the non-standard residues.
        residues = []
        for het in het_data:
            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Get the chemical name.
            chemical_name = self.__get_chemical_name(het[1])

            # Write the HETNAM records.
            file.write("%-6s  %2s %3s %-55s\n" % ('HETNAM', '', het[1], chemical_name))


        # The FORMUL records.
        #####################

        # Print out.
        print "Creating the FORMUL records."

        # Loop over the non-standard residues and generate and write the chemical formula.
        residues = []
        for het in het_data:
            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Initialise the chemical formula.
            formula = ''

            # Protons.
            if het[4]:
                if formula:
                    formula = formula + ' '
                formula = formula + 'H' + `het[4]`

            # Carbon.
            if het[5]:
                if formula:
                    formula = formula + ' '
                formula = formula + 'C' + `het[5]`

            # Nitrogen
            if het[6]:
                if formula:
                    formula = formula + ' '
                formula = formula + 'N' + `het[6]`

            # The FORMUL record (chemical formula).
            file.write("%-6s  %2s  %3s %2s%1s%-51s\n" % ('FORMUL', het[0], het[1], '', '', formula))


        # Add the atomic coordinate records (ATOM, HETATM, and TER).
        ############################################################

        # Print out.
        print "Creating the atomic coordinate records (ATOM, HETATM, and TER)."

        # Loop over the atomic data.
        for array in atomic_arrays:
            # Write the ATOM record.
            if array[1] == 'ATOM':
                file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('ATOM', array[0], array[2], '', array[3], array[4], array[5], '', array[6], array[7], array[8], 1.0, 0, array[9], array[10], ''))

            # Write the HETATM record.
            if array[1] == 'HETATM':
                file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', array[0], array[2], '', array[3], array[4], array[5], '', array[6], array[7], array[8], 1.0, 0, array[9], array[10], ''))

            # Write the TER record.
            if array[1] == 'TER':
                file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', array[0], array[3], array[4], array[5], ''))


        # Create the CONECT records.
        ############################

        # Print out.
        print "Creating the CONECT records."

        connect_count = 0
        for array in atomic_arrays:
            # No bonded atoms, hence no CONECT record is required.
            if len(array) == 10:
                continue

            # The atom number.
            atom_num = array[0]

            # Initialise some data structures.
            flush = 0
            bonded_index = 0
            bonded = ['', '', '', '']

            # Loop over the bonded atoms.
            for i in xrange(len(array[11:])):
                # End of the array, hence create the CONECT record in this iteration.
                if i == len(array[11:])-1:
                    flush = 1

                # Only four covalently bonded atoms allowed in one CONECT record.
                if bonded_index == 3:
                    flush = 1

                # Get the bonded atom name.
                bonded[bonded_index] = array[i+11]

                # Increment the bonded_index value.
                bonded_index = bonded_index + 1

                # Generate the CONECT record and increment the counter.
                if flush:
                    # Write the CONECT record.
                    file.write("%-6s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('CONECT', atom_num, bonded[0], bonded[1], bonded[2], bonded[3], '', '', '', '', '', ''))

                    # Increment the CONECT record count.
                    connect_count = connect_count + 1

                    # Reset the flush flag, the bonded atom count, and the bonded atom names.
                    flush = 0
                    bonded_index = 0
                    bonded = ['', '', '', '']


        # MASTER record.
        ################

        # Print out.
        print "Creating the MASTER record."

        # Write the MASTER record.
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, len(het_data), 0, 0, 0, 0, 0, len(self.structural_data), 1, connect_count, 0))


        # END.
        ######

        # Print out.
        print "Creating the END record."

        # Write the END record.
        file.write("END\n")
