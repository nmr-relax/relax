###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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


class Create_run:
    def __init__(self, relax):
        """Class containing the macro for setting up a run type."""

        self.relax = relax


    def create(self, run=None, run_type=None):
        """Macro for setting up a run type.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        type:  The type of run.


        Description
        ~~~~~~~~~~~

        The run name can be any string however the run type can only be one of the following:

            'mf' - Model-free analysis.


        Examples
        ~~~~~~~~

        To set up a model-free analysis run with the name 'm5', type:

        relax> create_run('m5', 'mf')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "create_run("
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
        self.relax.create_run.create(run=run, run_type=run_type)
