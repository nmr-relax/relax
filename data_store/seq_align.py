###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
"""Sequence alignment data structures."""

# relax module imports.
from data_store.data_classes import Element, RelaxListType
from lib.errors import RelaxError


class Sequence_alignments(RelaxListType):
    """The structure for holding all sequence alignments."""

    def add(self, object_ids=None, models=None, molecules=None, sequences=None, strings=None, gaps=None, msa_algorithm=None, pairwise_algorithm=None, matrix=None, gap_open_penalty=None, gap_extend_penalty=None, end_gap_open_penalty=None, end_gap_extend_penalty=None):
        """Add a new sequence alignment.

        @keyword object_ids:                The list of IDs for each structural object in the alignment.  In most cases this will be the data pipe name.  This will be used to retrieve alignments.
        @type object_ids:                   list of str
        @keyword models:                    The list of model numbers used in the alignment.  This will be used to retrieve alignments.
        @type models:                       list of int
        @keyword molecules:                 The list of molecules used in the alignment.  This will be used to retrieve alignments.
        @type molecules:                    list of str
        @keyword sequences:                 The list of residue sequences for the alignment as one letter codes.
        @type sequences:                    list of str
        @keyword strings:                   The list of alignment strings.
        @type strings:                      list of str
        @keyword gaps:                      The alignment gap matrix.
        @type gaps:                         numpy rank-2 int array
        @keyword msa_algorithm:             The global multiple sequence alignment (MSA) algorithm.
        @type msa_algorithm:                str
        @keyword pairwise_algorithm:        The pairwise sequence alignment algorithm.
        @type pairwise_algorithm:           str
        @keyword matrix:                    The substitution matrix
        @type matrix:                       str
        @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
        @type gap_open_penalty:             float
        @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
        @type gap_extend_penalty:           float
        @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
        @type end_gap_open_penalty:         float
        @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
        @type end_gap_extend_penalty:       float
        """

        # Append a new element.
        self.append(Alignment(object_ids=object_ids, molecules=molecules, models=models, sequences=sequences, strings=strings, gaps=gaps, msa_algorithm=msa_algorithm, pairwise_algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty))



class Alignment(Element):
    """Container for an individual sequence alignment."""

    def __init__(self, object_ids=None, models=None, molecules=None, sequences=None, strings=None, gaps=None, msa_algorithm=None, pairwise_algorithm=None, matrix=None, gap_open_penalty=None, gap_extend_penalty=None, end_gap_open_penalty=None, end_gap_extend_penalty=None):
        """Set up the sequence alignment object.

        @keyword object_ids:                The list of IDs for each structural object in the alignment.  In most cases this will be the data pipe name.  This will be used to retrieve alignments.
        @type object_ids:                   list of str
        @keyword models:                    The list of model numbers used in the alignment.  This will be used to retrieve alignments.
        @type models:                       list of int
        @keyword molecules:                 The list of molecules used in the alignment.  This will be used to retrieve alignments.
        @type molecules:                    list of str
        @keyword sequences:                 The list of residue sequences for the alignment as one letter codes.
        @type sequences:                    list of str
        @keyword strings:                   The list of alignment strings.
        @type strings:                      list of str
        @keyword gaps:                      The alignment gap matrix.
        @type gaps:                         numpy rank-2 int array
        @keyword msa_algorithm:             The global multiple sequence alignment (MSA) algorithm.
        @type msa_algorithm:                str
        @keyword pairwise_algorithm:        The pairwise sequence alignment algorithm.
        @type pairwise_algorithm:           str
        @keyword matrix:                    The substitution matrix
        @type matrix:                       str
        @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
        @type gap_open_penalty:             float
        @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
        @type gap_extend_penalty:           float
        @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
        @type end_gap_open_penalty:         float
        @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
        @type end_gap_extend_penalty:       float
        """

        # Store the values.
        self.object_ids = object_ids
        self.models = models
        self.molecules = molecules
        self.sequences = sequences
        self.strings = strings
        self.gaps = gaps
        self.msa_algorithm = msa_algorithm
        self.pairwise_algorithm = pairwise_algorithm
        self.matrix = matrix
        self.gap_open_penalty = gap_open_penalty
        self.gap_extend_penalty = gap_extend_penalty
        self.end_gap_open_penalty = end_gap_open_penalty
        self.end_gap_extend_penalty = end_gap_extend_penalty

        # Create a unique ID for each molecule.
        self.ids = [] 
        for i in range(len(self.object_ids)):
            self.ids.append(self.generate_id(object_id=self.object_ids[i], model=self.models[i], molecule=self.molecules[i]))

        # Check the IDs for uniqueness.
        for i in range(len(self.ids)):
            for j in range(len(self.ids)):
                if i == j:
                    continue
                if self.ids[i] == self.ids[j]:
                    raise RelaxError("The molecule ID '%s' is not unique." % self.ids[i])


    def generate_id(object_id=None, model=None, molecule=None):
        """Generate a unique ID.

        @keyword object_id: The structural object ID.
        @type object_id:    str
        @keyword model:     The model number.
        @type model:        int
        @keyword molecule:  The molecule name.
        @type molecule:     str
        @return:            The unique ID constructed from the object ID, model number and molecule name.
        @rtype:             str
        """

        # Init.
        id = ''

        # The object ID.
        if object_id != None:
            id += "Object '%s'" % object_id

        # The model number.
        if len(id):
            id += '; '
        if model != None:
            id += "Model %i" % model

        # The molecule name.
        if len(id):
            id += '; '
        if molecule != None:
            id += "Molecule '%s'" % molecule

        # Sanity check.
        if not len(id):
            raise RelaxError("No alignment ID could be constructed.")

        # Return the ID.
        return id
