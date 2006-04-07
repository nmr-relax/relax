###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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

from doc_string import regexp_doc
import help
from generic_fns.minimise import Minimise
from specific_fns.model_free import Model_free
from specific_fns.jw_mapping import Jw_mapping
from specific_fns.noe import Noe


class Molmol:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with Molmol."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def clear_history(self):
        """Function for clearing the Molmol command history."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.clear_history()"
            print text

        # Execute the functional code.
        self.__relax__.generic.molmol.clear_history()


    def command(self, command):
        """Function for executing a user supplied Molmol command.

        Example
        ~~~~~~~

        relax> molmol.command("InitAll yes")
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.command("
            text = text + "command=" + `command` + ")"
            print text

        # The command argument.
        if type(command) != str:
            raise RelaxStrError, ('command', command)

        # Execute the functional code.
        self.__relax__.generic.molmol.write(command=command)


    def view(self, run=None):
        """Function for viewing the collection of molecules extracted from the PDB file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run which the PDB belongs to.


        Example
        ~~~~~~~

        relax> molmol.view('m1')
        relax> molmol.view(run='pdb')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.view("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.molmol.view(run=run)


    def write(self, run=None, data_type=None, style="classic", file=None, dir='molmol', force=0):
        """Function for creating Molmol macros.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The data type to map to the structure.

        style:  The style of the macro.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to 1, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        This function allows residues specific values to be mapped to a structure through the
        creation of a Molmol '*.mac' macro which can be executed in Molmol by clicking on 'File,
        Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is
        availible.


        Classic style
        ~~~~~~~~~~~~~

        Creator:  Edward d'Auvergne

        Argument string:  "classic"

        Description:  The classic style draws the backbone of the protein in 'neon' style.  Rather
        than colouring the amino acids to which the NH bond belongs, the three covalent bonds of the
        petide bond from Ca to Ca to which the NH bond belongs is coloured.

        Supported data types:
        Model-free:  S2, te, Rex.
        


        Examples
        ~~~~~~~~

        To create a Molmol macro mapping the order parameter values, S2, of the run 'final' onto the
        structure using the classic style, type:

        relax> molmol.write('final', 'S2')
        relax> molmol.write('final', data_type='S2')
        relax> molmol.write('final', data_type='S2', style="classic", file='s2.mac', dir='molmol')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molmol.write("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", style=" + `style`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type for mapping to the structure.
        if type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # The style.
        if type(style) != str:
            raise RelaxStrError, ('style', style)

        # File.
        if file != None and type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            raise RelaxBinError, ('force flag', force)

        # Execute the functional code.
        self.__relax__.generic.molmol.write(run=run, data_type=data_type, style=style, file=file, dir=dir, force=force)



    # Docstring modification.
    #########################

    # Write function.
    write.__doc__ = write.__doc__ + "\n\n" + regexp_doc() + "\n"
    write.__doc__ = write.__doc__ + Minimise.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Model_free.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Jw_mapping.return_data_name.__doc__ + "\n\n"
    write.__doc__ = write.__doc__ + Noe.return_data_name.__doc__ + "\n"
