###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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


class OpenDX:
    def __init__(self, relax):
        """Macro for the execution of OpenDX."""

        self.relax = relax


    def dx(self, file="map", dir="dx", dx_exec="dx", execute=1):
        """Function for running OpenDX.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The file name prefix.  For example if file is set to 'temp', then the OpenDX program
        temp.net will be loaded.

        dir:  The directory to change to for running OpenDX.  If this is set to 'None', OpenDX will
        be run in the current directory.

        dx_exec:  The OpenDX executable file.  The default is 'dx'.

        execute:  The flag specifying whether to execute the visual program automatically at
        start-up.  The default is 1 which turns execution on.  Setting the value to zero turns
        execution off.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "dx("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", dx_exec=" + `dx_exec`
            text = text + ", execute=" + `execute` + ")"
            print text

        # File name.
        if type(file) != str:
            raise UserArgStrError, ('file name', file)

        # Directory name.
        if dir == None:
            pass
        elif type(dir) != str:
            raise UserArgNoneStrError, ('file name', file)

        # The OpenDX executable file.
        if type(dx_exec) != str:
            raise UserArgStrError, ('OpenDX executable file name', dx_exec)

        # Execute flag.
        if type(execute) != int or (execute != 0 and execute != 1):
            raise UserArgBinError, ('execute flag', execute)

        # Execute the functional code.
        self.relax.opendx.run(file=file, dir=dir, dx_exec=dx_exec, execute=execute)
