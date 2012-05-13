###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Functions for executing relax scripts."""

# Python module imports.
from os import F_OK, access

# relax module imports.
import prompt.interpreter
from relax_errors import RelaxError
from relax_io import get_file_path
from status import Status; status = Status()


def script(file=None, dir=None):
    """Function for executing a script file.

    @keyword file:  The name of the script to execute.
    @type file:     str
    @keyword dir:   The name of the directory in which the script is located.
    @type dir:      str or None
    """

    # File argument.
    if file == None:
        raise RelaxNoneError('file')
    elif not isinstance(file, str):
        raise RelaxStrError('file', file)

    # The full path.
    file_path = get_file_path(file, dir)

    # Test if the script file exists.
    if not access(file_path, F_OK):
        raise RelaxError("The script file '%s' does not exist." % file_path)

    # Turn on the function intro flag.
    orig_intro_state = status.prompt_intro
    status.prompt_intro = True

    # Load the interpreter.
    interpreter = prompt.interpreter.Interpreter(show_script=False, quit=False, raise_relax_error=True)
    interpreter.populate_self()
    interpreter.on(verbose=False)

    # Execute the script.
    prompt.interpreter.run_script(local=interpreter._locals, script_file=file_path)

    # Return the function intro flag to the original value.
    status.prompt_intro = orig_intro_state
