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

    The structural data object for this class is a container possessing a number of different arrays
    corresponding to different structural information.  These objects are described in the
    structural container docstring.
    """

    # Identification string.
    id = 'internal'


    def __init__(self):
        """Initialise the structural object."""

        # Reinitialise the data object to an empty structure container.
        self.structural_data = Structure_container()


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
         | PIV    | Pivot point                         |
         | CON    | Cone object                         |
         | AVE    | Average vector                      |
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


    def __validate_data_arrays(self):
        """Check the validity of the data arrays in the structure object."""

        # The number of atoms.
        num = len(self.structural_data.atom_name)

        # Check the other lengths.
        if len(bonded) != num and len(chain_id) != num and len(element) != num and len(pdb_record) != num and len(res_name) != num and len(res_num) != num and len(seg_id) != num and len(x) != num and len(y) != num and len(z) != num:
            raise RelaxError, "The structural data is invalid."


    def atom_add(self, pdb_record=None, atom_name=None, res_name=None, chain_id=None, res_num=None, pos=[None, None, None], segment_id=None, element=None):
        """Method for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @param pdb_record:  The optional PDB record name, e.g. 'ATOM', 'HETATM', or 'TER'.
        @type pdb_record:   str or None
        @param atom_name:   The atom name, e.g. 'H1'.
        @type atom_name:    str or None
        @param res_name:    The residue name.
        @type res_name:     str or None
        @param chain_id:    The chain identifier.
        @type chain_id:     str or None
        @param res_num:     The residue number.
        @type res_num:      int or None
        @param pos:         The position vector of coordinates.
        @type pos:          list (length = 3)
        @param segment_id:  The segment identifier.
        @type segment_id:   str or None
        @param element:     The element symbol.
        @type element:      str or None
        """

        # Append to all the arrays.
        self.structural_data.atom_name.append(atom_name)
        self.structural_data.bonded.append([])
        self.structural_data.chain_id.append(chain_id)
        self.structural_data.element.append(element)
        self.structural_data.pdb_record.append(pdb_record)
        self.structural_data.res_name.append(res_name)
        self.structural_data.res_num.append(res_num)
        self.structural_data.seg_id.append(segment_id)
        self.structural_data.x.append(pos[0])
        self.structural_data.y.append(pos[1])
        self.structural_data.z.append(pos[2])


    def atom_connect(self, index1=None, index2=None):
        """Method for connecting two atoms within the data structure object.

        This method will append index2 to the array at bonded[index1] and vice versa.


        @param index1:  The index of the first atom.
        @type index1:   int
        @param index2:  The index of the second atom.
        @type index2:   int
        """

        # Update the bonded array structure.
        self.structural_data.bonded[index1].append(index2)
        self.structural_data.bonded[index2].append(index1)


    def terminate(self):
        """Method for terminating the chain by adding a TER record to the structural data object.

        The residue number and name are taken from the last atom in the current structural object.
        """

        # The name and number of the last residue.
        res_name = self.structural_data.res_name[-1]
        res_num = self.structural_data.res_num[-1]

        # Add the TER 'atom'.
        self.atom_add(pdb_record='TER', res_name=res_name, res_num=res_num)


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

        # Check the validity of the data.
        self.__validate_data_arrays()


        # Collect the non-standard residue info.
        ########################################

        # Initialise some data.
        H_count = 0
        C_count = 0
        het_data = []

        # Loop over the atomic data.
        for i in xrange(len(self.structural_data.atom_names)):
            # Catch the HETATM records.
            if self.structural_data.pdb_record[i] != 'HETATM':
                continue

            # If the residue is not already stored initialise a new het_data element.
            # (residue number, residue name, chain ID, number of atoms, number of H, number of C, number of N).
            if not het_data or not self.structural_data.res_num[i] == het_data[-1][0]:
                het_data.append([self.structural_data.res_num[i], self.structural_data.res_name[i], self.structural_data.chain_id[i], 0, 0, 0, 0])

            # Total atom count.
            het_data[-1][3] = het_data[-1][3] + 1

            # Proton count.
            if self.structural_data.element[i] == 'H':
                het_data[-1][4] = het_data[-1][4] + 1

            # Carbon count.
            elif self.structural_data.element[i] == 'C':
                het_data[-1][5] = het_data[-1][5] + 1

            # Nitrogen count.
            elif self.structural_data.element[i] == 'N':
                het_data[-1][6] = het_data[-1][6] + 1

            # Unsupported element type.
            else:
                raise RelaxError, "The element " + `self.structural_data.element[i]` + " was expected to be one of ['H', 'C', 'N']."


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
        for i in xrange(len(self.structural_data.atom_names)):
            # Atom number.
            atom_num = i + 1

            # Aliases.
            atom_name = self.structural_data.atom_name[i]
            res_name = self.structural_data.res_name[i]
            chain_id = self.structural_data.chain_id[i]
            res_num = self.structural_data.res_num[i]
            x = self.structural_data.x[i]
            y = self.structural_data.y[i]
            z = self.structural_data.z[i]
            seg_id = self.structural_data.seg_id[i]
            element = self.structural_data.element[i]

            # Replace None with ''.
            if atom_name == None:
                atom_name = ''
            if res_name == None:
                res_name = ''
            if chain_id == None:
                chain_id = ''
            if res_num == None:
                res_num = ''
            if x == None:
                x = ''
            if y == None:
                y = ''
            if z == None:
                z = ''
            if seg_id == None:
                seg_id = ''
            if element == None:
                element = ''

            # Write the ATOM record.
            if array[1] == 'ATOM':
                file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('ATOM', atom_num, atom_name, '', res_name, chain_id, res_num, '', x, y, z, 1.0, 0, seg_id, element, ''))

            # Write the HETATM record.
            if array[1] == 'HETATM':
                file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', atom_num, atom_name, '', res_name, chain_id, res_num, '', x, y, z, 1.0, 0, seg_id, element, ''))

            # Write the TER record.
            if array[1] == 'TER':
                file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', atom_num, res_name, chain_id, res_num, ''))


        # Create the CONECT records.
        ############################

        # Print out.
        print "Creating the CONECT records."

        connect_count = 0
        for i in xrange(len(self.structural_data.atom_names)):
            # No bonded atoms, hence no CONECT record is required.
            if not len(self.structural_data.bonded[i]):
                continue

            # Initialise some data structures.
            flush = 0
            bonded_index = 0
            bonded = ['', '', '', '']

            # Loop over the bonded atoms.
            for j in xrange(len(self.structural_data.bonded[i])):
                # End of the array, hence create the CONECT record in this iteration.
                if j == len(self.structural_data.bonded[i])-1:
                    flush = 1

                # Only four covalently bonded atoms allowed in one CONECT record.
                if bonded_index == 3:
                    flush = 1

                # Get the bonded atom index.
                bonded[bonded_index] = self.structural_data.bonded[i][j]

                # Increment the bonded_index value.
                bonded_index = bonded_index + 1

                # Generate the CONECT record and increment the counter.
                if flush:
                    # Write the CONECT record.
                    file.write("%-6s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('CONECT', i+1, bonded[0], bonded[1], bonded[2], bonded[3], '', '', '', '', '', ''))

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


class Structure_container:
    """The container for the structural information.

    The structural data object for this class is a container possessing a number of different arrays
    corresponding to different structural information.  These objects include:

        - atom_name:  The atom name.
        - bonded:  Each element an array of bonded atom indecies.
        - chain_id:  The chain ID.
        - element:  The element symbol.
        - pdb_record:  The optional PDB record name (one of ATOM, HETATM, or TER).
        - res_name:  The residue name.
        - res_num:  The residue number.
        - seg_id:  The segment ID.
        - x:  The x coordinate of the atom.
        - y:  The y coordinate of the atom.
        - z:  The z coordinate of the atom.

    All arrays should be of equal length so that an atom index can retrieve all the corresponding
    data.  Only the atom identification string is compulsory, all other arrays can contain None.
    """


    def init(self):
        """Initialise all the arrays."""

        # The atom name (array of str).
        atom_name = []

        # The bonded atom indecies (array of arrays of int).
        bonded = []

        # The chain ID (array of str).
        chain_id = []

        # The element symbol (array of str).
        element = []

        # The optional PDB record name (array of str).
        pdb_record = []

        # The residue name (array of str).
        res_name = []

        # The residue number (array of int).
        res_num = []

        # The segment ID (array of int).
        seg_id = []

        # The x coordinate (array of float).
        x = []

        # The y coordinate (array of float).
        y = []

        # The z coordinate (array of float).
        z = []
