###############################################################################
#                                                                             #
# Copyright (C) 2004-2006 Edward d'Auvergne                                   #
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

import sys

import help


class Run:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for holding the functions for manipulating runs."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create(self, run=None, run_type=None):
        """Function for setting up a run type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        type:  The type of run.


        Description
        ~~~~~~~~~~~

        The run name can be any string however the run type can only be one of the following

            'jw':  Reduced spectral density mapping,
            'mf':  Model-free analysis,
            'mf_csa':  Model-free analysis with asymmetric CST,
            'noe':  Steady state NOE calculation,
            'relax_fit':  Relaxation curve fitting,
            'srls':  SRLS analysis.


        Examples
        ~~~~~~~~

        To set up a model-free analysis run with the name 'm5', type:

        relax> run.create('m5', 'mf')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "run.create("
            text = text + "run=" + `run`
            text = text + ", run_type=" + `run_type` + ")"
            print text

        # The name of the run.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The run type.
        if type(run_type) != str:
            raise RelaxStrError, ('run_type', run_type)

        # Execute the functional code.
        self.__relax__.generic.runs.create(run=run, run_type=run_type)


    def delete(self, run=None):
        """Function for deleting a run.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.


        Description
        ~~~~~~~~~~~

        This function will destroy all data corresponding to the given run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "run.delete("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if run != None and type(run) != str:
            raise RelaxNoneStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.runs.delete(run=run)


    def hybridise(self, hybrid=None, runs=None):
        """Function for a hybridised run from a number of other runs.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        hybrid:  The name of the hybrid run to create.

        runs:  An array containing the names of all runs to hybridise.


        Description
        ~~~~~~~~~~~

        This user function can be used to construct hybrid models.  An example of the use of a
        hybrid model could be if the protein consists of two independent domains.  These two domains
        could be analysed separately, each having their own optimised diffusion tensors.  The
        N-terminal domain run could be called 'N_sphere' while the C-terminal domain could be called
        'C_ellipsoid'.  These two runs could then be hybridised into a run called 'mixed model' by
        typing

        relax> run.hybridise('mixed model', ['N_sphere', 'C_ellipsoid'])
        relax> run.hybridise(hybrid='mixed model', runs=['N_sphere', 'C_ellipsoid'])

        This hybrid run can then be compared via model selection to a run where the entire protein
        is assumed to have a single diffusion tensor.

        The only requirements for runs to be hybridised is that, at minimum, a sequence has been
        loaded, that the sequence for all hybridised runs is the same, and that no residue is
        allowed to be selected in two or more runs.  The last condition is to ensure that overlap
        does not occur to allow statistically significant comparisons.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "run.hybridise("
            text = text + "hybrid=" + `hybrid`
            text = text + ", runs=" + `runs` + ")"
            print text

        # The hybrid argument.
        if hybrid != None and type(hybrid) != str:
            raise RelaxNoneStrError, ('hybrid run', hybrid)

        # Runs.
        if type(runs) != list:
            raise RelaxNoneListError, ('runs', runs)
        else:
            for name in runs:
                if type(name) != str:
                    raise RelaxListStrError, ('runs', runs)

        # Execute the functional code.
        self.__relax__.specific.hybrid.hybridise(hybrid=hybrid, runs=runs)
