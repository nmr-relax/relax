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

# relax module imports.
from relax_errors import RelaxError



class Internal_PDB(Str_object):
    """The internal relax PDB data object."""

    # Identification string.
    id = 'internal pdb'


    def atom_add(self, atomic_data=None, atom_id=None, record_name='', atom_name='', res_name='', chain_id='', res_num=None, pos=[None, None, None], segment_id='', element=''):
        """Function for adding an atom to the atomic_data structure.

        The atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.
            1:  The record name (one of ATOM, HETATM, or TER).
            2:  Atom name.
            3:  Residue name.
            4:  Chain ID.
            5:  Residue number.
            6:  The x coordinate of the atom.
            7:  The y coordinate of the atom.
            8:  The z coordinate of the atom.
            9:  Segment ID.
            10:  Element symbol.
            11+:  The bonded atom numbers.

        This function will create the key-value pair for the given atom.


        @param atomic_data: The dictionary to place the atomic data into.
        @type atomic_data:  dict
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
        @return:            None
        """

        # Initialise the key-value pair.
        atomic_data[atom_id] = []

        # Fill the positions.
        atomic_data[atom_id].append(len(atomic_data))
        atomic_data[atom_id].append(record_name)
        atomic_data[atom_id].append(atom_name)
        atomic_data[atom_id].append(res_name)
        atomic_data[atom_id].append(chain_id)
        atomic_data[atom_id].append(res_num)
        atomic_data[atom_id].append(pos[0])
        atomic_data[atom_id].append(pos[1])
        atomic_data[atom_id].append(pos[2])
        atomic_data[atom_id].append(segment_id)
        atomic_data[atom_id].append(element)


    def atom_connect(self, atomic_data=None, atom_id=None, bonded_id=None):
        """Function for connecting two atoms within the atomic_data data structure.

        The atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.
            1:  The record name (one of ATOM, HETATM, or TER).
            2:  Atom name.
            3:  Residue name.
            4:  Chain ID.
            5:  Residue number.
            6:  The x coordinate of the atom.
            7:  The y coordinate of the atom.
            8:  The z coordinate of the atom.
            9:  Segment ID.
            10:  Element symbol.
            11+:  The bonded atom numbers.

        This function will find the atom number corresponding to both the atom_id and bonded_id.
        The bonded_id atom number will then be appended to the atom_id array.  Because the
        connections work both ways in the PDB file, the atom_id atom number will be appended to the
        bonded_id atom array as well.


        @param atomic_data: The dictionary to place the atomic data into.
        @type atomic_data:  dict
        @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
        @type atom_id:      str
        @param bonded_id:   The second atom identifier.  This is used as the key within the
                            dictionary.
        @type bonded_id:    str
        """

        # Find the atom number corresponding to atom_id.
        if atomic_data.has_key(atom_id):
            atom_num = atomic_data[atom_id][0]
        else:
            raise RelaxError, "The atom corresponding to the atom_id " + `atom_id` + " doesn't exist."

        # Find the atom number corresponding to bonded_id.
        if atomic_data.has_key(bonded_id):
            bonded_num = atomic_data[bonded_id][0]
        else:
            raise RelaxError, "The atom corresponding to the bonded_id " + `bonded_id` + " doesn't exist."

        # Add the bonded_id to the atom_id array.
        atomic_data[atom_id].append(bonded_num)

        # Add the atom_id to the bonded_id array.
        atomic_data[bonded_id].append(atom_num)


    def get_chemical_name(self, hetID):
        """Function for returning the chemical name corresponding to the given residue ID.

        The following names are currently returned:
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


    def terminate(self, atomic_data=None, atom_id_ext='', res_num=None):
        """Function for terminating the chain by adding a TER record to the atomic_data object.

        @param atomic_data:     The dictionary to place the atomic data into.
        @type atomic_data:      dict
        @param atom_id_ext:     The atom identifier extension.
        @type atom_id_ext:      str
        @param res_num:         The residue number.
        @type res_num:          int
        """

        # The name of the last residue.
        atomic_arrays = atomic_data.values()
        atomic_arrays.sort()
        last_res = atomic_arrays[-1][3]

        # Add the TER 'atom'.
        atom_add(atomic_data=atomic_data, atom_id='TER' + atom_id_ext, record_name='TER', res_name=last_res, res_num=res_num)


    def write_pdb_file(self, atomic_data, file):
        """Function for creating a PDB file from the given data.

        Introduction
        ============

        A number of PDB records including HET, HETNAM, FORMUL, HETATM, TER, CONECT, MASTER, and END
        are created.  To create the non-standard residue records HET, HETNAM, and FORMUL, the data
        structure 'het_data' is created.  It is an array of arrays where the first dimension
        corresponds to a different residue and the second dimension has the elements:

            0:  Residue number.
            1:  Residue name.
            2:  Chain ID.
            3:  Total number of atoms in the residue.
            4:  Number of H atoms in the residue.
            5:  Number of C atoms in the residue.


        The PDB records
        ===============

        The following information about the PDB records has been taken from the "Protein Data Bank
        Contents Guide: Atomic Coordinate Entry Format Description" version 2.1 (draft), October 25
        1996.

        HET record
        ----------

        The HET record describes non-standard residues.  The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "HET   "     |                                                |
        |  8 - 10 | LString(3)   | hetID        | Het identifier, right-justified.               |
        | 13      | Character    | ChainID      | Chain identifier.                              |
        | 14 - 17 | Integer      | seqNum       | Sequence number.                               |
        | 18      | AChar        | iCode        | Insertion code.                                |
        | 21 - 25 | Integer      | numHetAtoms  | Number of HETATM records for the group present |
        |         |              |              | in the entry.                                  |
        | 31 - 70 | String       | text         | Text describing Het group.                     |
        |_________|______________|______________|________________________________________________|


        HETNAM record
        -------------

        The HETNAM associates a chemical name with the hetID from the HET record.  The format is of
        the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "HETNAM"     |                                                |
        |  9 - 10 | Continuation | continuation | Allows concatenation of multiple records.      |
        | 12 - 14 | LString(3)   | hetID        | Het identifier, right-justified.               |
        | 16 - 70 | String       | text         | Chemical name.                                 |
        |_________|______________|______________|________________________________________________|


        FORMUL record
        -------------

        The chemical formula for non-standard groups. The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "FORMUL"     |                                                |
        |  9 - 10 | Integer      | compNum      | Component number.                              |
        | 13 - 15 | LString(3)   | hetID        | Het identifier.                                |
        | 17 - 18 | Integer      | continuation | Continuation number.                           |
        | 19      | Character    | asterisk     | "*" for water.                                 |
        | 20 - 70 | String       | text         | Chemical formula.                              |
        |_________|______________|______________|________________________________________________|


        ATOM record
        -----------

        The ATOM record contains the atomic coordinates for atoms belonging to standard residues.
        The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "ATOM"       |                                                |
        |  7 - 11 | Integer      | serial       | Atom serial number.                            |
        | 13 - 16 | Atom         | name         | Atom name.                                     |
        | 17      | Character    | altLoc       | Alternate location indicator.                  |
        | 18 - 20 | Residue name | resName      | Residue name.                                  |
        | 22      | Character    | chainID      | Chain identifier.                              |
        | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
        | 27      | AChar        | iCode        | Code for insertion of residues.                |
        | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X in Angstroms.     |
        | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y in Angstroms.     |
        | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z in Angstroms.     |
        | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
        | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
        | 73 - 76 | LString(4)   | segID        | Segment identifier, left-justified.            |
        | 77 - 78 | LString(2)   | element      | Element symbol, right-justified.               |
        | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
        |_________|______________|______________|________________________________________________|


        HETATM record
        -------------

        The HETATM record contains the atomic coordinates for atoms belonging to non-standard
        groups.  The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "HETATM"     |                                                |
        |  7 - 11 | Integer      | serial       | Atom serial number.                            |
        | 13 - 16 | Atom         | name         | Atom name.                                     |
        | 17      | Character    | altLoc       | Alternate location indicator.                  |
        | 18 - 20 | Residue name | resName      | Residue name.                                  |
        | 22      | Character    | chainID      | Chain identifier.                              |
        | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
        | 27      | AChar        | iCode        | Code for insertion of residues.                |
        | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X.                  |
        | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y.                  |
        | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z.                  |
        | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
        | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
        | 73 - 76 | LString(4)   | segID        | Segment identifier; left-justified.            |
        | 77 - 78 | LString(2)   | element      | Element symbol; right-justified.               |
        | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
        |_________|______________|______________|________________________________________________|


        TER record
        ----------

        The end of the ATOM and HETATM records for a chain.  According to the draft atomic
        coordinate entry format description:

        "The TER record has the same residue name, chain identifier, sequence number and insertion
        code as the terminal residue. The serial number of the TER record is one number greater than
        the serial number of the ATOM/HETATM preceding the TER."

        The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "TER   "     |                                                |
        |  7 - 11 | Integer      | serial       | Serial number.                                 |
        | 18 - 20 | Residue name | resName      | Residue name.                                  |
        | 22      | Character    | chainID      | Chain identifier.                              |
        | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
        | 27      | AChar        | iCode        | Insertion code.                                |
        |_________|______________|______________|________________________________________________|


        CONECT record
        -------------

        The connectivity between atoms.  This is required for all HET groups and for non-standard
        bonds.  The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "CONECT"     |                                                |
        |  7 - 11 | Integer      | serial       | Atom serial number                             |
        | 12 - 16 | Integer      | serial       | Serial number of bonded atom                   |
        | 17 - 21 | Integer      | serial       | Serial number of bonded atom                   |
        | 22 - 26 | Integer      | serial       | Serial number of bonded atom                   |
        | 27 - 31 | Integer      | serial       | Serial number of bonded atom                   |
        | 32 - 36 | Integer      | serial       | Serial number of hydrogen bonded atom          |
        | 37 - 41 | Integer      | serial       | Serial number of hydrogen bonded atom          |
        | 42 - 46 | Integer      | serial       | Serial number of salt bridged atom             |
        | 47 - 51 | Integer      | serial       | Serial number of hydrogen bonded atom          |
        | 52 - 56 | Integer      | serial       | Serial number of hydrogen bonded atom          |
        | 57 - 61 | Integer      | serial       | Serial number of salt bridged atom             |
        |_________|______________|______________|________________________________________________|


        MASTER record
        -------------

        The control record for bookkeeping.  The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "MASTER"     |                                                |
        | 11 - 15 | Integer      | numRemark    | Number of REMARK records                       |
        | 16 - 20 | Integer      | "0"          |                                                |
        | 21 - 25 | Integer      | numHet       | Number of HET records                          |
        | 26 - 30 | Integer      | numHelix     | Number of HELIX records                        |
        | 31 - 35 | Integer      | numSheet     | Number of SHEET records                        |
        | 36 - 40 | Integer      | numTurn      | Number of TURN records                         |
        | 41 - 45 | Integer      | numSite      | Number of SITE records                         |
        | 46 - 50 | Integer      | numXform     | Number of coordinate transformation records    |
        |         |              |              | (ORIGX+SCALE+MTRIX)                            |
        | 51 - 55 | Integer      | numCoord     | Number of atomic coordinate records            |
        |         |              |              | (ATOM+HETATM)                                  |
        | 56 - 60 | Integer      | numTer       | Number of TER records                          |
        | 61 - 65 | Integer      | numConect    | Number of CONECT records                       |
        | 66 - 70 | Integer      | numSeq       | Number of SEQRES records                       |
        |_________|______________|______________|________________________________________________|


        END record
        ----------

        The end of the PDB file.  The format is of the record is:
        __________________________________________________________________________________________
        |         |              |              |                                                |
        | Columns | Data type    | Field        | Definition                                     |
        |_________|______________|______________|________________________________________________|
        |         |              |              |                                                |
        |  1 -  6 | Record name  | "END   "     |                                                |
        |_________|______________|______________|________________________________________________|



        @param atomic_data: The dictionary containing the atomic data.
        @type atomic_data:  dict
        @param file:        The PDB file object.  This object must be writable.
        @type file:         file object
        """

        # Sort the atoms.
        #################

        # Convert the atomic_data structure from a dictionary of arrays to an array of arrays and sort it by atom number.
        atomic_arrays = atomic_data.values()
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
            chemical_name = get_chemical_name(het[1])

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
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, len(het_data), 0, 0, 0, 0, 0, len(atomic_data), 1, connect_count, 0))


        # END.
        ######

        # Print out.
        print "Creating the END record."

        # Write the END record.
        file.write("END\n")
