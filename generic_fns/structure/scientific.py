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
"""Module containing the Scientific Python PDB specific structural object class."""


# Python module imports.
from math import sqrt
from numpy import dot, float64, zeros
from warnings import warn

# Scientific Python import.
module_avail = True
try:
    import Scientific.IO.PDB
except ImportError:
    module_avail = False

# relax module imports.
from api_base import Str_object
from data import Data as relax_data_store
from relax_errors import RelaxNoPdbChainError, RelaxNoResError, RelaxPdbLoadError
from relax_warnings import RelaxNoAtomWarning, RelaxZeroVectorWarning


class Scientific_data(Str_object):
    """The Scientific Python specific data object."""

    def load_structures(self, file_path, model, verbosity=False):
        """Function for loading the structures from the PDB file.

        @param file_path:   The full path of the file.
        @type file_path:    str
        @param model:       The PDB model to use.
        @type model:        int
        @param verbosity:   A flag which if True will cause messages to be printed.
        @type verbosity:    bool
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Use pointers (references) if the PDB data exists in another run.
        for data_pipe in relax_data_store:
            if hasattr(data_pipe, 'structure') and hasattr(cdp.structure, 'structures') and data_pipe.structure.file_name == file_path and data_pipe.structure.model == model:
                # Make a pointer to the data.
                cdp.structure.structures = data_pipe.structure.structures

                # Print out.
                if verbosity:
                    print "Using the structures from the data pipe " + `data_pipe.pipe_name` + "."
                    for i in xrange(len(cdp.structure.structures)):
                        print cdp.structure.structures[i]

                # Exit this function.
                return

        # Initialisation.
        cdp.structure.structures = []

        # Load the structure i from the PDB file.
        if type(model) == int:
            # Print out.
            if verbosity:
                print "Loading structure " + `model` + " from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(file_path, model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, file_path

            # Print the PDB info.
            if verbosity:
                print str

            # Place the structure in 'cdp.structure'.
            cdp.structure.structures.append(str)


        # Load all structures.
        else:
            # Print out.
            if verbosity:
                print "Loading all structures from the PDB file."

            # First model.
            i = 1

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(file_path, i)

                # No model 1.
                if len(str) == 0 and i == 1:
                    str = Scientific.IO.PDB.Structure(file_path)
                    if len(str) == 0:
                        raise RelaxPdbLoadError, file_path

                # Test if the last structure has been reached.
                if len(str) == 0:
                    del str
                    break

                # Print the PDB info.
                if verbosity:
                    print str

                # Place the structure in 'cdp.structure'.
                cdp.structure.structures.append(str)

                # Increment i.
                i = i + 1


    def xh_vector(self, data, structure=None, unit=1):
        """Function for calculating/extracting the XH vector from the loaded structure.

        @param data:        The spin system data container.
        @type data:         Residue instance
        @param structure:   The structure number to get the XH vector from.  If set to None and
            multiple structures exist, then the XH vector will be averaged across all structures.
        @type structure:    int
        @param unit:        A flag which if set will cause the function to return the unit XH vector
            rather than the full vector.
        @type unit:         int
        @return:            The XH vector (or unit vector if the unit flag is set).
        @rtype:             list or None
        """

        # Initialise.
        vector_array = []
        ave_vector = zeros(3, float64)

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Number of structures.
        num_str = len(cdp.structure.structures)

        # Loop over the structures.
        for i in xrange(num_str):
            # The vectors from a specific structure.
            if structure != None and structure != i:
                continue

            # Reassign the first peptide or nucleotide chain of the first structure.
            if cdp.structure.structures[i].peptide_chains:
                pdb_residues = cdp.structure.structures[i].peptide_chains[0].residues
            elif cdp.structure.structures[i].nucleotide_chains:
                pdb_residues = cdp.structure.structures[i].nucleotide_chains[0].residues
            else:
                raise RelaxNoPdbChainError

            # Find the corresponding residue in the PDB.
            pdb_res = None
            for k in xrange(len(pdb_residues)):
                if data.num == pdb_residues[k].number:
                    pdb_res = pdb_residues[k]
                    break
            if pdb_res == None:
                raise RelaxNoResError, data.num

            # Test if the proton atom exists for residue i.
            if not pdb_res.atoms.has_key(data.proton):
                warn(RelaxNoAtomWarning(data.proton, data.num))

            # Test if the heteronucleus atom exists for residue i.
            elif not pdb_res.atoms.has_key(data.heteronuc):
                warn(RelaxNoAtomWarning(data.heteronuc, data.num))

            # Calculate the vector.
            else:
                # Get the proton position.
                posH = pdb_res.atoms[data.proton].position.array

                # Get the heteronucleus position.
                posX = pdb_res.atoms[data.heteronuc].position.array

                # Calculate the XH bond vector.
                vector = posH - posX

                # Unit vector.
                if unit:
                    # Normalisation factor.
                    norm_factor = sqrt(dot(vector, vector))

                    # Test for zero length.
                    if norm_factor == 0.0:
                        warn(RelaxZeroVectorWarning(data.num))

                    # Calculate the normalised vector.
                    else:
                        vector_array.append(vector / norm_factor)

                # Normal XH vector.
                else:
                    vector_array.append(vector)

        # Return None if there are no vectors.
        if not len(vector_array):
            return

        # Sum the vectors.
        for vector in vector_array:
            # Sum.
            ave_vector = ave_vector + vector

        # Average the vector.
        ave_vector = ave_vector / len(vector_array)

        # Unit vector.
        if unit:
            ave_vector = ave_vector / sqrt(dot(ave_vector, ave_vector))

        # Return the vector.
        return ave_vector
