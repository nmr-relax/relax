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


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.load = x.load
        self.save = x.save


class Macro_class:
    def __init__(self, relax):
        """Class containing the macros for manipulating the program state."""

        self.relax = relax


    def load(self, file_name=None):
        """Macro for loading a saved program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file_name:  The file name, which must be a string, of a saved program state.


        Examples
        ~~~~~~~~

        The following commands will load the state saved in the file 'save'.

        relax> state.load('save')
        relax> state.load(file_name='save')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "state.load("
            text = text + "file_name=" + `file_name` + ")\n"
            print text

        # Test arguments
        if type(file_name) != str:
            print "The file name argument " + `file_name` + " is not a string."
            return

        # Execute the functional code.
        self.relax.state.load(file_name=file_name)


    def save(self, file_name=None, force=0):
        """Macro for saving the program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file_name:  The file name, which must be a string, to save the current program state in.

        force:  A flag which if set to 1 will cause the file to be overwritten.


        Examples
        ~~~~~~~~

        The following commands will save the current program state into the file 'save'.

        relax> state.save('save')
        relax> state.save(file_name='save')


        If the file 'save' already exists, the following commands will save the current program
        state by overwriting the file.

        relax> state.save('save', 1)
        relax> state.save(file_name='save', force=1)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "state.save("
            text = text + "file_name=" + `file_name`
            text = text + ", force=" + `force` + ")\n"
            print text

        # File name.
        if type(file_name) != str:
            print "The file name argument " + `file_name` + " is not a string."
            return

        # The force flag.
        if type(force) != int or (force != 0 and force != 1):
            print "The force flag should be the integer values of either 0 or 1."
            return

        # Execute the functional code.
        self.relax.state.save(file_name=file_name, force=force)
