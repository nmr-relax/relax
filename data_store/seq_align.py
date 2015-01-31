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
from lib.structure.internal.coordinates import generate_id


class Sequence_alignments(RelaxListType):
    """The structure for holding all sequence alignments."""

    def __init__(self):
        """Initialise some class variables."""

        # Execute the base class __init__() method.
        super(Sequence_alignments, self).__init__()

        # Some generic initial names.
        self.list_name = 'sequence_alignments'
        self.list_desc = 'List of all multiple sequence alignments'


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


    def find_alignment(self, object_ids=None, models=None, molecules=None, sequences=None, msa_algorithm=None, pairwise_algorithm=None, matrix=None, gap_open_penalty=None, gap_extend_penalty=None, end_gap_open_penalty=None, end_gap_extend_penalty=None):
        """Find any pre-existing sequence alignment.

        @keyword object_ids:                The list of IDs for each structural object in the alignment.  In most cases this will be the data pipe name.  This will be used to retrieve alignments.
        @type object_ids:                   list of str
        @keyword models:                    The list of model numbers used in the alignment.  This will be used to retrieve alignments.
        @type models:                       list of int
        @keyword molecules:                 The list of molecules used in the alignment.  This will be used to retrieve alignments.
        @type molecules:                    list of str
        @keyword sequences:                 The list of residue sequences for the alignment as one letter codes.
        @type sequences:                    list of str
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
        @return:                            Any matching sequence alignment object.
        @rtype:                             Alignment instance
        """

        # Loop over all current alignments.
        for i in range(len(self)):
            # Starting flag.
            found = True

            # Loop over the molecules.
            for j in range(len(object_ids)):
                # Check for any mismatches (breaking the loop for speed by avoiding unnecessary checks).
                if self[i].object_ids[j] != object_ids[j]:
                    found = False
                    break
                if self[i].models[j] != models[j]:
                    found = False
                    break
                if self[i].molecules[j] != molecules[j]:
                    found = False
                    break
                if self[i].sequences[j] != sequences[j]:
                    found = False
                    break

            # No match (skip the rest of the checks for speed).
            if not found:
                continue

            # Check the alignment settings for mismatches.
            if msa_algorithm and self[i].msa_algorithm != msa_algorithm:
                continue
            if pairwise_algorithm and self[i].pairwise_algorithm != pairwise_algorithm:
                continue
            if matrix and self[i].matrix != matrix:
                continue
            if gap_open_penalty != None and self[i].gap_open_penalty != gap_open_penalty:
                continue
            if gap_extend_penalty != None and  self[i].gap_extend_penalty != gap_extend_penalty:
                continue
            if end_gap_open_penalty != None and  self[i].end_gap_open_penalty != end_gap_open_penalty:
                continue
            if end_gap_extend_penalty != None and  self[i].end_gap_extend_penalty != end_gap_extend_penalty:
                continue

            # No mismatches, so this must be the alignment.
            return self[i]


    def from_xml(self, sequence_alignments_node, file_version=1):
        """Recreate the analyses data structure from the XML analyses node.

        @param sequence_alignments_node:    The sequence alignments XML node.
        @type sequence_alignments_node:     xml.dom.minicompat.Element instance
        @keyword file_version:              The relax XML version of the XML file.
        @type file_version:                 int
        """

        # Get all the alignment nodes.
        align_nodes = sequence_alignments_node.getElementsByTagName('sequence_alignment')

        # Loop over the nodes.
        for node in align_nodes:
            # Add a blank alignment container.
            self.append(Alignment(object_ids=[]))

            # Recreate the analysis container.
            self[-1].from_xml(node, file_version=file_version)



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

        # Execute the base class __init__() method.
        super(Alignment, self).__init__(name='sequence_alignment', desc='Multiple sequence alignment container.')

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
            self.ids.append(generate_id(object_id=self.object_ids[i], model=self.models[i], molecule=self.molecules[i]))

        # Check the IDs for uniqueness.
        for i in range(len(self.ids)):
            for j in range(len(self.ids)):
                if i == j:
                    continue
                if self.ids[i] == self.ids[j]:
                    raise RelaxError("The molecule ID '%s' is not unique." % self.ids[i])
