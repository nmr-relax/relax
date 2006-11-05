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

from math import sqrt, cos, pi, sin
from Numeric import Float64, arccos, dot, zeros
from os import F_OK, access
from re import compile, match
import Scientific.IO.PDB


class PDB:
    def __init__(self, relax):
        """Class containing the PDB related functions."""

        self.relax = relax

        # Print flag.
        self.print_flag = 1


    def atom_add(self, atom_id=None, atom_name='', res_name='', chain_id='', res_num=None, pos=None, segment_id='', element=''):
        """Function for adding an atom to the self.atomic_data structure.

        The self.atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.
            1:  Atom name.
            2:  Residue name.
            3:  Chain ID.
            4:  Residue number.
            5:  The x coordinate of the atom.
            6:  The y coordinate of the atom.
            7:  The z coordinate of the atom.
            8:  Segment ID.
            9:  Element symbol.
            10+:  The bonded atom numbers.

        This function will create the key-value pair for the given atom.


        @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
        @type atom_id:      str
        @param atom_name:   The atom name, e.g. H1.
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
        self.atomic_data[atom_id] = []

        # Fill the positions.
        self.atomic_data[atom_id].append(len(self.atomic_data) + 1)
        self.atomic_data[atom_id].append(atom_name)
        self.atomic_data[atom_id].append(residue_name)
        self.atomic_data[atom_id].append(chain_id)
        self.atomic_data[atom_id].append(res_num)
        self.atomic_data[atom_id].append(pos[0])
        self.atomic_data[atom_id].append(pos[1])
        self.atomic_data[atom_id].append(pos[2])
        self.atomic_data[atom_id].append(segment_id)
        self.atomic_data[atom_id].append(element)


    def atom_connect(self, atom_id=None, bonded_id=None):
        """Function for connecting two atoms within the self.atomic_data data structure.

        The self.atomic_data data structure is a dictionary of arrays.  The keys correspond to the
        'atom_id' strings.  The elements of the array are:

            0:  Atom number.
            1:  Atom name.
            2:  Residue name.
            3:  Chain ID.
            4:  Residue number.
            5:  The x coordinate of the atom.
            6:  The y coordinate of the atom.
            7:  The z coordinate of the atom.
            8:  Segment ID.
            9:  Element symbol.
            10+:  The bonded atom numbers.

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


    def centre_of_mass(self):
        """Calculate and return the centre of mass of the structure."""

        # Print out.
        print "Calculating the centre of mass."

        # Initialise the centre of mass.
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

        # Return the centre of mass.
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

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Test if the PDB file of the macromolecule has been loaded.
        if not self.relax.data.pdb.has_key(self.run):
            raise RelaxNoPdbError, self.run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError, self.run


        # Initialise the PDB data.
        ##########################

        # The atom and atomic connections data structures.
        self.atomic_data = {}

        # Chain ID, residue number, residue name, chemical name, and occupancy.
        chain_id = 'A'
        res_num = 1
        res_name = 'TNS'
        chemical_name = 'Tensor'
        occupancy = 1.0


        # Center of mass.
        #################

        # Calculate the centre of mass.
        R = self.centre_of_mass()

        # Add the central atom.
        self.atom_add(atom_id='R', element='C', pos=R)


        # Axes of the tensor.
        #####################

        # Create the unique axis of the spheroid.
        if self.relax.data.diff[self.run].type == 'spheroid':
            # Print out.
            print "\nGenerating the unique axis of the diffusion tensor."

            # The Dpar vector.
            Dpar_vect = self.relax.data.diff[self.run].Dpar_unit * self.relax.data.diff[self.run].Dpar * scale

            # The negative Dpar vector.
            Dpar_vect_neg = -Dpar_vect

            # Position of both vectors relative to the centre of mass.
            Dpar_vect = R + Dpar_vect
            Dpar_vect_neg = R + Dpar_vect_neg

            # Add the atom and connect it to the centre of mass.
            self.atom_add(atom_id='Dpar', element='C', pos=Dpar_vect)
            self.atom_add(atom_id='Dpar_neg', element='C', pos=Dpar_vect_neg)
            self.atom_connect(atom_id='Dpar', bonded_id='R')
            self.atom_connect(atom_id='Dpar_neg', bonded_id='R')

            # Print out.
            print "    Scaling factor:                      " + `scale`
            print "    Dpar vector (scaled + shifted to R): " + `Dpar_vect`

        # Create the three axes of the ellipsoid.
        if self.relax.data.diff[self.run].type == 'ellipsoid':
            # Print out.
            print "Generating the three axes of the ellipsoid."

            # The Dx, Dy, and Dz vectors.
            Dx_vect = self.relax.data.diff[self.run].Dx_unit * self.relax.data.diff[self.run].Dx * scale
            Dy_vect = self.relax.data.diff[self.run].Dy_unit * self.relax.data.diff[self.run].Dy * scale
            Dz_vect = self.relax.data.diff[self.run].Dz_unit * self.relax.data.diff[self.run].Dz * scale

            # The negative Dx, Dy, and Dz vectors.
            Dx_vect_neg = -Dx_vect
            Dy_vect_neg = -Dy_vect
            Dz_vect_neg = -Dz_vect

            # Positions relative to the centre of mass.
            Dx_vect = R + Dx_vect
            Dy_vect = R + Dy_vect
            Dz_vect = R + Dz_vect
            Dx_vect_neg = R + Dx_vect_neg
            Dy_vect_neg = R + Dy_vect_neg
            Dz_vect_neg = R + Dz_vect_neg

            # Add the atoms and connect them to the centre of mass.
            self.atom_add(atom_id='Dx', element='C', pos=Dx_vect)
            self.atom_add(atom_id='Dy', element='C', pos=Dy_vect)
            self.atom_add(atom_id='Dz', element='C', pos=Dz_vect)
            self.atom_add(atom_id='Dx_neg', element='C', pos=Dx_vect_neg)
            self.atom_add(atom_id='Dy_neg', element='C', pos=Dy_vect_neg)
            self.atom_add(atom_id='Dz_neg', element='C', pos=Dz_vect_neg)
            self.atom_connect(atom_id='Dx', bonded_id='R')
            self.atom_connect(atom_id='Dy', bonded_id='R')
            self.atom_connect(atom_id='Dz', bonded_id='R')
            self.atom_connect(atom_id='Dx_neg', bonded_id='R')
            self.atom_connect(atom_id='Dy_neg', bonded_id='R')
            self.atom_connect(atom_id='Dz_neg', bonded_id='R')

            # Print out.
            print "    Scaling factor:                      " + `scale`
            print "    Dx vector (scaled + shifted to R):   " + `Dx_vect`
            print "    Dy vector (scaled + shifted to R):   " + `Dy_vect`
            print "    Dz vector (scaled + shifted to R):   " + `Dz_vect`


        # Vector distribution.
        ######################

        # Print out.
        print "\nGenerating the geometric object."

        # Increment value.
        inc = 20

        # Get the uniform vector distribution.
        print "    Creating the uniform vector distribution."
        vectors = self.uniform_vect_dist_spherical_angles(inc=20)

        # Loop over the radial array of vectors (change in longitude).
        for i in range(inc):
            # Loop over the vectors of the radial array (change in latitude).
            for j in range(inc/2+2):
                # Index.
                index = i + j*inc

                # Atom id.
                atom_id = 'T' + `i` + 'P' + `j`

                # Rotate the vector into the diffusion frame.
                vector = dot(self.relax.data.diff[self.run].rotation, vectors[index])

                # Set the length of the vector to its diffusion rate within the diffusion tensor geometric object.
                vector = dot(self.relax.data.diff[self.run].tensor, vector)

                # Scale the vector.
                vector = vector * scale

                # Position relative to the centre of mass.
                pos = R + vector

                # Add the vector as a H atom.
                self.atom_add(atom_id=atom_id, element='H', pos=pos)

                # Connect to the previous atom (to generate the longitudinal lines).
                if j != 0:
                    prev_id = 'T' + `i` + 'P' + `j-1`
                    self.atom_connect(atom_id=atom_id, bonded_id=prev_id)

                # Connect across the radial arrays (to generate the latitudinal lines).
                if i != 0:
                    neighbour_id = 'T' + `i-1` + 'P' + `j`
                    self.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)

                # Connect the last radial array to the first (to zip up the geometric object and close the latitudinal lines).
                if i == inc-1:
                    neighbour_id = 'T' + `0` + 'P' + `j`
                    self.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)



        # Create the PDB file.
        ######################

        # Print out.
        print "\nGenerating the PDB file."

        # Open the PDB file for writing.
        tensor_pdb_file = self.relax.IO.open_write_file(self.file, self.dir, force=self.force)

        # Write the data.
        self.write_pdb_file(tensor_pdb_file, chain_id, res_num, res_name, chemical_name, occupancy)

        # Close the file.
        tensor_pdb_file.close()


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

        # Unknown hetID.
        raise RelaxError, "The residue ID (hetID) " + `hetID` + " is not recognised."

        
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
            if not hasattr(self.relax.data.res[self.run][i], 'xh_vect'):
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


    def uniform_vect_dist_spherical_angles(self, inc=20):
        """Uniform distribution of vectors on a sphere using uniform spherical angles.

        This function returns an array of unit vectors uniformly distributed within 3D space.  To
        create the distribution, uniform spherical angles are used.  The two spherical angles are
        defined as

            theta = 2.pi.u,
            phi = cos^-1(2v - 1),

        where

            u in [0, 1),
            v in [0, 1].

        Because theta is defined between [0, pi] and phi is defined between [0, 2pi], for a uniform
        distribution u is only incremented half of 'inc'.  The unit vectors are gerenated using the
        equation

                       | cos(theta) * sin(phi) |
            vector  =  | sin(theta) * sin(phi) |.
                       |      cos(phi)         |

        The vectors of this distribution generate both longitudinal and latitudinal lines.
        """

        # The inc argument must be an even number.
        if inc%2:
            raise RelaxError, "The increment value of " + `inc` + " must be an even number."

        # Generate the increment values of u.
        u = zeros(inc, Float64)
        val = 1.0 / float(inc)
        for i in xrange(inc):
            u[i] = float(i) * val

        # Generate the increment values of v.
        v = zeros(inc/2+2, Float64)
        val = 1.0 / float(inc/2)
        for i in xrange(1, inc/2+1):
            v[i] = float(i-1) * val + val/2.0
        v[-1] = 1.0

        # Generate the distribution of spherical angles theta.
        theta = 2.0 * pi * u

        # Generate the distribution of spherical angles phi.
        phi = arccos(2.0 * v - 1.0)

        # Initialise array of the distribution of vectors.
        vectors = []

        # Loop over the longitudinal lines.
        for j in xrange(len(v)):
            # Loop over the latitudinal lines.
            for i in xrange(len(u)):
                # X coordinate.
                x = cos(theta[i]) * sin(phi[j])

                # Y coordinate.
                y =  sin(theta[i])* sin(phi[j])

                # Z coordinate.
                z = cos(phi[j])

                # Append the vector.
                vectors.append([x, y, z])

        # Return the array of vectors.
        return vectors


    def write_pdb_file(self, file, chain_id, res_num, res_name, chemical_name, occupancy):
        """Function for creating a PDB file from the given data.

        Introduction
        ============

        A number of PDB records including HET, HETNAM, FORMUL, HETATM, TER, CONECT, MASTER, and END
        are created.


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

        The end of the ATOM and HETATM records.  The format is of the record is:
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




        @type file:     str
        @param file:    The PDB file name.
        @return:        None
        """

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

        # Convert the self.atomic_data structure from a dictionary of arrays to an array of arrays and sort it by atom number.
        atomic_arrays = self.atomic_data.values()
        atomic_arrays.sort()

        # Add the HETATM records.
        for array in atomic_arrays:
            # Write the HETATM record.
            file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', array[0], array[1]+`array[0]`, '', res_name, chain_id, res_num, '', array[2], array[3], array[4], occupancy, 0, '', array[1], ''))

        # Terminate (TER record).
        file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', len(self.atomic_data)+1, res_name, chain_id, '', ''))

        # Create the CONECT records.
        connect_count = 0
        for array in atomic_arrays:
            # No bonded atoms, hence no CONECT record is required.
            if len(array) == 4:
                continue

            # The atom number.
            atom_num = array[0]


            # Initialise some data structures.
            flush = 0
            bonded_index = 0
            bonded = ['', '', '', '']

            # Loop over the bonded atoms.
            for i in xrange(len(array[5:])):
                # End of the array, hence create the CONECT record in this iteration.
                if i == len(array[5:])-1:
                    flush = 1

                # Only four covalently bonded atoms allowed in one CONECT record.
                if bonded_index == 3:
                    flush = 1

                # Get the bonded atom name.
                bonded[bonded_index] = array[i+5]

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
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, 1, 0, 0, 0, 0, 0, len(self.atomic_data), 1, connect_count, 0))

        # END.
        file.write("END\n")
