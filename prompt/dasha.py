###############################################################################
#                                                                             #
# Copyright (C) 2005-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'dasha' user function class for controlling the Dasha model-free software."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import dasha
from status import Status; status = Status()


class Dasha(User_fn_class):
    """Class for interfacing with the program Dasha."""

    def create(self, algor='LM', dir=None, force=False):
        """Function for creating the Dasha script.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        algor:  The minimisation algorithm.

        dir:  The directory to place the files.

        force:  A flag which if set to True will cause the results file to be overwritten if it
        already exists.


        Description
        ~~~~~~~~~~~

        The script file created is called 'dir/dasha_script'.


        Optimisation algorithms
        ~~~~~~~~~~~~~~~~~~~~~~~

        The two minimisation algorithms within Dasha are accessible through the algor argument which
        can be set to:

            'LM' - The Levenberg-Marquardt algorithm.
            'NR' - Newton-Raphson algorithm.

        For Levenberg-Marquardt minimisation, the function 'lmin' will be called, while for Newton
        -Raphson, the function 'min' will be executed.
        """

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "dasha.create("
            text = text + "algor=" + repr(algor)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(algor, 'optimisation algorithm')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        dasha.create(algor=algor, dir=dir, force=force)


    def execute(self, dir=None, force=False, binary='dasha'):
        """Function for executing Dasha.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory to place the files.

        force:  A flag which if set to True will cause the results file to be overwritten if it
        already exists.

        binary:  The name of the executable Dasha program file.


        Execution
        ~~~~~~~~~

        Dasha will be executed as

        $ dasha < dasha_script | tee dasha_results


        If you would like to use a different Dasha executable file, change the keyword argument
        'binary' to the appropriate file name.  If the file is not located within the environment's
        path, include the full path in front of the binary file name.
        """

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "dasha.execute("
            text = text + "dir=" + repr(dir)
            text = text + ", force=" + repr(force)
            text = text + ", binary=" + repr(binary) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')
        arg_check.is_str(binary, 'Dasha executable file')

        # Execute the functional code.
        dasha.execute(dir=dir, force=force, binary=binary)


    def extract(self, dir=None):
        """Function for extracting data from the Dasha results file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        dir:  The directory where the file 'dasha_results' is found.
        """

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "dasha.extract("
            text = text + "dir=" + repr(dir) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(dir, 'directory name', can_be_none=True)

        # Execute the functional code.
        dasha.extract(dir=dir)
