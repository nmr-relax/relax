###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


    def set(self, run=None, data_type=None, val=None, err=None, res_num=None):
        """Function for setting data structure values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        res_num:  The residue number.

        data_type:  A string specifying the data type.

        val:  The value.

        err:  The error.


        Description
        ~~~~~~~~~~~

        If 'res_num' is set to the default of None, then all residues will have the value of
        'data_type' given by 'val', otherwise the single residue will be set to 'val'.


        Data type
        ~~~~~~~~~

        The following types are currently supported:
        _________________________________________________________________
        |                         |                                     |
        | Type                    | Pattern                             |
        |-------------------------|-------------------------------------|
        |                         |                                     |
        | Bond length             | '[Bb]ond[ -_][Ll]ength'             |
        |                         |                                     |
        | CSA                     | '[Cc][Ss][Aa]'                      |
        |-------------------------|-------------------------------------|
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type`
            text = text + ", val=" + `val`
            text = text + ", err=" + `err`
            text = text + ", res_num=" + `res_num` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data type.
        elif data_type == None:
            raise RelaxNoneError, 'data type'
        elif type(data_type) != str:
            raise RelaxStrError, ('data type', data_type)

        # Value.
        elif val == None:
            raise RelaxNoneError, 'value'
        elif type(val) != float and type(val) != int:
            raise RelaxFloatError, ('value', val)

        # Error.
        elif err != None:
            if type(err) != float:
                raise RelaxNoneFloatError, ('error', err)

        # The residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        self.relax.generic.value.set(run=run, res_num=res_num, data_type=data_type, val=val, err=err)


    def set(self, run=None, values=None, print_flag=1):
        """Function for setting the initial parameter values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        values:  An array of numbers of length equal to the number of parameters in the model.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Examples
        ~~~~~~~~

        This command will set the parameter values of the run 'm2', which is the original
        model-free equation with parameters {S2, te}, before minimisation to the preselected values
        of this function.

        relax> set('m2')


        This command will do the same except the S2 and te values will be set to one and ten ps
        respectively.

        relax> set('m2', [1.0, 10 * 10e-12])
        relax> set(run='m2', values=[1.0, 10 * 10e-12])
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "set("
            text = text + "run=" + `run`
            text = text + ", values=" + `values`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Relax defined values.
        if values != None:
            if type(values) != list:
                raise RelaxListError, ('values', values)
            for i in xrange(len(values)):
                if type(values[i]) != float and type(values[i]) != int:
                    raise RelaxListIntError, ('values', values)

        # The print flag.
        if type(print_flag) != int:
            raise RelaxIntError, ('print_flag', print_flag)

        # Execute the functional code.
        self.relax.generic.minimise.set(run=run, values=values, print_flag=print_flag)


    def write(self):
        raise RelaxError, "Broken code."
