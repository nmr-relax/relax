###############################################################################
#                                                                             #
# Copyright (C) 2003-2015 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the internal relax structural object."""

# Python module imports.
from copy import deepcopy
from numpy import array, dot, float64, linalg, zeros
import os
from os import F_OK, access, curdir, sep
from os.path import abspath
from re import search
import sys
from time import asctime
from warnings import warn

# relax module imports.
from lib import regex
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxNoneIntError, RelaxNoPdbError
from lib.io import file_root, open_read_file
from lib.selection import Selection
from lib.sequence import aa_codes_three_to_one
from lib.structure import pdb_read, pdb_write
from lib.structure.internal.displacements import Displacements
from lib.structure.internal.models import ModelList
from lib.structure.internal.molecules import MolContainer
from lib.structure.internal.selection import Internal_selection
from lib.warnings import RelaxWarning
from lib.xml import object_to_xml, xml_to_object


# Module variables.
CHAIN_ID_LIST = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
RELAX_VERSION = None


class Internal:
    """The internal relax structural data object.

    The structural data object for this class is a container possessing a number of different arrays corresponding to different structural information.  These objects are described in the structural container docstring.
    """

    def __init__(self):
        """Initialise the structural object."""

        # Initialise the empty model list.
        self.structural_data = ModelList()


    def _bonded_atom(self, attached_atom, index, mol):
        """Find the atom named attached_atom directly bonded to the atom located at the index.

        @param attached_atom:   The name of the attached atom to return.
        @type attached_atom:    str
        @param index:           The index of the atom which the attached atom is attached to.
        @type index:            int
        @param mol:             The molecule container.
        @type mol:              MolContainer instance
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element name (str), and atomic position (Numeric array of len 3)
        """

        # Init.
        bonded_found = False

        # No bonded atoms, so determine the connectivities.
        if not mol.bonded[index]:
            # Determine the molecule type if needed.
            if not hasattr(mol, 'type'):
                self._mol_type(mol)

            # Protein.
            if mol.type == 'protein':
                self._protein_connect(mol)

            # Find everything within 2 Angstroms and say they are bonded.
            else:
                self._find_bonded_atoms(index, mol, radius=2)

        # Loop over the bonded atoms.
        matching_list = []
        for bonded_index in mol.bonded[index]:
            if regex.search(mol.atom_name[bonded_index], attached_atom):
                matching_list.append(bonded_index)
        num_attached = len(matching_list)

        # Problem.
        if num_attached > 1:
            # Get the atom names.
            matching_names = []
            for i in matching_list:
                matching_names.append(mol.atom_name[i])

            # Return nothing but a warning.
            return None, None, None, None, None, 'More than one attached atom found: ' + repr(matching_names)

        # No attached atoms.
        if num_attached == 0:
            return None, None, None, None, None, "No attached atom could be found"

        # The bonded atom info.
        index = matching_list[0]
        bonded_num = mol.atom_num[index]
        bonded_name = mol.atom_name[index]
        element = mol.element[index]
        pos = [mol.x[index], mol.y[index], mol.z[index]]
        attached_name = mol.atom_name[index]

        # Return the information.
        return bonded_num, bonded_name, element, pos, attached_name, None


    def _find_bonded_atoms(self, index, mol, radius=1.2):
        """Find all atoms within a sphere and say that they are attached to the central atom.

        The found atoms will be added to the 'bonded' data structure.


        @param index:           The index of the central atom.
        @type index:            int
        @param mol:             The molecule container.
        @type mol:              MolContainer instance
        """

        # Central atom info.
        centre = array([mol.x[index], mol.y[index], mol.z[index]], float64)

        # Atom loop.
        dist_list = []
        connect_list = {}
        element_list = {}
        for i in range(len(mol.atom_num)):
            # Skip proton to proton bonds!
            if mol.element[index] == 'H' and mol.element[i] == 'H':
                continue

            # The atom's position.
            pos = array([mol.x[i], mol.y[i], mol.z[i]], float64)

            # The distance from the centre.
            dist = linalg.norm(centre-pos)

            # The atom is within the radius.
            if dist < radius:
                # Store the distance.
                dist_list.append(dist)

                # Store the atom index.
                connect_list[dist] = i

                # Store the element type.
                element_list[dist] = mol.element[i]

        # The maximum number of allowed covalent bonds.
        max_conn = 1000   # Ridiculous default!
        if mol.element[index] == 'H':
            max_conn = 1
        elif mol.element[index] == 'O':
            max_conn = 2
        elif mol.element[index] == 'N':
            max_conn = 3
        elif mol.element[index] == 'C':
            max_conn = 4

        # Sort.
        dist_list.sort()

        # Loop over the max number of connections (or the number of connected atoms, if less).
        for i in range(min(max_conn, len(dist_list))):
            mol.atom_connect(index, connect_list[dist_list[i]])


    def _get_chemical_name(self, hetID):
        """Return the chemical name corresponding to the given residue ID.

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

        For any other residues, no description is returned.

        @param hetID:   The residue ID.
        @type hetID:    str
        @return:        The chemical name.
        @rtype:         str or None
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


    def _parse_models_gaussian(self, file_path, verbosity=1):
        """Generator function for looping over the models in the Gaussian log file.

        @param file_path:   The full path of the Gaussian log file.
        @type file_path:    str
        @return:            The model number and all the records for that model.
        @rtype:             tuple of int and array of str
        @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
        @type verbosity:    int
        """

        # Open the file.
        file = open_read_file(file_path, verbosity=verbosity)
        lines = file.readlines()
        file.close()

        # Check for empty files.
        if lines == []:
            raise RelaxError("The Gaussian log file is empty.")

        # Init.
        found = False
        str_index = 0
        total_atom = 0
        model = 0
        records = []

        # Loop over the data.
        for i in range(len(lines)):
            # Found a structure.
            if search("Standard orientation", lines[i]):
                found = True
                str_index = 0
                continue

            # End of the model.
            if found and str_index > 4 and search("---------", lines[i]):
                # Yield the info
                yield records

                # Reset.
                records = []
                found = False

            # Not a structure line.
            if not found:
                continue

            # Append the line as a record of the model.
            records.append(lines[i])

            # Increment the structure line index.
            str_index += 1


    def _parse_pdb_connectivity_annotation(self, lines):
        """Loop over and parse the PDB connectivity annotation records.

        These are the records identified in the U{PDB version 3.30 documentation<http://www.wwpdb.org/documentation/format33/sect6.html>}.


        @param lines:       The lines of the PDB file excluding the sections prior to the connectivity annotation section.
        @type lines:        list of str
        @return:            The remaining PDB lines with the connectivity annotation records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the connectivity annotation section.
        records = [
            'SSBOND',
            'LINK  ',
            'CISPEP'
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the connectivity annotation section.
            if lines[i][:6] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_coord(self, lines):
        """Generator function for looping over the models in the PDB file.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect9.html}.


        @param lines:       The lines of the coordinate section.
        @type lines:        list of str
        @return:            The model number and all the records for that model.
        @rtype:             tuple of int and array of str
        """

        # Init.
        model = None
        records = []

        # Loop over the data.
        for i in range(len(lines)):
            # A new model record.
            if lines[i][:5] == 'MODEL':
                try:
                    model = int(lines[i].split()[1])
                except:
                    raise RelaxError("The MODEL record " + repr(lines[i]) + " is corrupt, cannot read the PDB file.")

            # Skip all records prior to the first ATOM or HETATM record.
            if not (lines[i][:4] == 'ATOM' or lines[i][:6] == 'HETATM') and not len(records):
                continue

            # End of the model.
            if lines[i][:6] == 'ENDMDL':
                # Yield the info.
                yield model, records

                # Reset the records.
                records = []

                # Skip the rest of this loop.
                continue

            # Append the line as a record of the model.
            records.append(lines[i])

        # If records is not empty then there are no models, so yield the lot.
        if len(records):
            yield model, records


    def _parse_pdb_hetrogen(self, lines):
        """Loop over and parse the PDB hetrogen records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect4.html}.


        @param lines:       The lines of the PDB file excluding the sections prior to the hetrogen section.
        @type lines:        list of str
        @return:            The remaining PDB lines with the hetrogen records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the hetrogen section.
        records = [
            'HET   ',
            'FORMUL',
            'HETNAM',
            'HETSYN'
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the hetrogen section.
            if lines[i][:6] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_misc(self, lines):
        """Loop over and parse the PDB miscellaneous records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect7.html}.


        @param lines:       The lines of the PDB file excluding the sections prior to the miscellaneous section.
        @type lines:        list of str
        @return:            The remaining PDB lines with the miscellaneous records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the miscellaneous section.
        records = [
            'SITE  '
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the miscellaneous section.
            if lines[i][:6] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_prim_struct(self, lines):
        """Loop over and parse the PDB primary structure records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect3.html}.


        @param lines:       The lines of the PDB file excluding the title section.
        @type lines:        list of str
        @return:            The remaining PDB lines with the primary structure records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the primary structure section.
        records = [
            'DBREF ',
            'DBREF1',
            'DBREF2',
            'SEQADV',
            'SEQRES',
            'MODRES'
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the primary structure section.
            if lines[i][:6] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_ss(self, lines, read_mol=None):
        """Loop over and parse the PDB secondary structure records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect5.html}.


        @param lines:       The lines of the PDB file excluding the sections prior to the secondary structure section.
        @type lines:        list of str
        @keyword read_mol:  The molecule(s) to read from the file, independent of model.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If set to None, then all molecules will be loaded.
        @type read_mol:     None, int, or list of int
        @return:            The remaining PDB lines with the secondary structure records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the secondary structure section (the depreciated TURN record is also included to handle old PDB files).
        records = [
            'HELIX ',
            'SHEET ',
            'TURN  '
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the secondary structure section.
            if lines[i][:6] not in records:
                break

            # A helix.
            if lines[i][:5] == 'HELIX':
                # Parse the record.
                record_type, ser_num, helix_id, init_res_name, init_chain_id, init_seq_num, init_icode, end_res_name, end_chain_id, end_seq_num, end_icode, helix_class, comment, length = pdb_read.helix(lines[i])

                # Only load the desired molecule.
                if read_mol != None:
                    if self._pdb_chain_id_to_mol_index(init_chain_id)+1 not in read_mol:
                        continue
                    if self._pdb_chain_id_to_mol_index(end_chain_id)+1 not in read_mol:
                        continue

                # Store the data.
                if not hasattr(self, 'helices'):
                    self.helices = []
                self.helices.append([helix_id, init_chain_id, init_res_name, init_seq_num, end_chain_id, end_res_name, end_seq_num, helix_class, length])

            # A sheet.
            if lines[i][:5] == 'SHEET':
                # Parse the record.
                record_type, strand, sheet_id, num_strands, init_res_name, init_chain_id, init_seq_num, init_icode, end_res_name, end_chain_id, end_seq_num, end_icode, sense, cur_atom, cur_res_name, cur_chain_id, cur_res_seq, cur_icode, prev_atom, prev_res_name, prev_chain_id, prev_res_seq, prev_icode = pdb_read.sheet(lines[i])

                # Only load the desired molecule.
                if read_mol != None:
                    if self._pdb_chain_id_to_mol_index(init_chain_id)+1 not in read_mol:
                        continue
                    if self._pdb_chain_id_to_mol_index(end_chain_id)+1 not in read_mol:
                        continue

                # Store the data.
                if not hasattr(self, 'sheets'):
                    self.sheets = []
                self.sheets.append([strand, sheet_id, num_strands, init_res_name, init_chain_id, init_seq_num, init_icode, end_res_name, end_chain_id, end_seq_num, end_icode, sense, cur_atom, cur_res_name, cur_chain_id, cur_res_seq, cur_icode, prev_atom, prev_res_name, prev_chain_id, prev_res_seq, prev_icode])

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_title(self, lines):
        """Loop over and parse the PDB title records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect2.html}.


        @param lines:       All lines of the PDB file.
        @type lines:        list of str
        @return:            The remaining PDB lines with the title records stripped.
        @rtype:             list of str
        """

        # The ordered list of (sometimes truncated) record names in the title section.
        records = [
            'HEADER',
            'OBSLTE',
            'TITLE ',
            'SPLT  ',
            'CAVEAT',
            'COMPND',
            'SOURCE',
            'KEYWDS',
            'EXPDTA',
            'NUMMDL',
            'MDLTYP',
            'AUTHOR',
            'REVDAT',
            'SPRSDE',
            'JRNL  ',
            'REMARK'
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the title section.
            if lines[i][:6] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_pdb_transform(self, lines):
        """Loop over and parse the PDB transform records.

        These are the records identified in the PDB version 3.30 documentation at U{http://www.wwpdb.org/documentation/format33/sect8.html}.


        @param lines:       The lines of the PDB file excluding the sections prior to the transform section.
        @type lines:        list of str
        @return:            The remaining PDB lines with the transform records stripped.
        @rtype:             list of str
        """

        # The ordered list of record names in the transform section.
        records = [
            'CRYST',
            'MTRIX',
            'ORIGX',
            'SCALE',
        ]

        # Loop over the lines.
        for i in range(len(lines)):
            # No match, therefore assume to be out of the transform section.
            if lines[i][0: 5] not in records:
                break

        # Return the remaining lines.
        return lines[i:]


    def _parse_models_xyz(self, file_path, verbosity=1):
        """Generator function for looping over the models in the XYZ file.

        @param file_path:   The full path of the XYZ file.
        @type file_path:    str
        @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
        @type verbosity:    int
        @return:            The model number and all the records for that model.
        @rtype:             tuple of int and array of str
        """

        # Open the file.
        file = open_read_file(file_path, verbosity=verbosity)
        lines = file.readlines()
        file.close()

        # Check for empty files.
        if lines == []:
            raise RelaxError("The XYZ file is empty.")

        # Init.
        total_atom = 0
        model = 0
        records = []

        # Loop over the data.
        for i in range(len(lines)):
            num=0
            word = lines[i].split()
            # Find the total atom number and the first model.
            if (i==0) and (len(word)==1):
                try:
                    total_atom = int(word[0])
                    num = 1
                except:
                    raise RelaxError("The MODEL record " + repr(lines[i]) + " is corrupt, cannot read the XYZ file.")

            # End of the model.
            if (len(records) == total_atom):
              # Yield the info
              yield records

              # Reset the records.
              records = []

            # Skip all records prior to atom coordinates record.
            if (len(word) != 4):
                continue

            # Append the line as a record of the model.
            records.append(lines[i])

        # If records is not empty then there are no models, so yield the lot.
        if len(records):
            yield records


    def _parse_mols_pdb(self, records):
        """Generator function for looping over the molecules in the PDB records of a model.

        @param records:     The list of PDB records for the model, or if no models exist the entire PDB file.
        @type records:      list of str
        @return:            The molecule number and all the records for that molecule.
        @rtype:             tuple of int and list of str
        """

        # Check for empty records.
        if records == []:
            raise RelaxError("There are no PDB records for this model.")

        # Init.
        mol_count = 1
        mol_records = [[]]
        end = False

        # Loop over the data.
        for i in range(len(records)):
            # A PDB termination record.
            if records[i][:3] == 'END':
                break

            # A master record, so we are done.
            if records[i][:6] == 'MASTER':
                break

            # A model termination record.
            if records[i][:6] == 'ENDMDL':
                end = True

            # A molecule termination record with no trailing HETATM or CONECT.
            elif i < len(records)-1 and records[i][:3] == 'TER' and not records[i+1][:6] == 'HETATM' and not records[i+1][:6] == 'CONECT':
                end = True

            # A HETATM followed by an ATOM record.
            elif i < len(records)-1 and records[i][:6] == 'HETATM' and records[i+1][:4] == 'ATOM':
                end = True

            # End.
            if end:
                # Increment the molecule counter.
                mol_count = mol_count + 1

                # Reset the flag.
                end = False

                # Skip the rest of this loop.
                continue

            # The molecule number.
            chain_id = records[i][21]
            if chain_id == ' ':
                mol_index = mol_count - 1
            else:
                mol_index = self._pdb_chain_id_to_mol_index(chain_id)

            # Add a new records list as required.
            while True:
                if len(mol_records) <= mol_index:
                    mol_records.append([])
                else:
                    break

            # Append the line as a record of the molecule.
            mol_records[mol_index].append(records[i])

        # Loop over the molecules and yield the molecule number and records.
        for i in range(len(mol_records)):
            if mol_records[i] != []:
                yield i+1, mol_records[i]


    def _pdb_chain_id_to_mol_index(self, chain_id=None):
        """Convert the PDB chain ID into the molecule index in a regular way.

        @keyword chain_id:  The PDB chain ID string.
        @type chain_id:     str
        @return:            The corresponding molecule index.
        @rtype:             int
        """

        # Initialise.
        mol_index = 0

        # Convert to the molecule index.
        if chain_id:
            mol_index = CHAIN_ID_LIST.index(chain_id)

        # Return the index.
        return mol_index


    def _residue_data(self, res_nums=None, res_names=None):
        """Convert the residue info into a dictionary of unique residues with numbers as keys.

        @keyword res_nums:  The list of residue numbers.
        @type res_nums:     list of int
        @keyword res_names: The list of residue names matching the numbers.
        @type res_names:    list of str
        @return:            The dictionary of residue names with residue numbers as keys.
        @rtype:             dict of str
        """

        # Initialise.
        data = {}

        # Loop over the data.
        for i in range(len(res_nums)):
            # The residue data already exists.
            if res_nums[i] in data:
                continue

            # Add the data.
            data[res_nums[i]] = res_names[i]

        # Return the dictionary.
        return data


    def _validate_data_arrays(self, struct):
        """Check the validity of the data arrays in the given structure object.

        @param struct:  The structural object.
        @type struct:   Structure_container instance
        """

        # The number of atoms.
        num = len(struct.atom_name)

        # Check the other lengths.
        if len(struct.bonded) != num and len(struct.chain_id) != num and len(struct.element) != num and len(struct.pdb_record) != num and len(struct.res_name) != num and len(struct.res_num) != num and len(struct.seg_id) != num and len(struct.x) != num and len(struct.y) != num and len(struct.z) != num:
            raise RelaxError("The structural data is invalid.")


    def _validate_records(self, lines):
        """Make sure all PDB records are 80 char in length, padding with whitespace when needed.

        All newline characters are stripped from the records as well.


        @param lines:       All lines of the PDB file.
        @type lines:        list of str
        @return:            The padded PDB lines.
        @rtype:             list of str
        """

        # Loop over the lines.
        for i in range(len(lines)):
            # Strip the newline character.
            lines[i] = lines[i].rstrip('\r\n')

            # Pad if needed.
            if len(lines[i]) != 80:
                lines[i] = "%-80s" % lines[i]

        # Return the fixed lines.
        return lines


    def _mol_type(self, mol):
        """Determine the type of molecule.

        @param mol:     The molecule data container.
        @type mol:      MolContainer instance
        """

        # Amino acids.
        aa = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']

        # Set the molecule type to default to 'other'.
        mol.type = 'other'

        # Loop over the residues.
        for res in mol.res_name:
            # Protein.
            if res in aa:
                # Set the molecule type and return.
                mol.type = 'protein'
                return


    def _protein_connect(self, mol):
        """Set up the connectivities for the protein.

        @param mol:     The molecule data container.
        @type mol:      MolContainer instance
        """

        # Initialise some residue data.
        curr_res_num = None
        res_atoms = []

        # Loop over all atoms.
        for i in range(len(mol.atom_num)):
            # New residue.
            if mol.res_num[i] != curr_res_num:
                # Intra-residue connectivites.
                if len(res_atoms):
                    self._protein_intra_connect(mol, res_atoms)

                # Update the residue number.
                curr_res_num = mol.res_num[i]

                # Reset the residue atom index list.
                res_atoms = []

            # Add the atom index to the list.
            res_atoms.append(i)

            # Last atom.
            if i == len(mol.atom_num) - 1 and len(res_atoms):
                self._protein_intra_connect(mol, res_atoms)


    def _protein_intra_connect(self, mol, res_atoms):
        """Set up the connectivities for the protein.

        @param mol:         The molecule data container.
        @type mol:          MolContainer instance
        @param res_atoms:   The list of atom indices corresponding to the residue.
        @type res_atoms:    list of int
        """

        # Back bond connectivity.
        indices = {
            'N': None,
            'C': None,
            'O': None,
            'CA': None,
            'HN': None,
            'H': None,  # Same as HN.
            'HA': None
        }

        # Loop over all atoms to find the indices.
        for index in res_atoms:
            if mol.atom_name[index] in indices:
                indices[mol.atom_name[index]] = index

        # Connect the atom pairs.
        pairs = [
            ['N', 'HN'],
            ['N', 'H'],
            ['N', 'CA'],
            ['CA', 'HA'],
            ['CA', 'C'],
            ['C', 'O']
        ]

        # Loop over the atoms pairs and connect them.
        for pair in pairs:
            if indices[pair[0]] != None and indices[pair[1]] != None:
                mol.atom_connect(indices[pair[0]], indices[pair[1]])


    def _translate(self, data, format='str'):
        """Convert the data into a format for writing to file.

        @param data:        The data to convert to the required format.
        @type data:         anything
        @keyword format:    The format to convert to.  This can be 'str', 'float', or 'int'.
        @type format:       str
        @return:            The converted version of the data.
        @rtype:             str
        """

        # Conversion to string.
        if format == 'str':
            # None values.
            if data == None:
                data = ''

            # Force convert to string.
            if not isinstance(data, str):
                data = repr(data)

        # Conversion to float.
        if format == 'float':
            # None values.
            if data == None:
                data = 0.0

            # Force convert to float.
            if not isinstance(data, float):
                data = float(data)

         # Return the converted data.
        return data


    def _trim_helix(self, helix=None, trim_res_list=[], res_data=None):
        """Trim the given helix based on the list of deleted residue numbers.

        @keyword helix:         The single helix metadata structure.
        @type helix:            list
        @keyword trim_res_list: The list of residue numbers which no longer exist.
        @type trim_res_list:    list of int
        @keyword res_data:      The dictionary of residue names with residue numbers as keys.
        @type res_data:         dict of str
        @return:                The trimmed helix metadata structure, or None if the whole helix is to be deleted.
        @rtype:                 list or None
        """

        # Unpack the helix residue numbers.
        start_res = helix[3]
        end_res = helix[6]

        # The reverse residue list.
        trim_res_list_rev = deepcopy(trim_res_list)
        trim_res_list_rev.reverse()

        # The helix residues.
        helix_res = list(range(start_res, end_res+1))

        # Trim forwards.
        for res_num in trim_res_list:
            if res_num == start_res:
                # Remove the residue.
                helix_res.pop(0)

                # No helix left.
                if len(helix_res) == 0:
                    break

                # Realias the starting residue.
                start_res = helix_res[0]

        # No helix left.
        if len(helix_res) == 0:
            return None

        # Trim backwards.
        for res_num in trim_res_list_rev:
            if res_num == end_res:
                helix_res.pop(-1)
                end_res = helix_res[-1]

        # Replace the starting and ending residues.
        if start_res != helix[3]:
            helix[3] = start_res
            helix[2] = res_data[start_res]
        if end_res != helix[6]:
            helix[6] = end_res
            helix[5] = res_data[end_res]

        # The helix length.
        helix[-1] = len(helix_res)

        # Return the modified helix.
        return helix


    def _trim_sheet(self, sheet=None, trim_res_list=[], res_data=None):
        """Trim the given sheet based on the list of deleted residue numbers.

        @keyword sheet:         The single sheet metadata structure.
        @type sheet:            list
        @keyword trim_res_list: The list of residue numbers which no longer exist.
        @type trim_res_list:    list of int
        @keyword res_data:      The dictionary of residue names with residue numbers as keys.
        @type res_data:         dict of str
        @return:                The trimmed sheet metadata structure, or None if the whole sheet is to be deleted.
        @rtype:                 list or None
        """

        # Unpack the sheet residue numbers.
        start_res = sheet[5]
        end_res = sheet[9]

        # The reverse residue list.
        trim_res_list_rev = deepcopy(trim_res_list)
        trim_res_list_rev.reverse()

        # The sheet residues.
        sheet_res = list(range(start_res, end_res+1))

        # Trim forwards.
        for res_num in trim_res_list:
            if res_num == start_res:
                # Remove the residue.
                sheet_res.pop(0)

                # No sheet left.
                if len(sheet_res) == 0:
                    break

                # Realias the starting residue.
                start_res = sheet_res[0]

        # No sheet left.
        if len(sheet_res) == 0:
            return None

        # Trim backwards.
        for res_num in trim_res_list_rev:
            if res_num == end_res:
                sheet_res.pop(-1)
                end_res = sheet_res[-1]

        # Replace the starting and ending residues.
        if start_res != sheet[5]:
            sheet[5] = start_res
            sheet[3] = res_data[start_res]
        if end_res != sheet[9]:
            sheet[9] = end_res
            sheet[7] = res_data[end_res]

        # Return the modified sheet.
        return sheet


    def add_atom(self, mol_name=None, atom_name=None, res_name=None, res_num=None, pos=[None, None, None], element=None, atom_num=None, chain_id=None, segment_id=None, pdb_record=None):
        """Add a new atom to the structural data object.

        @keyword mol_name:      The name of the molecule.
        @type mol_name:         str
        @keyword atom_name:     The atom name, e.g. 'H1'.
        @type atom_name:        str or None
        @keyword res_name:      The residue name.
        @type res_name:         str or None
        @keyword res_num:       The residue number.
        @type res_num:          int or None
        @keyword pos:           The position vector of coordinates.  If a rank-2 array is supplied, the length of the first dimension must match the number of models.
        @type pos:              rank-1 or rank-2 array or list of float
        @keyword element:       The element symbol.
        @type element:          str or None
        @keyword atom_num:      The atom number.
        @type atom_num:         int or None
        @keyword chain_id:      The chain identifier.
        @type chain_id:         str or None
        @keyword segment_id:    The segment identifier.
        @type segment_id:       str or None
        @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM' or 'HETATM'.
        @type pdb_record:       str or None
        """

        # Add a model if not present.
        if len(self.structural_data) == 0:
            self.add_model()

        # Check the position.
        if is_float(pos[0]):
            if len(pos) != 3:
                raise RelaxError("The single atomic position %s must be a 3D list." % pos)
        else:
            if len(pos) != len(self.structural_data):
                raise RelaxError("The %s atomic positions does not match the %s models present." % (len(pos), len(self.structural_data)))

        # Loop over each model.
        for i in range(len(self.structural_data)):
            # Alias the model.
            model = self.structural_data[i]

            # Specific molecule.
            mol = self.get_molecule(mol_name, model=model.num)

            # Add the molecule, if it does not exist.
            if mol == None:
                self.add_molecule(name=mol_name)
                mol = self.get_molecule(mol_name, model=model.num)

            # Split up the position if needed.
            if is_float(pos[0]):
                model_pos = pos
            else:
                model_pos = pos[i]

            # Add the atom.
            mol.atom_add(atom_name=atom_name, res_name=res_name, res_num=res_num, pos=model_pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record)


    def add_model(self, model=None, coords_from=None):
        """Add a new model to the store.

        The new model will be constructed with the structural information from the other models currently present.  The coords_from argument allows the atomic positions to be taken from a certain model.  If this argument is not set, then the atomic positions from the first model will be used.

        @keyword model:         The number of the model to create.
        @type model:            int or None
        @keyword coords_from:   The model number to take the coordinates from.
        @type coords_from:      int or None
        @return:                The model container.
        @rtype:                 ModelContainer instance
        """

        # Check if the model currently exists.
        if model != None:
            for i in range(len(self.structural_data)):
                if model == self.structural_data[i].num:
                    raise RelaxError("The model '%s' already exists." % model)

        # Add a new model.
        model = self.structural_data.add_item(model_num=model)

        # The model to duplicate.
        if coords_from == None:
            model_from = self.structural_data[0]
        else:
            for i in range(len(self.structural_data)):
                if self.structural_data[i].num == coords_from:
                    model_from = self.structural_data[i]
                    break

        # Duplicate all data from the MolList object down.
        for mol_index in range(len(model_from.mol)):
            # Create a new molecule container.
            model.mol.add_item(mol_name=model_from.mol[mol_index].mol_name, mol_cont=MolContainer())
            mol = model.mol[mol_index]
            mol_from = model_from.mol[mol_index]

            # Loop over the atomic data.
            for i in range(len(mol_from.atom_num)):
                mol.atom_num.append(mol_from.atom_num[i])
                mol.atom_name.append(mol_from.atom_name[i])
                mol.bonded.append(mol_from.bonded[i])
                mol.chain_id.append(mol_from.chain_id[i])
                mol.element.append(mol_from.element[i])
                mol.pdb_record.append(mol_from.pdb_record[i])
                mol.res_name.append(mol_from.res_name[i])
                mol.res_num.append(mol_from.res_num[i])
                mol.seg_id.append(mol_from.seg_id[i])
                mol.x.append(mol_from.x[i])
                mol.y.append(mol_from.y[i])
                mol.z.append(mol_from.z[i])

        # Return the model.
        return self.structural_data[-1]


    def add_molecule(self, model_num=None, name=None):
        """Add a new molecule to the store.

        @keyword model_num: The optional model to add the molecule to.  If not supplied, the molecule will be added to all models.
        @type model_num:    None or int
        @keyword name:      The molecule identifier string.
        @type name:         str
        """

        # Add a model if necessary.
        if len(self.structural_data) == 0:
            self.add_model()

        # Add the molecule to each model.
        for model in self.model_loop(model=model_num):
            model.mol.add_item(mol_name=name, mol_cont=MolContainer())


    def are_bonded(self, atom_id1=None, atom_id2=None):
        """Determine if two atoms are directly bonded to each other.

        @keyword atom_id1:  The molecule, residue, and atom identifier string of the first atom.
        @type atom_id1:     str
        @keyword atom_id2:  The molecule, residue, and atom identifier string of the second atom.
        @type atom_id2:     str
        @return:            True if the atoms are directly bonded.
        @rtype:             bool
        """

        # Generate the selection objects.
        sel_obj1 = Selection(atom_id1)
        sel_obj2 = Selection(atom_id2)

        # Build the connectivities if needed.
        for mol in self.structural_data[0].mol:
            for i in range(len(mol.atom_num)):
                if not len(mol.bonded[i]):
                    self._find_bonded_atoms(i, mol, radius=2)

        # Loop over the molecules.
        for mol in self.structural_data[0].mol:
            # Skip non-matching molecules.
            if not sel_obj1.contains_mol(mol.mol_name):
                continue
            if not sel_obj2.contains_mol(mol.mol_name):
                continue

            # Find the first atom.
            index1 = None
            index2 = None
            for i in range(len(mol.atom_num)):
                # Matching first atom.
                if index1 == None and sel_obj1.contains_spin(mol.atom_num[i], mol.atom_name[i], mol.res_num[i], mol.res_name[i], mol.mol_name):
                    index1 = i

                # Matching second atom.
                if index2 == None and sel_obj2.contains_spin(mol.atom_num[i], mol.atom_name[i], mol.res_num[i], mol.res_name[i], mol.mol_name):
                    index2 = i

                # Nothing left to do.
                if index1 != None and index2 != None:
                    break

            # Connectivities exist.
            if index1 < len(mol.bonded):
                if index2 in mol.bonded[index1]:
                    return True
                else:
                    return False


    def are_bonded_index(self, mol_index1=None, atom_index1=None, mol_index2=None, atom_index2=None):
        """Determine if two atoms, given as indices, are directly bonded to each other.

        @keyword mol_index1:    The molecule index of the first atom.
        @type mol_index1:       int
        @keyword atom_index1:   The index of the first atom.
        @type atom_index1:      int
        @keyword mol_index2:    The molecule index of the second atom.
        @type mol_index2:       int
        @keyword atom_index2:   The index of the second atom.
        @type atom_index2:      int
        @return:                True if the atoms are directly bonded.
        @rtype:                 bool
        """

        # Alias the molecule.
        mol1 = self.structural_data[0].mol[mol_index1]
        mol2 = self.structural_data[0].mol[mol_index2]

        # Build the connectivities if needed.
        if not len(mol1.bonded[atom_index1]):
            self._find_bonded_atoms(atom_index1, mol1, radius=2)
        if not len(mol2.bonded[atom_index2]):
            self._find_bonded_atoms(atom_index2, mol2, radius=2)

        # Is the second atom in the bonded list of the first?
        if atom_index2 in mol1.bonded[atom_index1]:
            return True

        # No!
        return False


    def atom_loop(self, selection=None, str_id=None, model_num=None, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False, mol_index_flag=False, index_flag=False, ave=False):
        """Generator function for looping over all atoms in the internal relax structural object.

        This method should be designed as a U{generator<http://www.python.org/dev/peps/pep-0255/>}.  It should loop over all atoms of the system yielding the following atomic information, if the corresponding flag is True, in tuple form:

            1.  Model number.
            2.  Molecule name.
            3.  Residue number.
            4.  Residue name.
            5.  Atom number.
            6.  Atom name.
            7.  The element name (its atomic symbol and optionally the isotope, e.g. 'N', 'Mg', '17O', '13C', etc).
            8.  The position of the atom in Euclidean space.


        @keyword selection:         The internal structural selection object.  This is obtained by calling the selection() method with the atom ID string.
        @type selection:            lib.structure.internal.Internal_selection instance
        @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.  If None, then all structures will be looped over.
        @type str_id:               str, int, or None
        @keyword model_num:         Only loop over a specific model.
        @type model_num:            int or None
        @keyword mol_name_flag:     A flag which if True will cause the molecule name to be yielded.
        @type mol_name_flag:        bool
        @keyword res_num_flag:      A flag which if True will cause the residue number to be yielded.
        @type res_num_flag:         bool
        @keyword res_name_flag:     A flag which if True will cause the residue name to be yielded.
        @type res_name_flag:        bool
        @keyword atom_num_flag:     A flag which if True will cause the atom number to be yielded.
        @type atom_num_flag:        bool
        @keyword atom_name_flag:    A flag which if True will cause the atom name to be yielded.
        @type atom_name_flag:       bool
        @keyword element_flag:      A flag which if True will cause the element name to be yielded.
        @type element_flag:         bool
        @keyword pos_flag:          A flag which if True will cause the atomic position to be yielded.
        @type pos_flag:             bool
        @keyword mol_index_flag:    A flag which if True will cause the molecule index to be yielded.
        @type mol_index_flag:       bool
        @keyword index_flag:        A flag which if True will cause the atomic index to be yielded.
        @type index_flag:           bool
        @keyword ave:               A flag which if True will result in this method returning the average atom properties across all loaded structures.
        @type ave:                  bool
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number (int), residue name (str), atom number (int), atom name(str), element name (str), and atomic position (array of len 3).
        """

        # Check that the structure is loaded.
        if not len(self.structural_data):
            raise RelaxNoPdbError

        # Obtain all data from the first model (except the position data).
        model = self.structural_data[0]

        # Loop over all molecules and atoms in the selection.
        for mol_index, i in selection.loop():
            mol = model.mol[mol_index]

            # Initialise.
            res_num = mol.res_num[i]
            res_name = mol.res_name[i]
            atom_num = mol.atom_num[i]
            atom_name = mol.atom_name[i]
            element = mol.element[i]

            # The atom position.
            if pos_flag:
                # Average the position.
                if ave:
                    # Initialise.
                    pos = zeros(3, float64)

                    # Loop over the models.
                    for model in self.model_loop(model=model_num):
                        # Alias.
                        mol2 = model.mol[mol_index]

                        # Some sanity checks.
                        if mol2.atom_num[i] != atom_num:
                            raise RelaxError("The loaded structures do not contain the same atoms.  The average structural properties can not be calculated.")

                        # Sum the atom positions.
                        pos = pos + array([mol2.x[i], mol2.y[i], mol2.z[i]], float64)

                    # Average the position array (divide by the number of models).
                    pos = pos / len(self.structural_data)

                # All positions.
                else:
                    # Initialise.
                    pos = []

                    # Loop over the models.
                    for model in self.model_loop(model=model_num):
                        # Alias.
                        mol2 = model.mol[mol_index]

                        # Append the position.
                        pos.append([mol2.x[i], mol2.y[i], mol2.z[i]])

                    # Convert.
                    pos = array(pos, float64)

            # The molecule name.
            mol_name = mol.mol_name

            # Build the tuple to be yielded.
            atomic_tuple = ()
            if mol_name_flag:
                atomic_tuple = atomic_tuple + (mol_name,)
            if res_num_flag:
                atomic_tuple = atomic_tuple + (res_num,)
            if res_name_flag:
                atomic_tuple = atomic_tuple + (res_name,)
            if atom_num_flag:
                atomic_tuple = atomic_tuple + (atom_num,)
            if atom_name_flag:
                atomic_tuple = atomic_tuple + (atom_name,)
            if element_flag:
                atomic_tuple = atomic_tuple + (element,)
            if pos_flag:
                atomic_tuple = atomic_tuple + (pos,)
            if mol_index_flag:
                atomic_tuple += (mol_index,)
            if index_flag:
                atomic_tuple += (i,)

            # Yield the information.
            if len(atomic_tuple) == 1:
                atomic_tuple = atomic_tuple[0]
            yield atomic_tuple


    def bond_vectors(self, attached_atom=None, model_num=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None, return_name=False, return_warnings=False):
        """Find the bond vector between the atoms of 'attached_atom' and 'atom_id'.

        @keyword attached_atom:     The name of the bonded atom.
        @type attached_atom:        str
        @keyword model_num:         The model of which to return the vectors from.  If not supplied and multiple models exist, then vectors from all models will be returned.
        @type model_num:            None or int
        @keyword mol_name:          The name of the molecule that attached_atom belongs to.
        @type mol_name:             str
        @keyword res_num:           The number of the residue that attached_atom belongs to.
        @type res_num:              str
        @keyword res_name:          The name of the residue that attached_atom belongs to.
        @type res_name:             str
        @keyword spin_num:          The number of the spin that attached_atom is attached to.
        @type spin_num:             str
        @keyword spin_name:         The name of the spin that attached_atom is attached to.
        @type spin_name:            str
        @keyword return_name:       A flag which if True will cause the name of the attached atom to be returned together with the bond vectors.
        @type return_name:          bool
        @keyword return_warnings:   A flag which if True will cause warning messages to be returned.
        @type return_warnings:      bool
        @return:                    The list of bond vectors for each model.
        @rtype:                     list of numpy arrays (or a tuple if return_name or return_warnings are set)
        """

        # Initialise some objects.
        vectors = []
        attached_name = None
        warnings = None

        # Use the first model for the atom matching.
        model = self.structural_data[0]

        # Loop over the molecules.
        for mol_index in range(len(model.mol)):
            # Alias.
            mol = model.mol[mol_index]

            # Skip non-matching molecules.
            if mol_name and mol_name != mol.mol_name:
                continue

            # Find the atomic index of the base atom.
            index = None
            for i in range(len(mol.atom_name)):
                # Residues don't match.
                if (res_num != None and mol.res_num[i] != res_num) or (res_name != None and mol.res_name[i] != res_name):
                    continue

                # Atoms don't match.
                if (spin_num != None and mol.atom_num[i] != spin_num) or (spin_name != None and mol.atom_name[i] != spin_name):
                    continue

                # Update the index and stop searching.
                index = i
                break

            # Found the atom.
            if index != None:
                # Loop over the models.
                for model in self.model_loop(model=model_num):
                    # Alias.
                    mol = model.mol[mol_index]

                    # Get the atom bonded to this model/molecule/residue/atom.
                    bonded_num, bonded_name, element, pos, attached_name, warnings = self._bonded_atom(attached_atom, index, mol)

                    # No bonded atom.
                    if (bonded_num, bonded_name, element) == (None, None, None):
                        continue

                    # The bond vector.
                    vector = array(pos, float64) - array([mol.x[index], mol.y[index], mol.z[index]], float64)

                    # Append the vector to the vectors array.
                    vectors.append(vector)

            # Not found.
            else:
                warnings = "Cannot find the atom in the structure"

        # Build the tuple to be yielded.
        data = (vectors,)
        if return_name:
            data = data + (attached_name,)
        if return_warnings:
            data = data + (warnings,)

        # Return the data.
        return data


    def collapse_ensemble(self, model_num=None, model_to=1):
        """Collapse the ensemble into a single model.

        @keyword model_num: The number of the model to keep.  All other models will be removed.
        @type model_num:    int
        @keyword model_to:  The model number for the sole remaining model.
        @type model_to:     int
        """

        # Store all the model numbers.
        models = []
        for model_cont in self.model_loop():
            if model_cont.num != model_num:
                models.append(model_cont.num)

        # Delete all models.
        for model in models:
            self.delete(model)

        # Renumber the remaining model.
        self.set_model(model_orig=model_num, model_new=model_to)


    def connect_atom(self, mol_name=None, index1=None, index2=None):
        """Connect two atoms in the structural data object.

        @keyword mol_name:  The name of the molecule.
        @type mol_name:     str
        @keyword index1:    The global index of the first atom.
        @type index1:       str
        @keyword index2:    The global index of the first atom.
        @type index2:       str
        """

        # Add the molecule, if it does not exist.
        if self.get_molecule(mol_name) == None:
            self.add_molecule(name=mol_name)

        # Loop over each model.
        for model in self.structural_data:
            # Specific molecule.
            mol = self.get_molecule(mol_name)

            # Add the atom.
            mol.atom_connect(index1=index1, index2=index2)


    def delete(self, model=None, selection=None, verbosity=1):
        """Deletion of structural information.

        @keyword model:     Individual structural models from a loaded ensemble can be deleted by specifying the model number.
        @type model:        None or int
        @keyword selection: The internal structural selection object.  This is obtained by calling the selection() method with the atom ID string.
        @type selection:    lib.structure.internal.Internal_selection instance
        @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
        @type verbosity:    int
        """

        # All data.
        if model == None and selection == None:
            # Printout.
            if verbosity:
                print("Deleting the following structural data:\n")
                print(self.structural_data)

            # Delete the structural data.
            del self.structural_data

            # Initialise the empty model list.
            self.structural_data = ModelList()

        # Delete a whole model.
        elif selection == None:
            self.structural_data.delete_model(model_num=model)

        # Atom subset deletion.
        else:
            # Loop over the atoms and find the indices of the atoms to delete.
            indices = {}
            for mol_index, i in selection.loop():
                if mol_index not in indices:
                    indices[mol_index] = []
                indices[mol_index].append(i)
            for mol_index in indices:
                indices[mol_index].reverse()

            # Loop over the models.
            del_res_nums = []
            for model_cont in self.model_loop():
                # Skip models.
                if model != None and model_cont.num == model:
                    continue

                # Loop over the molecules.
                for mol_index in indices:
                    mol = model_cont.mol[mol_index]

                    # Generate a residue data dictionary for the metadata trimming (prior to atom deletion).
                    res_data = self._residue_data(res_nums=mol.res_num, res_names=mol.res_name)

                    # Loop over the reverse indices and pop out the data.
                    for i in indices[mol_index]:
                        mol.atom_num.pop(i)
                        mol.atom_name.pop(i)
                        mol.bonded.pop(i)
                        mol.chain_id.pop(i)
                        mol.element.pop(i)
                        mol.pdb_record.pop(i)
                        mol.res_name.pop(i)
                        res_num = mol.res_num.pop(i)
                        mol.seg_id.pop(i)
                        mol.x.pop(i)
                        mol.y.pop(i)
                        mol.z.pop(i)

                        # The residue no longer exists.
                        if res_num not in mol.res_num and res_num not in del_res_nums:
                            del_res_nums.append(res_num)

                        # Second atom of the bonded pair.
                        for j in range(len(mol.bonded)):
                            if i in mol.bonded[j]:
                                mol.bonded[j].pop(mol.bonded[j].index(i))

                        # Update the bonded lists, as the indices need to be shifted.
                        for j in range(i, len(mol.bonded)):
                            for k in range(len(mol.bonded[j])):
                                mol.bonded[j][k] -= 1

                    # Reset the metadata if nothing remains.
                    if mol.atom_num == []:
                        if hasattr(mol, 'file_name'):
                            del mol.file_name
                        if hasattr(mol, 'file_path'):
                            del mol.file_path
                        if hasattr(mol, 'file_mol_num'):
                            del mol.file_mol_num
                        if hasattr(mol, 'file_model'):
                            del mol.file_model

            # Nothing more to do.
            if not len(del_res_nums):
                return
            if model != None and len(self.structural_data) > 1:
                return

            # Fix the deleted residue number order.
            del_res_nums.reverse()

            # Handle the helix metadata.
            if hasattr(self, 'helices'):
                del_helix_indices = []
                for i in range(len(self.helices)):
                    # Trim the helix.
                    helix = self._trim_helix(helix=self.helices[i], trim_res_list=del_res_nums, res_data=res_data)

                    # Trimmed helix.
                    if helix != None:
                        self.helices[i] = helix

                    # No helix left.
                    else:
                        del_helix_indices.append(i)

                # Loop over the reverse helix indices and pop out the data.
                del_helix_indices.reverse()
                for i in del_helix_indices:
                    self.helices.pop(i)

            # Handle the sheet metadata.
            if hasattr(self, 'sheets'):
                del_sheet_indices = []
                for i in range(len(self.sheets)):
                    # Trim the sheet.
                    sheet = self._trim_sheet(sheet=self.sheets[i], trim_res_list=del_res_nums, res_data=res_data)

                    # Trimmed sheet.
                    if sheet != None:
                        self.sheets[i] = sheet

                    # No sheet left.
                    else:
                        del_sheet_indices.append(i)

                # Loop over the reverse sheet indices and pop out the data.
                del_sheet_indices.reverse()
                for i in del_sheet_indices:
                    self.sheets.pop(i)


    def empty(self):
        """Report if the structural data structure is empty or not.

        @return:    True if empty, False otherwise.
        @rtype:     bool
        """

        # Check the ModelList structure.
        if len(self.structural_data) == 0:
            return True
        else:
            return False


    def from_xml(self, str_node, dir=None, file_version=1):
        """Recreate the structural object from the XML structural object node.

        @param str_node:        The structural object XML node.
        @type str_node:         xml.dom.minicompat.Element instance
        @keyword dir:           The name of the directory containing the results file.
        @type dir:              str
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Recreate all base objects (i.e. metadata).
        xml_to_object(str_node, self, file_version=file_version, blacklist=['model', 'displacements'])

        # Recreate the model / molecule data structure.
        model_nodes = str_node.getElementsByTagName('model')
        self.structural_data.from_xml(model_nodes, file_version=file_version)

        # The displacement structure.
        disp_nodes = str_node.getElementsByTagName('displacements')
        if len(disp_nodes):
            # Initialise the object.
            self.displacements = Displacements()

            # Recreate the molecule data structures for the current model.
            self.displacements.from_xml(disp_nodes[0], file_version=file_version)


    def get_model(self, model):
        """Return or create the model.

        @param model:   The model number.
        @type model:    int or None
        @return:        The ModelContainer corresponding to the model number or that newly created.
        @rtype:         ModelContainer instance
        """

        # Check if the target is a single model.
        if model == None and self.num_models() > 1:
            raise RelaxError("The target model cannot be determined as there are %s models already present." % self.num_modes())

        # No model specified.
        if model == None:
            # Create the first model, if necessary.
            if self.num_models():
                self.structural_data.add_item()

            # Alias the first model.
            model_cont = self.structural_data[0]

        # The model has been specified.
        else:
            # Get the preexisting model.
            found = False
            for model_cont in self.structural_data:
                if model_cont.num == model:
                    found = True
                    break

            # Add the model if it doesn't exist.
            if not found:
                self.structural_data.add_item(model)
                model_cont = self.structural_data[-1]

        # Return the container.
        return model_cont


    def get_molecule(self, molecule, model=None):
        """Return the molecule.

        Only one model can be specified.


        @param molecule:    The molecule name.
        @type molecule:     int or None
        @keyword model:     The model number.
        @type model:        int or None
        @raises RelaxError: If the model is not specified and there is more than one model loaded.
        @return:            The MolContainer corresponding to the molecule name and model number.
        @rtype:             MolContainer instance or None
        """

        # Check if the target is a single molecule.
        if model == None and self.num_models() > 1:
            raise RelaxError("The target molecule cannot be determined as there are %s models already present." % self.num_models())

        # Check the model argument.
        if not isinstance(model, int) and not model == None:
            raise RelaxNoneIntError

        # No models.
        if not len(self.structural_data):
            return

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over the molecules.
            for mol in model_cont.mol:
                # Return the matching molecule.
                if mol.mol_name == molecule:
                    return mol


    def has_molecule(self, model_num=None, name=None):
        """Check if the molecule name exists.

        @keyword model_num: The optional model to check.  If not supplied, the molecule will be searched for across all models.
        @type model_num:    None or int
        @param name:        The molecule name.
        @type name:         str
        @return:            True if the molecule exists, False otherwise.
        @rtype:             bool
        """

        # No models.
        if not len(self.structural_data):
            return False

        # Loop over the models.
        for model_cont in self.model_loop(model=model_num):
            # Loop over the molecules.
            for mol in model_cont.mol:
                # Matching molecule.
                if mol.mol_name == name:
                    return True

        # No match.
        return False


    def load_gaussian(self, file_path, set_mol_name=None, set_model_num=None, verbosity=False):
        """Method for loading structures from a Gaussian log file.

        @param file_path:       The full path of the Gaussian log file.
        @type file_path:        str
        @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
        @type set_mol_name:     None, str, or list of str
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the Gaussian log model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @return:                The status of the loading of the Gaussian log file.
        @rtype:                 bool
        """

        # Initial printout.
        if verbosity:
            print("\nInternal relax Gaussian log parser.")

        # Test if the file exists.
        if not access(file_path, F_OK):
            # Exit indicating failure.
            return False

        # Separate the file name and path.
        path, file_name = os.path.split(file_path)

        # The absolute path.
        path_abs = abspath(curdir) + sep + path

        # Set up the molecule name data structure.
        if set_mol_name:
            if not isinstance(set_mol_name, list):
                set_mol_name = [set_mol_name]
        else:
            set_mol_name = [file_root(file_name) + '_mol1']

        # Set up the model number data structure.
        if set_model_num:
            if not isinstance(set_model_num, list):
                set_model_num = [set_model_num]
        else:
            set_model_num = [1]

        # Loop over all models in the Gaussian log file, doing nothing so the last model records are stored.
        for model_records in self._parse_models_gaussian(file_path, verbosity=verbosity):
            pass

        # Generate the molecule container.
        mol = MolContainer()

        # Fill the molecular data object.
        mol.fill_object_from_gaussian(model_records)

        # Create the structural data data structures.
        self.pack_structs([[mol]], orig_model_num=[1], set_model_num=set_model_num, orig_mol_num=[0], set_mol_name=set_mol_name, file_name=file_name, file_path=path, file_path_abs=path_abs, verbosity=verbosity)

        # Loading worked.
        return True


    def load_pdb(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, alt_loc=None, verbosity=False, merge=False):
        """Method for loading structures from a PDB file.

        @param file_path:       The full path of the PDB file.
        @type file_path:        str
        @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If set to None, then all molecules will be loaded.
        @type read_mol:         None, int, or list of int
        @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
        @type set_mol_name:     None, str, or list of str
        @keyword read_model:    The PDB model to extract from the file.  If set to None, then all models will be loaded.
        @type read_model:       None, int, or list of int
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the PDB model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword alt_loc:       The PDB ATOM record 'Alternate location indicator' field value to select which coordinates to use.
        @type alt_loc:          str or None
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @keyword merge:         A flag which if set to True will try to merge the PDB structure into the currently loaded structures.
        @type merge:            bool
        @return:                The status of the loading of the PDB file.
        @rtype:                 bool
        """

        # Initial printout.
        if verbosity:
            print("\nInternal relax PDB parser.")

        # Test if the file exists.
        if not access(file_path, F_OK):
            # Exit indicating failure.
            return False

        # Separate the file name and path.
        path, file = os.path.split(file_path)

        # The absolute path.
        path_abs = abspath(curdir) + sep + path

        # Convert the structure reading args into lists.
        if read_mol and not isinstance(read_mol, list):
            read_mol = [read_mol]
        if set_mol_name and not isinstance(set_mol_name, list):
            set_mol_name = [set_mol_name]
        if read_model and not isinstance(read_model, list):
            read_model = [read_model]
        if set_model_num and not isinstance(set_model_num, list):
            set_model_num = [set_model_num]

        # Open the PDB file.
        pdb_file = open_read_file(file_path, verbosity=verbosity)
        pdb_lines = pdb_file.readlines()
        pdb_file.close()

        # Check for empty files.
        if pdb_lines == []:
            raise RelaxError("The PDB file is empty.")

        # Pre-process the lines, fixing PDB violations.
        pdb_lines = self._validate_records(pdb_lines)

        # Process the different sections.
        pdb_lines = self._parse_pdb_title(pdb_lines)
        pdb_lines = self._parse_pdb_prim_struct(pdb_lines)
        pdb_lines = self._parse_pdb_hetrogen(pdb_lines)
        pdb_lines = self._parse_pdb_ss(pdb_lines, read_mol=read_mol)
        pdb_lines = self._parse_pdb_connectivity_annotation(pdb_lines)
        pdb_lines = self._parse_pdb_misc(pdb_lines)
        pdb_lines = self._parse_pdb_transform(pdb_lines)

        # Loop over all models in the PDB file.
        model_index = 0
        orig_model_num = []
        mol_conts = []
        for model_num, model_records in self._parse_pdb_coord(pdb_lines):
            # Only load the desired model.
            if read_model and model_num not in read_model:
                continue

            # Store the original model number.
            orig_model_num.append(model_num)

            # Loop over the molecules of the model.
            mol_conts.append([])
            mol_index = 0
            orig_mol_num = []
            new_mol_name = []
            for mol_num, mol_records in self._parse_mols_pdb(model_records):
                # Only load the desired model.
                if read_mol and mol_num not in read_mol:
                    continue

                # Set the target molecule name.
                if set_mol_name:
                    new_mol_name.append(set_mol_name[mol_index])
                else:
                    # Number of structures already present for the model.
                    num_struct = 0
                    if self.structural_data != None and len(self.structural_data) and (not set_model_num or (model_index <= len(set_model_num) and set_model_num[model_index] == self.structural_data[0].num)):
                        num_struct = len(self.structural_data[0].mol)

                    # Set the name to the file name plus the structure number.
                    new_mol_name.append(file_root(file) + '_mol' + repr(mol_num+num_struct))

                # Store the original mol number.
                orig_mol_num.append(mol_num)

                # Generate the molecule container.
                mol = MolContainer()

                # Fill the molecular data object.
                mol.fill_object_from_pdb(mol_records, alt_loc_select=alt_loc)

                # Store the molecule container.
                mol_conts[model_index].append(mol)

                # Increment the molecule index.
                mol_index = mol_index + 1

            # Increment the model index.
            model_index = model_index + 1

        # No data, so throw a warning and exit.
        if not len(mol_conts):
            warn(RelaxWarning("No structural data could be read from the file '%s'." % file_path))
            return False

        # Create the structural data data structures.
        self.pack_structs(mol_conts, orig_model_num=orig_model_num, set_model_num=set_model_num, orig_mol_num=orig_mol_num, set_mol_name=new_mol_name, file_name=file, file_path=path, file_path_abs=path_abs, merge=merge, verbosity=verbosity)

        # Loading worked.
        return True


    def load_xyz(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=False):
        """Method for loading structures from a XYZ file.

        @param file_path:       The full path of the XYZ file.
        @type file_path:        str
        @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If set to None, then all molecules will be loaded.
        @type read_mol:         None, int, or list of int
        @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None, then the molecules will be automatically labelled based on the file name or other information.
        @type set_mol_name:     None, str, or list of str
        @keyword read_model:    The XYZ model to extract from the file.  If set to None, then all models will be loaded.
        @type read_model:       None, int, or list of int
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then the XYZ model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @return:                The status of the loading of the XYZ file.
        @rtype:                 bool
        """

        # Initial printout.
        if verbosity:
            print("\nInternal relax XYZ parser.")

        # Test if the file exists.
        if not access(file_path, F_OK):
            # Exit indicating failure.
            return False

        # Separate the file name and path.
        path, file = os.path.split(file_path)

        # The absolute path.
        path_abs = abspath(curdir) + sep + path

        # Convert the structure reading args into lists.
        if read_mol and not isinstance(read_mol, list):
            read_mol = [read_mol]
        if set_mol_name and not isinstance(set_mol_name, list):
            set_mol_name = [set_mol_name]
        if read_model and not isinstance(read_model, list):
            read_model = [read_model]
        if set_model_num and not isinstance(set_model_num, list):
            set_model_num = [set_model_num]

        # Loop over all models in the XYZ file.
        mol_index = 0
        model_index = 0
        xyz_model_increment = 0
        orig_model_num = []
        mol_conts = []
        orig_mol_num = []
        new_mol_name = []
        for model_records in self._parse_models_xyz(file_path, verbosity=verbosity):
            # Increment the xyz_model_increment
            xyz_model_increment = xyz_model_increment +1

            # Only load the desired model.
            if read_model and xyz_model_increment not in read_model:
                continue

            # Store the original model number.
            orig_model_num.append(model_index)

            # Loop over the molecules of the model.
            if read_mol and mol_index not in read_mol:
                continue

            # Set the target molecule name.
            if set_mol_name:
                new_mol_name.append(set_mol_name[mol_index])
            else:
                if mol_index == 0:
                   #Set the name to the file name plus the structure number.
                   new_mol_name.append(file_root(file) + '_mol' + repr(mol_index+1))

            # Store the original mol number.
            orig_mol_num.append(mol_index)

            # Generate the molecule container.
            mol = MolContainer()

            # Fill the molecular data object.
            mol.fill_object_from_xyz(model_records)

            # Store the molecule container.
            mol_conts.append([])
            mol_conts[model_index].append(mol)

            # Increment the molecule index.
            mol_index = mol_index + 1

            # Increment the model index.
            model_index = model_index + 1

        # Create the structural data data structures.
        orig_mol_num = [0]
        self.pack_structs(mol_conts, orig_model_num=orig_model_num, set_model_num=set_model_num, orig_mol_num=orig_mol_num, set_mol_name=new_mol_name, file_name=file, file_path=path, file_path_abs=path_abs, verbosity=verbosity)

        # Loading worked.
        return True


    def mean(self):
        """Calculate the mean structure from all models in the structural data object."""

        # Create a new model for the mean structure.
        num = self.num_models()
        self.add_model()
        mean_model = self.structural_data[-1]

        # The selection object.
        selection = self.selection()

        # Loop over the molecules and atoms.
        for mol_index, i in selection.loop():
            # Set the mean structure coordinate to zero.
            mean_model.mol[mol_index].x[i] = 0.0
            mean_model.mol[mol_index].y[i] = 0.0
            mean_model.mol[mol_index].z[i] = 0.0

            # Loop over the models and sum the coordinates.
            for model_index in range(num):
                model_cont = self.structural_data[model_index]
                mean_model.mol[mol_index].x[i] += model_cont.mol[mol_index].x[i]
                mean_model.mol[mol_index].y[i] += model_cont.mol[mol_index].y[i]
                mean_model.mol[mol_index].z[i] += model_cont.mol[mol_index].z[i]

            # Averages.
            mean_model.mol[mol_index].x[i] /= num
            mean_model.mol[mol_index].y[i] /= num
            mean_model.mol[mol_index].z[i] /= num

        # Delete all models but the mean.
        for model_index in reversed(list(range(num))):
            self.delete(model=self.structural_data[model_index].num)


    def model_list(self):
        """Create a list of all models.

        @return:    The list of all models.
        @rtype:     list of int
        """

        # Assemble the list.
        models = []
        for model in self.model_loop():
            models.append(model.num)

        # Return the list.
        return models


    def model_loop(self, model=None):
        """Generator method for looping over the models in numerical order.

        @keyword model: Limit the loop to a single number.
        @type model:    int
        @return:        The model structural object.
        @rtype:         ModelContainer container
        """

        # A single model.
        if model:
            for i in range(len(self.structural_data)):
                if self.structural_data[i].num == model:
                    yield self.structural_data[i]

        # All models.
        else:
            # The models.
            model_nums = []
            for i in range(len(self.structural_data)):
                if self.structural_data[i].num != None:
                    model_nums.append(self.structural_data[i].num)

            # Sort.
            if model_nums:
                model_nums.sort()

            # Loop over the models in order.
            for model_num in model_nums:
                # Find the model.
                for i in range(len(self.structural_data)):
                    # Yield the model.
                    if self.structural_data[i].num == model_num:
                        yield self.structural_data[i]

            # No models, so just yield the single container.
            if not model_nums:
                yield self.structural_data[0]


    def num_models(self):
        """Method for returning the number of models.

        @return:    The number of models in the structural object.
        @rtype:     int
        """

        return len(self.structural_data)


    def num_molecules(self):
        """Method for returning the number of molecules.

        @return:    The number of molecules in the structural object.
        @rtype:     int
        """

        # No data.
        if self.empty():
            return 0

        # Validate the structural object.
        self.validate()

        # Return the number.
        return len(self.structural_data[0].mol)


    def one_letter_codes(self, mol_name=None):
        """Generate and return the one letter code sequence for the given molecule.

        @keyword mol_name:  The name of the molecule to return the one letter codes for.
        @type mol_name:     str
        @return:            The one letter code sequence for the given molecule.
        @rtype:             str
        """

        # Initialise.
        codes = ''

        # Use the first model.
        model = self.structural_data[0]

        # Loop over the molecules.
        for mol_index in range(len(model.mol)):
            # Alias.
            mol = model.mol[mol_index]

            # Skip non-matching molecules.
            if mol_name and mol_name != mol.mol_name:
                continue

            # Loop over the residues.
            for res_name, res_num in mol.loop_residues():
                codes += aa_codes_three_to_one(res_name)
            
        # Return the codes.
        return codes


    def pack_structs(self, data_matrix, orig_model_num=None, set_model_num=None, orig_mol_num=None, set_mol_name=None, file_name=None, file_path=None, file_path_abs=None, verbosity=1, merge=False):
        """From the given structural data, expand the structural data data structure.

        @param data_matrix:         A matrix of structural objects.
        @type data_matrix:          list of lists of structural objects
        @keyword orig_model_num:    The original model numbers (for storage).
        @type orig_model_num:       list of int
        @keyword set_model_num:     The new model numbers (for model renumbering).
        @type set_model_num:        list of int
        @keyword orig_mol_num:      The original molecule numbers (for storage).
        @type orig_mol_num:         list of int
        @keyword set_mol_name:      The new molecule names.
        @type set_mol_name:         list of str
        @keyword file_name:         The name of the file from which the molecular data has been extracted.
        @type file_name:            None or str
        @keyword file_path:         The full path to the file specified by 'file_name'.
        @type file_path:            None or str
        @keyword file_path_abs:     The absolute path to the file specified by 'file_name'.  This is a fallback mechanism in case results or save files are located somewhere other than the working directory.
        @type file_path_abs:        None or str
        @keyword verbosity: The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1.
        @type verbosity:    int
        @keyword merge:             A flag which if set to True will try to merge the structure into the currently loaded structures.
        @type merge:                bool
        """

        # Test the number of models.
        if len(orig_model_num) != len(data_matrix):
            raise RelaxError("Structural data mismatch, %s original models verses %s in the structural data." % (len(orig_model_num), len(data_matrix)))

        # Test the number of molecules.
        if len(orig_mol_num) != len(data_matrix[0]):
            raise RelaxError("Structural data mismatch, %s original molecules verses %s in the structural data." % (len(orig_mol_num), len(data_matrix[0])))

        # Model numbers do not change.
        if not set_model_num:
            set_model_num = orig_model_num

        # Test the model mapping.
        if len(set_model_num) != len(data_matrix):
            raise RelaxError("Failure of the mapping of new model numbers, %s new model numbers verses %s models in the structural data." % (len(set_model_num), len(data_matrix)))

        # Test the molecule mapping.
        if len(set_mol_name) != len(data_matrix[0]):
            raise RelaxError("Failure of the mapping of new molecule names, %s new molecule names verses %s molecules in the structural data." % (len(set_mol_name), len(data_matrix[0])))

        # Test that the target models and structures are absent, and get the already existing model numbers.
        for i in range(len(set_model_num)):
            # Merging flag is set, so skip the checks.
            if merge:
                continue

            # A new model, so no need to check.
            if not set_model_num[i] in self.structural_data.current_models:
                continue

            # Loop over the structures.
            index = self.structural_data.current_models.index(set_model_num[i])
            for j in range(len(self.structural_data[index].mol)):
                if self.structural_data[index].mol[j].mol_name in set_mol_name:
                    raise RelaxError("The molecule '%s' of model %s already exists." % (self.structural_data[i].mol[j].mol_name, self.structural_data[i].num))

        # Loop over the models.
        for i in range(len(set_model_num)):
            # The model doesn't currently exist.
            if set_model_num[i] not in self.structural_data.current_models:
                # Create the model.
                self.structural_data.add_item(set_model_num[i])

                # Get the model.
                model = self.structural_data[-1]

            # Otherwise get the pre-existing model.
            else:
                model = self.structural_data[self.structural_data.current_models.index(set_model_num[i])]

            # Loop over the molecules.
            for j in range(len(set_mol_name)):
                # Override the merge argument if the molecule does not exist.
                found = False
                merge_new = True
                for k in range(len(model.mol)):
                    if model.mol[k].mol_name == set_mol_name[j]:
                        found = True
                if not found:
                    merge_new = False

                # Printout.
                if verbosity:
                    if merge_new:
                        print("Merging with model %s of molecule '%s' (from the original molecule number %s of model %s)" % (set_model_num[i], set_mol_name[j], orig_mol_num[j], orig_model_num[i]))
                    else:
                        print("Adding molecule '%s' to model %s (from the original molecule number %s of model %s)" % (set_mol_name[j], set_model_num[i], orig_mol_num[j], orig_model_num[i]))

                # The index of the new molecule to add or merge.
                index = len(model.mol)
                if merge_new:
                    index -= 1

                # Consistency check.
                if model.num != self.structural_data[0].num and self.structural_data[0].mol[index].mol_name != set_mol_name[j]:
                    raise RelaxError("The new molecule name of '%s' in model %s does not match the corresponding molecule's name of '%s' in model %s." % (set_mol_name[j], set_model_num[i], self.structural_data[0].mol[index].mol_name, self.structural_data[0].num))

                # Pack the structures.
                if merge_new:
                    mol = model.mol.merge_item(mol_name=set_mol_name[j], mol_cont=data_matrix[i][j])
                else:
                    mol = model.mol.add_item(mol_name=set_mol_name[j], mol_cont=data_matrix[i][j])

                # Set the molecule name and store the structure file info.
                mol.mol_name = set_mol_name[j]
                mol.file_name = file_name
                mol.file_path = file_path
                mol.file_path_abs = file_path_abs
                mol.file_mol_num = orig_mol_num[j]
                mol.file_model = orig_model_num[i]


    def rotate(self, R=None, origin=None, model=None, selection=None):
        """Rotate the structural information about the given origin.

        @keyword R:         The forwards rotation matrix.
        @type R:            numpy 3D, rank-2 array
        @keyword origin:    The origin of the rotation.
        @type origin:       numpy 3D, rank-1 array
        @keyword model:     The model to rotate.  If None, all models will be rotated.
        @type model:        int
        @keyword selection: The internal structural selection object.  This is obtained by calling the selection() method with the atom ID string.
        @type selection:    lib.structure.internal.Internal_selection instance
        """

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over all molecules and atoms in the selection.
            for mol_index, i in selection.loop():
                mol = model_cont.mol[mol_index]

                # The origin to atom vector.
                vect = array([mol.x[i], mol.y[i], mol.z[i]], float64) - origin

                # Rotation.
                rot_vect = dot(R, vect)

                # The new position.
                pos = rot_vect + origin
                mol.x[i] = pos[0]
                mol.y[i] = pos[1]
                mol.z[i] = pos[2]


    def selection(self, atom_id=None):
        """Convert the atom ID string into a special internal selection object for speed.

        @keyword atom_id:   The molecule, residue, and atom identifier string.  Only atoms matching this selection will be used.
        @type atom_id:      str or None
        @return:            The internal structural selection object.
        @rtype:             Internal_selection instance
        """

        # Initialise the internal structural selection object.
        selection = Internal_selection()

        # Generate the atom ID selection object.
        sel_obj = None
        if atom_id:
            sel_obj = Selection(atom_id)

        # Validate the models.
        self.validate_models(verbosity=0)

        # Obtain all data from the first model (except the position data).
        model = self.structural_data[0]

        # Loop over the molecules.
        for mol_index in range(len(model.mol)):
            mol = model.mol[mol_index]

            # Skip non-matching molecules.
            if sel_obj and not sel_obj.contains_mol(mol.mol_name):
                continue

            # Add the molecule index.
            selection.add_mol(mol_index=mol_index)

            # Loop over the atoms.
            for i in range(len(mol.atom_num)):
                # Skip non-matching atoms.
                if sel_obj and not sel_obj.contains_spin(mol.atom_num[i], mol.atom_name[i], mol.res_num[i], mol.res_name[i], mol.mol_name):
                    continue

                # Add the atom index.
                selection.add_atom(mol_index=mol_index, atom_index=i)

        # Return the object.
        return selection


    def set_model(self, model_orig=None, model_new=None):
        """Set or reset the model number.
        @keyword model_orig:    The original model number.  Leave as None if no models are currently present.
        @type model_orig:       None or int
        @keyword model_new:     The new model number to set the model to.
        @type model_new:        int
        """

        # Check.
        if model_orig == None and self.num_models() != 1:
            raise RelaxError("If the original model number is not supplied, only one model in the current structural object is allowed, but %s were found." % self.num_models())

        # Set the single model number.
        if model_orig == None:
            self.structural_data[0].num = model_new
            return

        # Find the model and set the number.
        set = False
        for i in range(len(self.structural_data)):
            if model_orig == self.structural_data[i].num:
                self.structural_data[i].num = model_new
                set = True

        # Sanity check.
        if not set:
            raise RelaxError("The original model number %s could not be found in the structural object." % model_orig)


    def target_mol_name(self, set=None, target=None, index=None, mol_num=None, file=None):
        """Add the new molecule name to the target data structure.

        @keyword set:       The list of new molecule names.  If not supplied, the names will be generated from the file name.
        @type set:          None or list of str
        @keyword target:    The target molecule name data structure to which the new name will be appended.
        @type target:       list
        @keyword index:     The molecule index, matching the set argument.
        @type index:        int
        @keyword mol_num:   The molecule number.
        @type mol_num:      int
        @keyword file:      The name of the file, excluding all directories.
        @type file:         str
        """

        # Set the target molecule name.
        if set:
            target.append(set[index])
        else:
            # Set the name to the file name plus the structure number.
            target.append(file_root(file) + '_mol' + repr(mol_num))


    def translate(self, T=None, model=None, selection=None):
        """Displace the structural information by the given translation vector.

        @keyword T:         The translation vector.
        @type T:            numpy 3D, rank-1 array
        @keyword model:     The model to rotate.  If None, all models will be rotated.
        @type model:        int
        @keyword selection: The internal structural selection object.  This is obtained by calling the selection() method with the atom ID string.
        @type selection:    lib.structure.internal.Internal_selection instance
        """

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over all molecules and atoms in the selection.
            for mol_index, i in selection.loop():
                mol = model_cont.mol[mol_index]

                # Translate.
                mol.x[i] = mol.x[i] + T[0]
                mol.y[i] = mol.y[i] + T[1]
                mol.z[i] = mol.z[i] + T[2]


    def to_xml(self, doc, element):
        """Prototype method for converting the structural object to an XML representation.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the alignment tensors XML element to.
        @type element:  XML element object
        """

        # Create the structural element and add it to the higher level element.
        str_element = doc.createElement('structure')
        element.appendChild(str_element)

        # Set the structural attributes.
        str_element.setAttribute('desc', 'Structural information')

        # No contents to store, so pack up the structural containers.
        if not self.structural_data.is_empty():
            self.structural_data.to_xml(doc, str_element)

        # The structural metadata.
        metadata = ['helices', 'sheets']
        for name in metadata:
            # The metadata does not exist.
            if not hasattr(self, name):
                continue

            # Get the object.
            obj = getattr(self, name)

            # Create a new element for this object, and add it to the main element.
            sub_elem = doc.createElement(name)
            str_element.appendChild(sub_elem)

            # Add the value to the sub element.
            object_to_xml(doc, sub_elem, value=obj)

        # The displacement structure.
        if hasattr(self, 'displacements'):
            # Create an XML element.
            disp_element = doc.createElement('displacements')
            str_element.appendChild(disp_element)

            # Set the attributes.
            disp_element.setAttribute('desc', 'The rotational and translational displacements between models')

            # Add the displacement data.
            self.displacements.to_xml(doc, disp_element)


    def validate_models(self, verbosity=1):
        """Check that the models are consistent with each other.

        This checks that the primary structure is identical between the models.


        @keyword verbosity: If 0, then all printouts will be silenced.
        @type verbosity:    int
        """

        # Print out.
        if verbosity:
            print("Validating models:")

        # Loop over the models.
        for i in range(len(self.structural_data)):
            # Check the molecules.
            if len(self.structural_data[0].mol) != len(self.structural_data[i].mol):
                raise RelaxError("The number of molecules, %i, in model %i does not match the %i molecules of the first model." % (len(self.structural_data[i].mol), self.structural_data[i].num, len(self.structural_data[0].mol)))

            # Loop over the molecules.
            for j in range(len(self.structural_data[i].mol)):
                # Alias the molecules.
                mol = self.structural_data[i].mol[j]
                mol_ref = self.structural_data[0].mol[j]

                # Check the names.
                if mol.mol_name != mol_ref.mol_name:
                    raise RelaxError("The molecule name '%s' of model %i does not match the name '%s' of the first model." % (mol.mol_name, self.structural_data[i].num, mol_ref.mol_name))

                # Loop over the atoms.
                for k in range(len(mol.atom_name)):
                    # Create pseudo-pdb formatted records (with no atomic coordinates).
                    atom = "%-6s%5s %4s%1s%3s %1s%4s%1s   %8s%8s%8s%6.2f%6.2f      %4s%2s%2s" % ('ATOM', mol.atom_num[k], self._translate(mol.atom_name[k]), '', self._translate(mol.res_name[k]), self._translate(mol.chain_id[k]), self._translate(mol.res_num[k]), '', '#', '#', '#', 1.0, 0, self._translate(mol.seg_id[k]), self._translate(mol.element[k]), '')
                    atom_ref = "%-6s%5s %4s%1s%3s %1s%4s%1s   %8s%8s%8s%6.2f%6.2f      %4s%2s%2s" % ('ATOM', mol_ref.atom_num[k], self._translate(mol_ref.atom_name[k]), '', self._translate(mol_ref.res_name[k]), self._translate(mol_ref.chain_id[k]), self._translate(mol_ref.res_num[k]), '', '#', '#', '#', 1.0, 0, self._translate(mol_ref.seg_id[k]), self._translate(mol_ref.element[k]), '')

                    # Check the atom info.
                    if atom != atom_ref:
                        print(atom)
                        print(atom_ref)
                        raise RelaxError("The atoms of model %i do not match the first model." % self.structural_data[i].num)

        # Final printout.
        if verbosity:
            print("\tAll models are consistent")


    def write_pdb(self, file, model_num=None):
        """Method for the creation of a PDB file from the structural data.

        A number of PDB records including HET, HETNAM, FORMUL, HELIX, SHEET, HETATM, TER, CONECT, MASTER, and END are created.  To create the non-standard residue records HET, HETNAM, and FORMUL, the data structure 'het_data' is created.  It is an array of arrays where the first dimension corresponds to a different residue and the second dimension has the elements:

            0.  Residue number.
            1.  Residue name.
            2.  Chain ID.
            3.  Total number of atoms in the residue.
            4.  Number of H atoms in the residue.
            5.  Number of C atoms in the residue.


        @param file:            The PDB file object.  This object must be writable.
        @type file:             file object
        @keyword model_num:     The model to place into the PDB file.  If not supplied, then all models will be placed into the file.
        @type model_num:        None or int
        """

        # Validate the structural data.
        self.validate()

        # Print out.
        print("\nCreating the PDB records\n")

        # Write some initial remarks.
        print("REMARK")
        pdb_write.remark(file, num=4, remark="This file complies with format v. 3.30, Jul-2011.")
        pdb_write.remark(file, num=40, remark=None)
        pdb_write.remark(file, num=40, remark="Created using relax (http://www.nmr-relax.com).")
        pdb_write.remark(file, num=40, remark=None)
        if RELAX_VERSION:
            pdb_write.remark(file, num=40, remark="relax version %s." % RELAX_VERSION)
        pdb_write.remark(file, num=40, remark="Created on %s." % asctime())
        num_remark = 2

        # Determine if model records will be created.
        model_records = False
        for model in self.model_loop():
            if hasattr(model, 'num') and model.num != None:
                model_records = True


        ####################
        # Hetrogen section #
        ####################

        # Initialise the hetrogen info array.
        het_data = []
        het_data_coll = []

        # Loop over the molecules of the first model.
        index = 0
        for mol in self.structural_data[0].mol_loop():
            # Check the validity of the data.
            self._validate_data_arrays(mol)

            # Append an empty array for this molecule.
            het_data.append([])

            # Collect the non-standard residue info.
            for i in range(len(mol.atom_name)):
                # Skip non-HETATM records and HETATM records with no residue info.
                if mol.pdb_record[i] != 'HETATM' or mol.res_name[i] == None:
                    continue

                # Skip waters.
                if mol.res_name[i] == 'HOH':
                    continue

                # If the residue is not already stored initialise a new het_data element.
                # (residue number, residue name, chain ID, number of atoms, atom count array).
                if not het_data[index] or not mol.res_num[i] == het_data[index][-1][0]:
                    het_data[index].append([mol.res_num[i], mol.res_name[i], CHAIN_ID_LIST[index], 0, []])

                    # Catch missing chain_ids.
                    if het_data[index][-1][2] == None:
                        het_data[index][-1][2] = ''

                # Total atom count.
                het_data[index][-1][3] = het_data[index][-1][3] + 1

                # Find if the atom has already a count entry.
                entry = False
                for j in range(len(het_data[index][-1][4])):
                    if mol.element[i] == het_data[index][-1][4][j][0]:
                        entry = True

                # Create a new specific atom count entry.
                if not entry:
                    het_data[index][-1][4].append([mol.element[i], 0])

                # Increment the specific atom count.
                for j in range(len(het_data[index][-1][4])):
                    if mol.element[i] == het_data[index][-1][4][j][0]:
                        het_data[index][-1][4][j][1] = het_data[index][-1][4][j][1] + 1

            # Create the collective hetrogen info data structure.
            for i in range(len(het_data[index])):
                # Find the entry in the collective structure.
                found = False
                for j in range(len(het_data_coll)):
                    # Different residue numbers.
                    if het_data[index][i][0] != het_data_coll[j][0]:
                        continue

                    # Different chain IDs.
                    if het_data_coll[j][2] != het_data[index][i][2]:
                        continue

                    # Change the flag.
                    found = True

                # If there is no match, add the new residue to the collective.
                if not found:
                    het_data_coll.append(het_data[index][i])

            # Increment the molecule index.
            index = index + 1


        # The HET records.
        ##################

        # Print out.
        print("HET")

        # Write the HET records.
        for het in het_data_coll:
            pdb_write.het(file, het_id=het[1], chain_id=het[2], seq_num=het[0], num_het_atoms=het[3])


        # The HETNAM records.
        #####################

        # Print out.
        print("HETNAM")

        # Loop over the non-standard residues.
        residues = []
        for het in het_data_coll:
            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Get the chemical name.
            chemical_name = self._get_chemical_name(het[1])
            if not chemical_name:
                chemical_name = 'Unknown'

            # Write the HETNAM records.
            pdb_write.hetnam(file, het_id=het[1], text=chemical_name)


        # The FORMUL records.
        #####################

        # Print out.
        print("FORMUL")

        # Loop over the non-standard residues and generate and write the chemical formula.
        residues = []
        for i in range(len(het_data_coll)):
            # Alias.
            het = het_data_coll[i]

            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Initialise the chemical formula.
            formula = ''

            # Loop over the atoms.
            for atom_count in het[4]:
                formula = formula + atom_count[0] + repr(atom_count[1])

            # The FORMUL record (chemical formula).
            pdb_write.formul(file, comp_num=i+1, het_id=het[1], text=formula)


        ###############################
        # Secondary structure section #
        ###############################

        # The HELIX records.
        ####################

        if hasattr(self, 'helices') and len(self.helices):
            # Printout.
            print("HELIX")

            # Loop over and unpack the helix data.
            index = 1
            for helix_id, init_chain_id, init_res_name, init_seq_num, end_chain_id, end_res_name, end_seq_num, helix_class, length in self.helices:
                pdb_write.helix(file, ser_num=index, helix_id=helix_id, init_chain_id=init_chain_id, init_res_name=init_res_name, init_seq_num=init_seq_num, end_chain_id=end_chain_id, end_res_name=end_res_name, end_seq_num=end_seq_num, helix_class=helix_class, length=length)
                index += 1

        # The SHEET records.
        ####################

        if hasattr(self, 'sheets') and len(self.sheets):
            # Printout.
            print("SHEET")

            # Loop over and unpack the helix data.
            index = 1
            for strand, sheet_id, num_strands, init_res_name, init_chain_id, init_seq_num, init_icode, end_res_name, end_chain_id, end_seq_num, end_icode, sense, cur_atom, cur_res_name, cur_chain_id, cur_res_seq, cur_icode, prev_atom, prev_res_name, prev_chain_id, prev_res_seq, prev_icode in self.sheets:
                pdb_write.sheet(file, strand=strand, sheet_id=sheet_id, num_strands=num_strands, init_res_name=init_res_name, init_chain_id=init_chain_id, init_seq_num=init_seq_num, init_icode=init_icode, end_res_name=end_res_name, end_chain_id=end_chain_id, end_seq_num=end_seq_num, end_icode=end_icode, sense=sense, cur_atom=cur_atom, cur_res_name=cur_res_name, cur_chain_id=cur_chain_id, cur_res_seq=cur_res_seq, cur_icode=cur_icode, prev_atom=prev_atom, prev_res_name=prev_res_name, prev_chain_id=prev_chain_id, prev_res_seq=prev_res_seq, prev_icode=prev_icode)
                index += 1


        ######################
        # Coordinate section #
        ######################

        # Initial printout if models are present.
        if model_records:
            print("\nMODEL records:")

        # Loop over the models.
        for model in self.model_loop(model_num):
            # Initialise record counts.
            num_hetatm = 0
            num_atom = 0
            num_ter = 0
            ser_num = 1

            # MODEL record, for multiple models.
            ####################################

            if model_records:
                # Printout.
                sys.stdout.write('.')

                # Write the model record.
                pdb_write.model(file, serial=model.num)


            # Add the atomic coordinate records (ATOM, HETATM, and TER).
            ############################################################

            # Loop over the molecules.
            index = 0
            atom_serial = 0
            for mol in model.mol_loop():
                # Printout.
                if not model_records:
                    print("ATOM, HETATM, TER")

                # Loop over the atomic data.
                atom_record = False
                for i in range(len(mol.atom_name)):
                    # Write the ATOM record.
                    if mol.pdb_record[i] in [None, 'ATOM']:
                        atom_record = True

                        # The atom number.
                        atom_serial += 1

                        # Handle the funky atom name alignment.  From the PDB format documents:
                        # "Alignment of one-letter atom name such as C starts at column 14, while two-letter atom name such as FE starts at column 13."
                        if len(mol.atom_name[i]) == 1:
                            atom_name = " %s" % mol.atom_name[i]
                        else:
                            atom_name = "%s" % mol.atom_name[i]

                        # Write out.
                        pdb_write.atom(file, serial=atom_serial, name=atom_name, res_name=mol.res_name[i], chain_id=CHAIN_ID_LIST[index], res_seq=mol.res_num[i], x=mol.x[i], y=mol.y[i], z=mol.z[i], occupancy=1.0, temp_factor=0, element=mol.element[i])
                        num_atom += 1
                        ser_num += 1

                        # Info for the TER record.
                        ter_num = atom_serial + 1
                        ter_name = mol.res_name[i]
                        ter_chain_id = CHAIN_ID_LIST[index]
                        ter_res_num = mol.res_num[i]

                # Finish the ATOM section with the TER record.
                if atom_record:
                    pdb_write.ter(file, serial=ser_num, res_name=ter_name, chain_id=CHAIN_ID_LIST[index], res_seq=ter_res_num)
                    num_ter += 1
                    ser_num += 1

                # Loop over the atomic data.
                count_shift = False
                for i in range(len(mol.atom_name)):
                    # Write the HETATM record.
                    if mol.pdb_record[i] == 'HETATM':
                        # The atom number.
                        atom_serial += 1

                        # Increment the atom number if a TER record was created.
                        if atom_record and atom_serial == ter_num:
                            count_shift = True
                        if atom_record and count_shift:
                            atom_serial += 1

                        # Write out.
                        pdb_write.hetatm(file, serial=ser_num, name=self._translate(mol.atom_name[i]), res_name=mol.res_name[i], chain_id=CHAIN_ID_LIST[index], res_seq=mol.res_num[i], x=mol.x[i], y=mol.y[i], z=mol.z[i], occupancy=1.0, temp_factor=0.0, element=mol.element[i])
                        num_hetatm += 1
                        ser_num += 1

                # Increment the molecule index.
                index += 1


            # ENDMDL record, for multiple structures.
            ########################################

            if model_records:
                if not model_records:
                    print("ENDMDL")
                pdb_write.endmdl(file)


        # Create the CONECT records.
        ############################

        # Print out.
        if model_records:
            sys.stdout.write('\n')
        print("CONECT")

        # Initialise record counts.
        num_conect = 0

        # The per molecule incremented atom counts.
        atom_counts = [0]
        index = 0
        for mol in self.structural_data[0].mol_loop():
            if index == 0:
                atom_counts.append(len(mol.atom_name))
            else:
                atom_counts.append(atom_counts[index] + len(mol.atom_name))
            index += 1

        # Loop over the molecules of the first model.
        index = 0
        for mol in self.structural_data[0].mol_loop():
            # Loop over the atoms.
            for i in range(len(mol.atom_name)):
                # No bonded atoms, hence no CONECT record is required.
                if not len(mol.bonded[i]):
                    continue

                # Initialise some data structures.
                flush = 0
                bonded_index = 0
                bonded = ['', '', '', '']
                bonded_shifted = ['', '', '', '']

                # Loop over the bonded atoms.
                for j in range(len(mol.bonded[i])):
                    # End of the array, hence create the CONECT record in this iteration.
                    if j == len(mol.bonded[i])-1:
                        flush = True

                    # Only four covalently bonded atoms allowed in one CONECT record.
                    if bonded_index == 3:
                        flush = True

                    # Get the bonded atom index.
                    bonded[bonded_index] = mol.bonded[i][j]

                    # Increment the bonded_index value.
                    bonded_index = bonded_index + 1

                    # Generate the CONECT record and increment the counter.
                    if flush:
                        # Convert the atom indices to atom numbers.
                        for k in range(4):
                            if bonded[k] != '':
                                bonded_shifted[k] = bonded[k] + 1 + atom_counts[index]

                        # Write the CONECT record.
                        pdb_write.conect(file, serial=i+1+atom_counts[index], bonded1=bonded_shifted[0], bonded2=bonded_shifted[1], bonded3=bonded_shifted[2], bonded4=bonded_shifted[3])

                        # Reset the flush flag, the bonded atom count, and the bonded atom names.
                        flush = False
                        bonded_index = 0
                        bonded = ['', '', '', '']

                        # Increment the CONECT record count.
                        num_conect = num_conect + 1

            # Increment the molecule index.
            index += 1


        # MASTER record.
        ################

        print("\nMASTER")
        pdb_write.master(file, num_het=len(het_data_coll), num_coord=num_atom+num_hetatm, num_ter=num_ter, num_conect=num_conect)


        # END.
        ######

        print("END")
        pdb_write.end(file)


    def validate(self):
        """Check the integrity of the structural data.

        The number of molecules must be the same in all models.
        """

        # Reference number of molecules.
        num_mols = len(self.structural_data[0].mol)

        # Loop over all other models.
        for i in range(1, len(self.structural_data)):
            # Model alias.
            model_i = self.structural_data[i]

            # Size check.
            if num_mols != len(model_i.mol):
                raise RelaxError("The structural object is not valid - the number of molecules is not the same for all models.")

            # Molecule name check.
            for j in range(len(model_i.mol)):
                if model_i.mol[j].mol_name != self.structural_data[0].mol[j].mol_name:
                    raise RelaxError("The molecule name '%s' of model %s does not match the corresponding molecule '%s' of model %s." % (model_i.mol[j].mol_name, model_i.num, self.structural_data[0].mol[j].mol_name, self.structural_data[0].num))
