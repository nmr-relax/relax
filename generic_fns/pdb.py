###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
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

from math import sqrt
from Numeric import Float64, dot, zeros
from os import F_OK, access
from re import compile
import Scientific.IO.PDB


class PDB:
    def __init__(self, relax):
        """Class containing the PDB related functions."""

        self.relax = relax

        # Print flag.
        self.print_flag = 1


    def atom_add(self, atom_id, element, pos):
        """Function for adding an atom to the self.atomic_data structure.

        The self.atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.

            1:  Element type.

            2:  The x coordinate of the atom.

            3:  The y coordinate of the atom.

            4:  The z coordinate of the atom.

            5 onwards:  The bonded atom numbers.

        This function will create the key-value pair for the atom.

        """

        # Create the key-value pair.
        # The array elements added are:
        #     The atom number (length of the structure + 1).
        #     The element type.
        #     The coordinates.
        self.atomic_data[atom_id] = [len(self.atomic_data) + 1, element, pos[0], pos[1], pos[2]]


    def atom_connect(self, atom_id, bonded_id):
        """Function for connecting two atoms within the self.atomic_data data structure.

        The self.atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.

            1:  Element type.

            2:  The x coordinate of the atom.

            3:  The y coordinate of the atom.

            4:  The z coordinate of the atom.

            5 onwards:  The bonded atom numbers.

        This function will find the atom number corresponding to both the atom_id and bonded_id.
        The bonded_id atom number will then be appended to the atom_id array.  Because the
        connections work both ways in the PDB file, the atom_id atom number will be appended to the
        bonded_id atom array as well.

        """

        # Find the atom number corresponding to atom_id.
        if self.atomic_data.has_key(atom_id):
            atom_num = self.atomic_data[atom_id][0]
        else:
            raise RelaxError, "The atom corresponding to the atom_id " + `atom_id` + " doesn't exist."

        # Find the atom number corresponding to bonded_id.
        if self.atomic_data.has_key(bonded_id):
            bonded_num = self.atomic_data[bonded_id][0]
        else:
            raise RelaxError, "The atom corresponding to the bonded_id " + `bonded_id` + " doesn't exist."

        # Add the bonded_id to the atom_id array.
        self.atomic_data[atom_id].append(bonded_num)

        # Add the atom_id to the bonded_id array.
        self.atomic_data[bonded_id].append(atom_num)


    def atomic_mass(self, element=None):
        """Return the atomic mass of the given element."""

        # Proton.
        if element == 'H' or element == 'Q':
            return 1.00794

        # Carbon.
        elif element == 'C':
            return 12.0107

        # Nitrogen.
        elif element == 'N':
            return 14.0067

        # Oxygen.
        elif element == 'O':
            return 15.9994

        # Sulphur.
        elif element == 'S':
            return 32.065

        # Unknown.
        else:
            raise RelaxError, "The mass of the element " + `element` + " has not yet been programmed into relax."


    def center_of_mass(self):
        """Calculate and return the center of mass of the structure."""

        # Print out.
        print "Calculating the center of mass."

        # Initialise the center of mass.
        R = zeros(3, Float64)

        # Initialise the total mass.
        M = 0.0

        # Loop over the structures.
        for struct in self.relax.data.pdb[self.run].structures:
            # Protein.
            if struct.peptide_chains:
                chains = struct.peptide_chains

            # RNA/DNA.
            elif struct.nucleotide_chains:
                chains = struct.nucleotide_chains

            # Loop over the residues of the protein in the PDB file.
            for res in chains[0].residues:
                # Find the corresponding residue in 'self.relax.data'.
                found = 0
                for res_data in self.relax.data.res[self.run]:
                    if res.number == res_data.num:
                        found = 1
                        break

                # Doesn't exist.
                if not found:
                    continue

                # Skip unselected residues.
                if not res_data.select:
                    continue

                # Loop over the atoms of the residue.
                for atom in res:
                    # Atomic mass.
                    mass = self.atomic_mass(atom.properties['element'])

                    # Total mass.
                    M = M + mass

                    # Sum of mass * position.
                    R = R + mass * atom.position.array

        # Normalise.
        R = R / M

        # Final print out.
        print "    Total mass:      M = " + `M`
        print "    Center of mass:  R = " + `R`
        print

        # Return the center of mass.
        return R


    def create_tensor_pdb(self, run=None, scale=1.8e-6, file=None, dir=None, force=0):
        """The pdb loading function."""

        # Arguments.
        self.run = run
        self.scale = scale
        self.file = file
        self.dir = dir
        self.force = force

        # Tests.
        ########

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if PDB data corresponding to the run already exists.
        if not self.relax.data.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError, self.run


        # Initialise the PDB data.
        ##########################

        # The atom and atomic connections data structures.
        self.atomic_data = {}

        # Chain ID, residue number, residue name, chemical name, occupancy, and default element.
        chain_id = 'A'
        res_num = 1
        res_name = 'TNS'
        chemical_name = 'Tensor'
        occupancy = 1.0
        element = 'H'


        # Center of mass.
        #################

        # Calculate the center of mass.
        R = self.center_of_mass()

        # Add the central atom.
        self.atom_add(atom_id='R', element='C', pos=R)


        # Axes of the tensor.
        #####################

        # Get the unique axis of the spheroid.
        if self.relax.data.diff[self.run].type == 'spheroid':
            # Print out.
            print "Calculating the Dpar unit vector (the unique axis of the diffusion tensor)."

            # The Dpar unit vector.
            Dpar_unit = self.relax.data.diff[self.run].Dpar_unit

            # The Dpar vector.
            Dpar_vect = Dpar_unit * self.relax.data.diff[self.run].Dpar * scale

            # Position relative to the center of mass.
            pos = R + Dpar_vect

            # Add the atom and connect it to the center of mass.
            self.atom_add(atom_id='Dpar', element='C', pos=pos)
            self.atom_connect(atom_id='Dpar', bonded_id='R')

            # Print out.
            print "    Scaling factor:              " + `scale`
            print "    Unit vector:                 " + `Dpar_unit`
            print "    Dpar vector (scaled):        " + `Dpar_vect`
            print "    Relative to center of mass:  " + `pos`
            print


        # Create the PDB file.
        ######################

        # Open the PDB file for writing.
        tensor_pdb_file = self.relax.IO.open_write_file(self.file, self.dir, force=self.force)

        # Write the data.
        self.write_pdb_file(tensor_pdb_file, chain_id, res_num, res_name, chemical_name, occupancy)

        # Close the file.
        tensor_pdb_file.close()


    def load_structures(self):
        """Function for loading the structures from the PDB file."""

        # Use pointers (references) if the PDB data exists in another run.
        for run in self.relax.data.run_names:
            if self.relax.data.pdb.has_key(run) and hasattr(self.relax.data.pdb[run], 'structures') and self.relax.data.pdb[run].file_name == self.file and self.relax.data.pdb[run].model == self.model:
                # Make a pointer to the data.
                self.relax.data.pdb[self.run].structures = self.relax.data.pdb[run].structures

                # Print out.
                if self.print_flag:
                    print "Using the structures from the run " + `run` + "."
                    for i in xrange(len(self.relax.data.pdb[self.run].structures)):
                        print self.relax.data.pdb[self.run].structures[i]

                # Exit this function.
                return

        # Initialisation.
        self.relax.data.pdb[self.run].structures = []

        # Load the structure i from the PDB file.
        if type(self.model) == int:
            # Print out.
            if self.print_flag:
                print "Loading structure " + `self.model` + " from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(self.file_path, self.model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, self.file_path

            # Print the PDB info.
            if self.print_flag:
                print str

            # Place the structure in 'self.relax.data.pdb[self.run]'.
            self.relax.data.pdb[self.run].structures.append(str)


        # Load all structures.
        else:
            # Print out.
            if self.print_flag:
                print "Loading all structures from the PDB file."

            # First model.
            i = 1

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(self.file_path, i)

                # No model 1.
                if len(str) == 0 and i == 1:
                    str = Scientific.IO.PDB.Structure(self.file_path)
                    if len(str) == 0:
                        raise RelaxPdbLoadError, self.file_path

                # Test if the last structure has been reached.
                if len(str) == 0:
                    del str
                    break

                # Print the PDB info.
                if self.print_flag:
                    print str

                # Place the structure in 'self.relax.data.pdb[self.run]'.
                self.relax.data.pdb[self.run].structures.append(str)

                # Increment i.
                i = i + 1


    def read(self, run=None, file=None, dir=None, model=None, load_seq=1, fail=1, print_flag=1):
        """The pdb loading function."""

        # Arguments.
        self.run = run
        self.file = file
        self.dir = dir
        self.model = model
        self.load_seq = load_seq
        self.fail = fail
        self.print_flag = print_flag

        # Tests.
        ########

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if PDB data corresponding to the run already exists.
        if self.relax.data.pdb.has_key(self.run):
            raise RelaxPdbError, self.run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # The file path.
        self.file_path = self.relax.IO.file_path(self.file, self.dir)

        # Test if the file exists.
        if not access(self.file_path, F_OK):
            if fail:
                raise RelaxFileError, ('PDB', self.file_path)
            else:
                warn(RelaxNoPDBFileWarning(self.file_path))
                return


        # Data creation.
        ################

        # Add the run to the PDB data structure.
        self.relax.data.pdb.add_item(self.run)

        # File name.
        self.relax.data.pdb[self.run].file_name = self.file_path

        # Model.
        self.relax.data.pdb[self.run].model = model


        # Load the structures.
        ######################

        self.load_structures()


        # Finish.
        #########

        # Sequence loading.
        if self.load_seq and not self.relax.data.res.has_key(self.run):
            self.relax.generic.sequence.load_PDB_sequence(self.run)

        # Load into Molmol (if running).
        self.relax.generic.molmol.open_pdb(self.run)


    def set_vector(self, run=None, res=None, xh_vect=None):
        """Function for setting the XH unit vectors."""

        # Place the XH unit vector in 'self.relax.data.res'.
        self.relax.data.res[run][res].xh_vect = xh_vect


    def vectors(self, run=None, heteronuc=None, proton=None, res_num=None, res_name=None):
        """Function for calculating/extracting the XH unit vector from the loaded structure."""

        # Arguments.
        self.heteronuc = heteronuc
        self.proton = proton

        # Test if the PDB file has been loaded.
        if not self.relax.data.pdb.has_key(run):
            raise RelaxPdbError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the residue number is a valid regular expression.
        if type(res_num) == str:
            try:
                compile(res_num)
            except:
                raise RelaxRegExpError, ('residue number', res_num)

        # Test if the residue name is a valid regular expression.
        if res_name:
            try:
                compile(res_name)
            except:
                raise RelaxRegExpError, ('residue name', res_name)

        # Test that the nuclei have been correctly set.
        if self.heteronuc == self.proton:
            raise RelaxError, "The proton and heteronucleus are set to the same atom."

        # Print out.
        if self.print_flag:
            print "\nCalculating unit XH vectors.\n"

        # Nuclei.
        self.relax.data.pdb[self.run].proton = proton
        self.relax.data.pdb[self.run].heteronuc = heteronuc

        # Number of structures.
        num_str = len(self.relax.data.pdb[self.run].structures)

        # Create a temporary vector list for each residue.
        for i in xrange(len(self.relax.data.res[self.run])):
            self.relax.data.res[self.run][i].xh_vect = []

        # Loop over the structures.
        for i in xrange(num_str):
            # Print out.
            if self.print_flag:
                print "\nStructure " + `i + 1` + "\n"

            # Reassign the first peptide or nucleotide chain of the first structure.
            if self.relax.data.pdb[self.run].structures[i].peptide_chains:
                pdb_residues = self.relax.data.pdb[self.run].structures[i].peptide_chains[0].residues
            elif self.relax.data.pdb[self.run].structures[i].nucleotide_chains:
                pdb_residues = self.relax.data.pdb[self.run].structures[i].nucleotide_chains[0].residues
            else:
                raise RelaxNoPdbChainError

            # Loop over the sequence.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Remap the data structure 'self.relax.data.res[self.run][j]'.
                data = self.relax.data.res[self.run][j]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Skip the residue if there is no match to 'num'.
                if type(res_num) == int:
                    if not data.num == res_num:
                        continue
                elif type(res_num) == str:
                    if not match(res_num, `data.num`):
                        continue

                # Skip the residue if there is no match to 'name'.
                if res_name != None:
                    if not match(res_name, data.name):
                        continue

                # Find the corresponding residue in the PDB.
                pdb_res = None
                for k in xrange(len(pdb_residues)):
                    if data.num == pdb_residues[k].number:
                        pdb_res = pdb_residues[k]
                        break
                if pdb_res == None:
                    raise RelaxNoResError, data.num

                # Test if the proton atom exists for residue i.
                if not pdb_res.atoms.has_key(self.proton):
                    warn(RelaxNoAtomWarning(self.proton, data.num))
                    data.xh_vect.append(None)

                # Test if the heteronucleus atom exists for residue i.
                elif not pdb_res.atoms.has_key(self.heteronuc):
                    warn(RelaxNoAtomWarning(self.heteronuc, data.num))
                    data.xh_vect.append(None)

                # Calculate the vector.
                else:
                    # Get the proton position.
                    posH = pdb_res.atoms[self.proton].position.array

                    # Get the heteronucleus position.
                    posX = pdb_res.atoms[self.heteronuc].position.array

                    # Calculate the XH bond vector.
                    vector = posH - posX

                    # Normalisation factor.
                    norm_factor = sqrt(dot(vector, vector))

                    # Test for zero length.
                    if norm_factor == 0.0:
                        if self.print_flag:
                            print "The XH bond vector for residue " + `data.num` + " is of zero length."
                        data.xh_vect.append(None)

                    # Calculate the normalised vector.
                    else:
                        data.xh_vect.append(vector / norm_factor)

        # Print out.
        if self.print_flag:
            if num_str > 1:
                print "\nCalculating and averaging the unit XH vectors from all structures."
            else:
                print "\nCalculating the unit XH vectors from the structure."

        # Average the vectors and convert xh_vect from an array of vectors to a vector.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Skip the residue if there is no match to 'num'.
            if type(res_num) == int:
                if not data.num == res_num:
                    continue
            elif type(res_num) == str:
                if not match(res_num, `data.num`):
                    continue

            # Skip the residue if there is no match to 'name'.
            if res_name != None:
                if not match(res_name, data.name):
                    continue

            # No vectors.
            if data.xh_vect[0] == None:
                del data.xh_vect
                continue

            # Average vectors.
            ave_vector = zeros(3, Float64)

            # Sum the vectors.
            for j in xrange(num_str):
                # Sum.
                ave_vector = ave_vector + data.xh_vect[j]

            # Average the vector.
            ave_vector = ave_vector / num_str

            # Replace the temporary vector list with the normalised average vector.
            data.xh_vect = ave_vector / sqrt(dot(ave_vector, ave_vector))


    def write_pdb_file(self, file, chain_id, res_num, res_name, chemical_name, occupancy):
        """Function for creating a PDB file from the given data."""

        # The HET record.
        file.write("%-6s %3s  %1s%4s%1s  %5s     %-40s\n" % ('HET', res_name, chain_id, res_num, '', len(self.atomic_data), ''))

        # The HETNAM record.
        file.write("%-6s  %2s %3s %-55s\n" % ('HETNAM', '', res_name, chemical_name))

        # Count the elements.
        H_count = 0
        C_count = 0
        for key in self.atomic_data:
            # The element.
            element = self.atomic_data[key][1]

            # Protons.
            if element == 'H':
                H_count = H_count + 1

            # Carbons.
            elif element == 'C':
                C_count = C_count + 1

            # Unsupported element type.
            else:
                raise RelaxError, "The element " + `element` + " was expected to be one of ['H', 'C']."

        # Chemical formula.
        formula = ''
        if H_count:
            if formula:
                formula = formula + ' '
            formula = formula + 'H' + `H_count`
        if C_count:
            if formula:
                formula = formula + ' '
            formula = formula + 'C' + `C_count`

        # The FORMUL record (chemical formula).
        file.write("%-6s  %2s  %3s %2s%1s%-51s\n" % ('FORMUL', 1, res_name, '', '', formula))

        # Add the HETATM records.
        for key in self.atomic_data:
            # Write the HETATM record.
            file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', self.atomic_data[key][0], self.atomic_data[key][1]+`self.atomic_data[key][0]`, '', res_name, chain_id, res_num, '', self.atomic_data[key][2], self.atomic_data[key][3], self.atomic_data[key][4], occupancy, 0, '', self.atomic_data[key][1], ''))

        # Terminate (TER record).
        file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', len(self.atomic_data)+1, res_name, chain_id, '', ''))

        # Create the CONECT records.
        connect_count = 0
        for key in self.atomic_data:
            # The atom number.
            atom_num = self.atomic_data[key][0]

            # First bonded atom.
            if len(self.atomic_data[key]) > 5:
                bonded1 = self.atomic_data[key][5]

            # No CONECT record required!
            else:
                continue

            # Second bonded atom.
            if len(self.atomic_data[key]) > 6:
                bonded2 = self.atomic_data[key][6]
            else:
                bonded2 = ''

            # Third bonded atom.
            if len(self.atomic_data[key]) > 7:
                bonded3 = self.atomic_data[key][7]
            else:
                bonded3 = ''

            # Forth bonded atom.
            if len(self.atomic_data[key]) > 8:
                bonded4 = self.atomic_data[key][8]
            else:
                bonded4 = ''

            # Write the CONECT record.
            file.write("%-6s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('CONECT', atom_num, bonded1, bonded2, bonded3, bonded4, '', '', '', '', '', ''))

            # Increment the CONECT record count.
            connect_count = connect_count + 1

        # MASTER record.
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, 1, 0, 0, 0, 0, 0, len(self.atomic_data), 1, connect_count, 0))

        # END.
        file.write("END\n")
