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

from LinearAlgebra import inverse
from Numeric import Float64, array, average, identity, matrixmultiply, zeros
from re import match, search


class Relax_fit:
    def __init__(self, relax):
        """Class containing functions for relaxation data."""

        self.relax = relax


    def assemble_param_vector(self, index=None, sim_index=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        param_vector = []

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][index]

        # Normal parameters.
        if sim_index == None:
            # Loop over the model parameters.
            for i in xrange(len(data.params)):
                # Relaxation rate.
                if data.params[i] == 'Rx':
                    if data.rx == None:
                        param_vector.append(0.0)
                    elif sim_index != None:
                        param_vector.append(data.rx_sim[sim_index])
                    else:
                        param_vector.append(data.rx)

                # Initial intensity.
                elif data.params[i] == 'I0':
                    if data.i0 == None:
                        param_vector.append(0.0)
                    elif sim_index != None:
                        param_vector.append(data.i0_sim[sim_index])
                    else:
                        param_vector.append(data.i0)

                # Intensity at infinity.
                elif data.params[i] == 'Iinf':
                    if data.iinf == None:
                        param_vector.append(0.0)
                    elif sim_index != None:
                        param_vector.append(data.iinf_sim[sim_index])
                    else:
                        param_vector.append(data.iinf)

        # Return a Numeric array.
        return array(param_vector, Float64)


    def assemble_scaling_matrix(self, index=None, scaling=1):
        """Function for creating the scaling matrix."""

        # Initialise.
        self.scaling_matrix = identity(len(self.param_vector), Float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][index]

        # Loop over the model-free parameters.
        for i in xrange(len(data.params)):
            # Relaxation rate.
            if data.params[i] == 'Rx':
                pass

            # Intensity scaling.
            elif search('^i', data.params[i]):
                # Find the position of the first time point.
                pos = data.relax_times.index(min(data.relax_times))

                # Scaling.
                self.scaling_matrix[i, i] = 1.0 / average(data.intensities[pos])

            # Increment i.
            i = i + 1


    def assign_function(self, run=None, i=None, intensity=None):
        """Function for assigning peak intensity data to either the reference or saturated spectra."""

        # Alias the residue specific data structure.
        data = self.relax.data.res[run][i]

        # Initialise.
        index = None
        if not hasattr(data, 'intensities'):
            data.intensities = []
            data.relax_times = []

        # Determine if the relaxation time already exists for the residue (duplicated spectra).
        for i in xrange(len(data.relax_times)):
            if self.relax_time == data.relax_times[i]:
                index = i

        # A new relaxation time has been encountered.
        if index == None:
            data.intensities.append([intensity])
            data.relax_times.append(self.relax_time)

        # Duplicated spectra.
        else:
            data.intensities[index].append(intensity)


    def data_init(self):
        """Function for initialising the data structures."""

        # Curve type.
        if not hasattr(self.relax.data, 'curve_type'):
            self.relax.data.curve_type = {}

        # Get the data names.
        data_names = self.data_names()

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Alias the residue specific data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Loop over the data structure names.
            for name in data_names:
                # Data structures which are initially empty arrays.
                list_data = [ 'params' ]
                if name in list_data:
                    init_data = []

                # Otherwise initialise the data structure to None.
                else:
                    init_data = None

                # If the name is not in 'data', add it.
                if not hasattr(data, name):
                    setattr(data, name, init_data)


    def data_names(self, set='all'):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        params:  An array of the model-free parameter names associated with the model.

        rx:  Either the R1 or R2 relaxation rate.

        i0:  The initial intensity.

        iinf:  The intensity at infinity.

        chi2:  Chi-squared value.

        iter:  Iterations.

        f_count:  Function count.

        g_count:  Gradient count.

        h_count:  Hessian count.

        warning:  Minimisation warning.
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('rx')
            names.append('i0')
            names.append('iinf')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        return names


    def grid_search(self, run, lower, upper, inc, constraints, print_flag, sim_index=None):
        """The grid search function."""

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(run=run, min_algor='grid', constraints=constraints, print_flag=print_flag, sim_index=sim_index)


    def grid_search_setup(self, index=None):
        """The grid search setup function."""

        # The length of the parameter array.
        n = len(self.param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if self.lower != None:
            if len(self.lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if self.upper != None:
            if len(self.upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(self.inc) == list:
            if len(self.inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = self.inc
        elif type(self.inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(self.inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        j = 0

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][index]

        # Loop over the model-free parameters.
        for i in xrange(len(data.params)):
            # Relaxation rate (from 0 to 20 s^-1).
            if data.params[i] == 'Rx':
                min_options.append([inc[j], 0.0, 20.0])

            # Intensity
            elif search('^I', data.params[i]):
                # Find the position of the first time point.
                pos = data.relax_times.index(min(data.relax_times))

                # Scaling.
                min_options.append([inc[j], 0.0, average(data.intensities[pos])])

            # Increment j.
            j = j + 1

        # Set the lower and upper bounds if these are supplied.
        if self.lower != None:
            for j in xrange(n):
                if self.lower[j] != None:
                    min_options[j][1] = self.lower[j]
        if self.upper != None:
            for j in xrange(n):
                if self.upper[j] != None:
                    min_options[j][2] = self.upper[j]

        # Test if the grid is too large.
        self.grid_size = 1
        for i in xrange(len(min_options)):
            self.grid_size = self.grid_size * min_options[i][0]
        if type(self.grid_size) == long:
            raise RelaxError, "A grid search of size " + `self.grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / self.scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / self.scaling_matrix[j, j]

        return min_options


    def linear_constraints(self, index=None):
        """Function for setting up the linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~

        The relaxation rate constraints are:

            Rx >= 0

        The intensity constraints are:

            I0 >= 0
            Iinf >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0 |     |  Rx  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |  .  |  I0  |  >=  |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     | Iinf |      |    0    |

        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, Float64)
        i = 0
        j = 0

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][index]

        # Loop over the model-free parameters.
        for k in xrange(len(data.params)):
            # Relaxation rate.
            if data.params[k] == 'Rx':
                # Rx >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Intensity parameter.
            elif search('^I', data.params[k]):
                # I0, Iinf >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Increment i.
            i = i + 1

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, print_flag=0, sim_index=None):
        """Relaxation curve fitting function."""

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Test if the sequence data for self.run is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Alias the residue specific data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Skip residues which have no data.
            if not hasattr(data, 'intensities') or not hasattr(data, 'relax_times'):
                continue

            # Create the initial parameter vector.
            self.param_vector = self.assemble_param_vector(index=i, sim_index=sim_index)

            # Diagonal scaling.
            self.assemble_scaling_matrix(index=i, scaling=scaling)
            self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_setup(index=i)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(index=i)

            # Print out.
            if self.print_flag >= 1:
                # Individual residue print out.
                if self.print_flag >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + `self.relax.data.res[self.run][i].num` + " " + self.relax.data.res[self.run][i].name
                print "\n\n" + string
                print len(string) * '~'

                # Grid search print out.
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `self.grid_size` + " (constraints may decrease this size).\n"

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Initialise the data structures for the model-free function.
            ave_intensities = []
            param_names = []
            param_values = []
            num_params = None

            # Loop over the time points.
            for j in xrange(len(data.relax_times)):
                pass


    def model_setup(self, model, params):
        """Function for updating various data structures dependant on the model selected."""

        # Set the model.
        self.relax.data.curve_type[self.run] = model

        # Initialise the data structures (if needed).
        self.data_init()

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # The parameter names.
            self.relax.data.res[self.run][i].params = params


    def read(self, run=None, file=None, dir=None, relax_time=0.0, format=None, heteronuc=None, proton=None, int_col=None):
        """Function for reading peak intensity data."""

        # Arguments.
        self.run = run
        self.relax_time = relax_time
        self.format = format
        self.heteronuc = heteronuc
        self.proton = proton
        self.int_col = int_col

        # Initialise the global data if necessary.
        self.data_init()

        # Generic intensity function.
        self.relax.generic.intensity.read(run=run, file=file, dir=dir, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col, assign_func=self.assign_function)


    def read_columnar_results(self, run, file_data):
        """Function for reading the results file."""

        # Arguments.
        self.run = run

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        col = {}
        for i in xrange(len(header)):
            if header[i] == 'Num':
                col['num'] = i
            elif header[i] == 'Name':
                col['name'] = i
            elif header[i] == 'Selected':
                col['select'] = i
            elif header[i] == 'Ref_intensity':
                col['ref_int'] = i
            elif header[i] == 'Ref_error':
                col['ref_err'] = i
            elif header[i] == 'Sat_intensity':
                col['sat_int'] = i
            elif header[i] == 'Sat_error':
                col['sat_err'] = i
            elif header[i] == 'NOE':
                col['noe'] = i
            elif header[i] == 'NOE_error':
                col['noe_err'] = i

        # Test the file.
        if len(col) < 2:
            raise RelaxInvalidDataError


        # Sequence.
        ###########

        # Generate the sequence.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Add the residue.
            self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(file_data[i][col['select']]))


        # Data.
        #######

        # Loop over the file data.
        for i in xrange(len(file_data)):
            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # Reassign data structure.
            data = self.relax.data.res[self.run][index]

            # Skip unselected residues.
            if not data.select:
                continue

            # Reference intensity.
            try:
                data.ref = float(file_data[i][col['ref_int']])
            except ValueError:
                data.ref = None

            # Reference error.
            try:
                data.ref_err = float(file_data[i][col['ref_err']])
            except ValueError:
                data.ref_err = None

            # Saturated intensity.
            try:
                data.sat = float(file_data[i][col['sat_int']])
            except ValueError:
                data.sat = None

            # Saturated error.
            try:
                data.sat_err = float(file_data[i][col['sat_err']])
            except ValueError:
                data.sat_err = None

            # NOE.
            try:
                data.noe = float(file_data[i][col['noe']])
            except ValueError:
                data.noe = None

            # NOE error.
            try:
                data.noe_err = float(file_data[i][col['noe_err']])
            except ValueError:
                data.noe_err = None


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0."""

        return 1.0


    def return_data_name(self, name):
        """
        Relaxation curve fitting data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | rate                   | rate         | '^[Rr]ate$'                                      |
        |________________________|______________|__________________________________________________|

        """

        # Rate.
        if match('^[Rr]ate$', name):
            return 'rate'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Rate.
        if object_name == 'rate':
            grace_string = 'Rate'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def return_value(self, run, i, data_type='noe'):
        """Function for returning the NOE value and error."""

        # Arguments.
        self.run = run

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][i]

        # Get the object.
        object_name = self.return_data_name(data_type)
        if not object_name:
            raise RelaxError, "The NOE calculation data type " + `data_type` + " does not exist."
        object_error = object_name + "_err"

        # Get the value.
        value = None
        if hasattr(data, object_name):
            value = getattr(data, object_name)

        # Get the error.
        error = None
        if hasattr(data, object_error):
            error = getattr(data, object_error)

        # Return the data.
        return value, error


    def select_model(self, run=None, model='exp'):
        """Function for selecting the model of the exponential curve."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'relax_fit'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'relax_fit':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Two parameter exponential fit.
        if model == 'exp':
            print "Two parameter exponential fit."
            params = ['Rx', 'I0']

        # Three parameter inversion recovery fit.
        elif model == 'inv':
            print "Three parameter inversion recovery fit."
            params = ['Rx', 'I0', 'Iinf']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(model, params)


    def set_error(self, run=None, error=0.0, spectrum_type=None, res_num=None, res_name=None):
        """Function for setting the errors."""

        # Arguments.
        self.run = run
        self.spectrum_type = spectrum_type
        self.res_num = res_num
        self.res_name = res_name

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the residue number is a valid regular expression.
        if type(res_num) == str:
            try:
                compile(res_num)
            except:
                raise RelaxRegExpError, ('residue number', res_num)

        # Test if the residue name is a valid regular expression.
        if res_name:
            try:
                compile(res_name)
            except:
                raise RelaxRegExpError, ('residue name', res_name)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Alias the residue specific data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # If 'res_num' is not None, skip the residue if there is no match.
            if type(res_num) == int and not data.num == res_num:
                continue
            elif type(res_num) == str and not match(res_num, `data.num`):
                continue

            # If 'res_name' is not None, skip the residue if there is no match.
            if res_name != None and not match(res_name, data.name):
                continue

            # Set the error.
            if self.spectrum_type == 'ref':
                data.ref_err = float(error)
            elif self.spectrum_type == 'sat':
                data.sat_err = float(error)


    def write(self, run=None, file=None, dir=None, force=0):
        """Function for writing NOE values and errors to a file."""

        # Arguments
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Open the file for writing.
        noe_file = self.relax.IO.open_write_file(file, dir, force)

        # Write the data.
        self.relax.generic.value.write_data(self.run, None, noe_file, return_value=self.return_value)

        # Close the file.
        noe_file.close()


    def write_columnar_line(self, file=None, num=None, name=None, select=None, ref_int=None, ref_err=None, sat_int=None, sat_err=None, noe=None, noe_err=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s " % select)
        if not select:
            file.write("\n")
            return

        # Reference and saturated data.
        file.write("%-25s %-25s " % (ref_int, ref_err))
        file.write("%-25s %-25s " % (sat_int, sat_err))

        # NOE and error.
        file.write("%-25s %-25s " % (noe, noe_err))

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Header.
        #########


        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', ref_int='Ref_intensity', ref_err='Ref_error', sat_int='Sat_intensity', sat_err='Sat_error', noe='NOE', noe_err='NOE_error')


        # Values.
        #########

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # Unselected residues.
            if not data.select:
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=0)
                continue

            # Reference intensity.
            ref_int = None
            if hasattr(data, 'ref'):
                ref_int = data.ref

            # Reference error.
            ref_err = None
            if hasattr(data, 'ref_err'):
                ref_err = data.ref_err

            # Saturated intensity.
            sat_int = None
            if hasattr(data, 'sat'):
                sat_int = data.sat

            # Saturated error.
            sat_err = None
            if hasattr(data, 'sat_err'):
                sat_err = data.sat_err

            # NOE
            noe = None
            if hasattr(data, 'noe'):
                noe = data.noe

            # NOE error.
            noe_err = None
            if hasattr(data, 'noe_err'):
                noe_err = data.noe_err

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, ref_int=ref_int, ref_err=ref_err, sat_int=sat_int, sat_err=sat_err, noe=noe, noe_err=noe_err)
