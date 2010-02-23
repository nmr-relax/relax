###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2010 Edward d'Auvergne                        #
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
"""Module containing the 'pymol' user function class for interacting with PyMOL."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
import colour
from generic_fns import pymol


class Pymol(User_fn_class):
    """Class for interfacing with PyMOL."""

    def cartoon(self):
        """Apply the PyMOL cartoon style and colour by secondary structure.


        Description
        ~~~~~~~~~~~

        This function applies the PyMOL cartoon style which is equivalent to hiding everything and
        clicking on show cartoon.  It also colours the cartoon with red helices, yellow strands, and
        green loops.  The following commands are executed:

            cmd.hide('everything', file)
            cmd.show('cartoon', file)
            util.cbss(file, 'red', 'yellow', 'green')

        where file is the file name without the '.pdb' extension.


        Example
        ~~~~~~~

        To apply this user function, type:

        relax> pymol.cartoon()
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.cartoon()"
            print(text)

        # Execute the functional code.
        pymol.cartoon()


    def clear_history(self):
        """Function for clearing the PyMOL command history."""

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.clear_history()"
            print(text)

        # Execute the functional code.
        self.__relax__.generic.pymol.clear_history()


    def command(self, command=None):
        """Function for executing a user supplied PyMOL command.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        command:  The PyMOL command to execute.


        Description
        ~~~~~~~~~~~

        This user function allows you to pass PyMOL commands to the program.  This can be useful
        for automation or scripting.


        Example
        ~~~~~~~

        To reinitialise the PyMOL instance, type:

        relax> pymol.command("reinitialise")
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.command("
            text = text + "command=" + repr(command) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(command, 'pymol command')

        # Execute the functional code.
        pymol.command(command=command)


    def cone_pdb(self, file=None):
        """Display, as designed, the cone PDB geometric object from the N-state model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the PDB file containing the cone geometric object.


        Description
        ~~~~~~~~~~~

        The PDB file containing the geometric object must be created using the complementary
        'n_state_model.cone_pdb()' user function.

        The cone PDB file is read in using the command:

            load file

        The average CoM-pivot point vector, the residue 'AVE' is displayed using the commands:

            select resn AVE
            show sticks, 'sele'
            color blue, 'sele'

        The cone object, the residue 'CON', is displayed using the commands:

            select resn CON
            hide ('sele')
            show sticks, 'sele'
            color white, 'sele'
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.cone_pdb("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')

        # Execute the functional code.
        pymol.cone_pdb(file=file)


    def macro_exec(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
        """Function for executing PyMOL macros.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        data_type:  The data type to map to the structure.

        style:  The style of the macro.

        colour_start:  The starting colour, either an array or string, of the linear colour
        gradient.

        colour_end:  The ending colour, either an array or string, of the linear colour gradient.

        colour_list:  The list of colours to match the start and end strings.


        Description
        ~~~~~~~~~~~

        This function allows residues specific values to be mapped to a structure through PyMOL
        macros.  Currently only the 'classic' style, which is described below, is available.


        Colour
        ~~~~~~

        The values are coloured based on a linear colour gradient which is specified through the
        'colour_start' and 'colour_end' arguments.  These arguments can either be a string to
        identify one of the RGB (red, green, blue) colour arrays listed in the tables below, or you
        can give the RGB vector itself.  For example, colour_start='white' and
        colour_start=[1.0, 1.0, 1.0] both select the same colour.  Leaving both arguments at None
        will select the default colour gradient which for each type of analysis is described below.

        When supplying the colours as strings, two lists of colours can be selected from which to
        match the strings.  These are the default PyMOL colour list and the X11 colour list, both
        of which are described in the tables below.  The default behaviour is to first search the
        Molmol list and then the X11 colour list, raising an error if neither contain the string.
        To explicitly select these lists, set the 'colour_list' argument to either 'molmol' or
        'x11'.


        Examples
        ~~~~~~~~

        To map the order parameter values, S2, onto the structure using the classic style, type:

        relax> pymol.macro_exec('S2')
        relax> pymol.macro_exec(data_type='S2')
        relax> pymol.macro_exec(data_type='S2', style="classic")
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.macro_exec("
            text = text + "data_type=" + repr(data_type)
            text = text + ", style=" + repr(style)
            text = text + ", colour_start=" + repr(colour_start)
            text = text + ", colour_end=" + repr(colour_end)
            text = text + ", colour_list=" + repr(colour_list) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(data_type, 'data type')
        arg_check.is_str(style, 'style')
        arg_check.is_str_or_num_list(colour_start, 'starting colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str_or_num_list(colour_end, 'ending colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str(colour_list, 'colour list', can_be_none=True)

        # Execute the functional code.
        pymol.macro_exec(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)


    def tensor_pdb(self, file=None):
        """Function displaying the diffusion tensor PDB geometric object over the loaded PDB.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the PDB file containing the tensor geometric object.


        Description
        ~~~~~~~~~~~

        In executing this user function, a PDB file must have previously been loaded into this data
        pipe a geometric object or polygon representing the Brownian rotational diffusion tensor
        will be overlain with the loaded PDB file and displayed within PyMOL.  The PDB file
        containing the geometric object must be created using the complementary
        'pdb.create_diff_tensor_pdb()' user function.

        The tensor PDB file is read in using the command:

            load file

        The centre of mass residue 'COM' is displayed using the commands:

            select resn COM
            show dots, 'sele'
            color blue, 'sele'

        The axes of the diffusion tensor, the residue 'AXS', is displayed using the commands:

            select resn AXS
            hide ('sele')
            show sticks, 'sele'
            color cyan, 'sele'
            label 'sele', name

        The simulation axes, the residues 'SIM', are displayed using the commands:

            select resn SIM
            colour cyan, 'sele'
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.tensor_pdb("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(file, 'file name')

        # Execute the functional code.
        pymol.tensor_pdb(file=file)


    def vector_dist(self, file='XH_dist.pdb'):
        """Function displaying the PDB file representation of the XH vector distribution.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the PDB file containing the vector distribution.


        Description
        ~~~~~~~~~~~

        A PDB file of the macromolecule must have previously been loaded as the vector distribution
        will be overlain with the macromolecule within PyMOL.  The PDB file containing the vector
        distribution must be created using the complementary 'pdb.create_vector_dist()' user
        function.

        The vector distribution PDB file is read in using the command:

            load file

        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.vector_dist("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')

        # Execute the functional code.
        pymol.vector_dist(file=file)


    def view(self):
        """Function for viewing the collection of molecules extracted from the PDB file.


        Example
        ~~~~~~~

        relax> pymol.view()
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.view()"
            print(text)

        # Execute the functional code.
        pymol.view()


    def write(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir='pymol', force=False):
        """Function for creating PyMOL macros.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        data_type:  The data type to map to the structure.

        style:  The style of the macro.

        colour_start:  The starting colour, either an array or string, of the linear colour
        gradient.

        colour_end:  The ending colour, either an array or string, of the linear colour gradient.

        colour_list:  The list of colours to match the start and end strings.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which, if set to True, will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        This function allows residues specific values to be mapped to a structure through the
        creation of a PyMOL macro which can be executed in PyMOL by clicking on 'File,
        Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is
        available.


        Colour
        ~~~~~~

        The values are coloured based on a linear colour gradient which is specified through the
        'colour_start' and 'colour_end' arguments.  These arguments can either be a string to
        identify one of the RGB (red, green, blue) colour arrays listed in the tables below, or you
        can give the RGB vector itself.  For example, colour_start='white' and
        colour_start=[1.0, 1.0, 1.0] both select the same colour.  Leaving both arguments at None
        will select the default colour gradient which for each type of analysis is described below.

        When supplying the colours as strings, two lists of colours can be selected from which to
        match the strings.  These are the default PyMOL colour list and the X11 colour list, both
        of which are described in the tables below.  The default behaviour is to first search the
        PyMOL list and then the X11 colour list, raising an error if neither contain the string.
        To explicitly select these lists, set the 'colour_list' argument to either 'molmol' or
        'x11'.


        Examples
        ~~~~~~~~

        To create a PyMOL macro mapping the order parameter values, S2, onto the structure using
        the classic style, type:

        relax> pymol.write('S2')
        relax> pymol.write(data_type='S2')
        relax> pymol.write(data_type='S2', style="classic", file='s2.mac', dir='pymol')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "pymol.write("
            text = text + "data_type=" + repr(data_type)
            text = text + ", style=" + repr(style)
            text = text + ", colour_start=" + repr(colour_start)
            text = text + ", colour_end=" + repr(colour_end)
            text = text + ", colour_list=" + repr(colour_list)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(data_type, 'data type')
        arg_check.is_str(style, 'style')
        arg_check.is_str_or_num_list(colour_start, 'starting colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str_or_num_list(colour_end, 'ending colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str(colour_list, 'colour list', can_be_none=True)
        arg_check.is_str_or_inst(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        pymol.write(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=dir, force=force)



    # Docstring modification.
    #########################

    # Write function.
    #write.__doc__ = write.__doc__ + "\n\n" + Pymol.classic.__doc__ + "\n\n"

    # Molmol RGB colour list.
    write.__doc__ = write.__doc__ + "\n\n" + colour.__molmol_colours_prompt_doc__ + "\n\n"

    # X11 RGB colour list.
    write.__doc__ = write.__doc__ + "\n\n" + colour.__x11_colours_prompt_doc__ + "\n\n"
