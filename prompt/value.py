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
from specific_fns.model_free import Model_free


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


    def set(self, run=None, value=None, data_type=None, res_num=None, force=0):
        """Function for setting residue specific data values.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        value:  The value(s).

        data_type:  A string specifying the data type to assign the value to.

        res_num:  The residue number.

        force:  A flag specifying whether to force the setting of values.


        Description
        ~~~~~~~~~~~

        Value argument.

        The value argument can be a single value, an array of values, or None, the choice of which
        determines the behaviour of this function.
        
        Single value:  If a single value is given, then the data_type argument must be supplied.
        All data types matching the data_type string will be given the supplied value.
        
        Array of values:  If an array of values is given, then the data_type argument must be None.
        The length of the array must equal the number of parameters in the model for a certain
        residue.  The parameters will be set to the values of the array.
        
        None:  If None is given as the value, then the data_type argument can be either None or a
        string.  If data_type is None then all residue specific data consisting of the parameters
        of the model-free model will be set to the hard wired values.  Otherwise if data_types is a
        string, then all data types matching that string will have their values set to the hard
        wired values.
        

        Data type argument.


        Residue number argument.

        If 'res_num' is set to the default of None, then all residues will have the value of
        'data_type' given by 'value', otherwise the single residue will be set to 'value'.


        The force flag.

        If this argument is set to the default of 0 and the data already has values, then an error
        is raised and the values are not changed.  Otherwise if set to 1, then the data values will
        be set even if data values already exist.


        Examples
        ~~~~~~~~

        To set the CSA value of all residues in the model-free run 'm1' to -170 ppm, type:

        relax> value.set('m1', -170 * 1e-6, 'csa')
        relax> value.set('m1', value=-170 * 1e-6, data_type='csa')

        To set the NH bond length of all residues in the model-free run 'm5' to 1.02 Angstroms,
        type:

        relax> value.set('m5', 1.02 * 1e-10, 'bond_length')
        relax> value.set('m5', value=1.02 * 1e-10, data_type='r')

        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "value.set("
            text = text + "run=" + `run`
            text = text + ", value=" + `value`
            text = text + ", data_type=" + `data_type`
            text = text + ", res_num=" + `res_num`
            text = text + ", force=" + `force` + ")"
            print text

        # The run name.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Value.
        if value != None and type(value) != list and type(value) != float and type(value) != int:
            raise RelaxNoneFloatListError, ('value', value)
        if type(value) == list:
            for i in len(value):
                if type(value[i]) != float and type(value[i]) != int:
                    raise RelaxListFloatError, ('value', value)

        # Data type.
        if data_type != None and type(data_type) != str:
            raise RelaxNoneStrError, ('data type', data_type)

        # If the value argument is a single value, make sure the data_type argument is set.
        if (type(value) == float or type(value) == int) and data_type == None:
            raise RelaxError, "When the value is a single number, the data_type argument must be set."
            
        # If the value argument is an array, make sure data_type is None.
        if type(value) == list and data_type != None:
            raise RelaxError, "When the value are given as an array, the data_type argument must be None."

        # The residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        self.relax.generic.value.set(run=run, value=value, data_type=data_type, res_num=res_num)


    def set_old(self, run=None, values=None, print_flag=1):
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


    # Modify the docstring of the set method to include the docstring of the model-free specific function get_data_name.
    ####################################################################################################################

    set.__doc__ = set.__doc__ + "\n" + Model_free.get_data_name.__doc__ + "\n"
