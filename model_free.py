from math import pi
from Numeric import Float64, array, ones, zeros
from re import match

from functions.mf import Mf
from minimise.generic import generic_minimise


class Model_free:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def create(self, model=None, equation=None, param_types=None, scaling=1):
        """Macro to create a model-free model.

        Arguments
        ~~~~~~~~~

        model:  The name of the model-free model.

        equation:  The model-free equation.

        param_type:  The parameters of the model.


        Description
        ~~~~~~~~~~~

        For selection of the model-free equation the string 'mf_orig' will select the original
        model-free equation while the string 'mf_ext' will select the extended model-free equation.

        The following parameters are accepted for the original model-free equation:
            S2:          The square of the generalised order parameter.
            te:          The effective correlation time.
        The following parameters are accepted for the extended model-free equation:
            S2f:         The square of the generalised order parameter of the faster motion.
            tf:          The effective correlation time of the faster motion.
            S2s:         The square of the generalised order parameter of the slower motion.
            ts:          The effective correlation time of the slower motion.
        The following parameters are accepted for both the original and extended equations:
            Rex:         The chemical exchange relaxation.
            Bond length: The average bond length <r>.
            CSA:         The chemical shift anisotropy.


        Examples
        ~~~~~~~~

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> mf_model_create('m1', 'mf_orig', ['S2'])
        relax> mf_model_create(model='m1', param_types=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2s', 'ts',
        'Rex', 'CSA', 'Bond length'.

        relax> mf_model_create('large_model', 'mf_ext', ['S2f', 'tf', 'S2s', 'ts', 'Rex', 'CSA',
                               'Bond length'])
        relax> mf_model_create(model='large_model', param_types=['S2f', 'tf', 'S2s', 'ts', 'Rex',
                               'CSA', 'Bond length'], equation='mf_ext')
        """

        if not model or type(model) != str:
            print "Model-free model name is invalid."
            return
        elif not equation:
            print "Model-free equation type not selected."
            return
        elif not param_types:
            print "Model-free parameters not given."
            return
        elif not equation == 'mf_orig' and not equation == 'mf_ext':
            print "Model-free equation '" + equation + "' is not supported."
            return

        # Test if sequence data is loaded.
        if not len(self.relax.data.seq):
            print "Sequence data has to be loaded first."
            return

        # Arguments
        self.model = model
        self.equation = equation
        self.types = param_types

        # Test the scaling flag.
        if scaling == 0 or scaling == 1:
            self.scaling = scaling
        else:
            print "The scaling flag is set incorrectly."
            return

        # Test the parameter names.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in range(len(self.types)):
            # Check if the parameter is a string.
            if type(self.types[i]) != str:
                print "The parameter " + `self.types[i]` + " is not a string."
                return

            # Test the parameter.
            invalid_param = 0
            if self.types[i] == 'S2':
                if self.equation == 'mf_ext' or s2:
                    invalid_param = 1
                s2 = 1
            elif self.types[i] == 'te':
                if self.equation == 'mf_ext' or te:
                    invalid_param = 1
                s2_flag = 0
                for j in range(len(self.types)):
                    if self.types[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1
                te = 1
            elif self.types[i] == 'S2f':
                if self.equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1
            elif self.types[i] == 'tf':
                if self.equation == 'mf_orig' or tf:
                    invalid_param = 1
                s2f_flag = 0
                for j in range(len(self.types)):
                    if self.types[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1
                tf = 1
            elif self.types[i] == 'S2s':
                if self.equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1
            elif self.types[i] == 'ts':
                if self.equation == 'mf_orig' or ts:
                    invalid_param = 1
                s2s_flag = 0
                for j in range(len(self.types)):
                    if self.types[j] == 'S2s':
                        s2s_flag = 1
                if not s2s_flag:
                    invalid_param = 1
                ts = 1
            elif self.types[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1
            elif self.types[i] == 'Bond length':
                if r:
                    invalid_param = 1
                r = 1
            elif self.types[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1
            else:
                print "The parameter " + self.types[i] + " is not supported."
                return

            # The invalid parameter flag is set.
            if invalid_param:
                print "The parameter array " + `self.types` + " contains an invalid parameter or combination of parameters."
                return

        # Create the scaling vector.
        self.scaling_vector()

        # Update the data structures.
        self.data_update()


    def data_update(self):
        """Function for updating various data structures depending on the model selected."""

        # Update the equation and param_types data structures.
        try:
            self.relax.data.equations
        except AttributeError:
            self.relax.data.equations = {}
        try:
            self.relax.data.params
        except AttributeError:
            self.relax.data.params = {}
        try:
            self.relax.data.param_types
        except AttributeError:
            self.relax.data.param_types = {}
        try:
            self.relax.data.param_errors
        except AttributeError:
            self.relax.data.param_errors = {}
        try:
            self.relax.data.scaling
        except AttributeError:
            self.relax.data.scaling = {}
        try:
            self.relax.data.min_results
        except AttributeError:
            self.relax.data.min_results = {}

        self.relax.data.equations[self.model] = self.equation
        self.relax.data.param_types[self.model] = self.types

        # Create the params data structure.
        self.relax.data.params[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)
        self.relax.data.param_errors[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)

        # Diagonal scaling.
        if self.scaling:
            self.relax.data.scaling[self.model] = zeros((len(self.relax.data.seq), len(self.types)), Float64)
            self.relax.data.scaling[self.model][:] = self.scale_vect

        # Minimisation results.
        self.relax.data.min_results[self.model] = zeros((len(self.relax.data.seq), 5), Float64)


    def fixed_setup(self, min_options=None, model=None):
        """The fixed parameter value setup function."""

        # The original model-free equations.
        if match('mf_orig', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2.
                if match('S2', self.relax.data.param_types[model][i]):
                    min_options[i] = 0.5

                # te.
                elif match('te', self.relax.data.param_types[model][i]):
                    min_options[i] = 100.0 * 1e-12

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    min_options[i] = 0.0

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    min_options[i] = 1.02 * 1e-10

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    min_options[i] = -170 * 1e-6

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the original model-free equation."
                    return min_options

        # The extended model-free equations.
        elif match('mf_ext', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2f.
                if match('S2f', self.relax.data.param_types[model][i]):
                    min_options[i] = 0.5

                # tf.
                elif match('tf', self.relax.data.param_types[model][i]):
                    min_options[i] = 10.0 * 1e-12

                # S2s.
                elif match('S2s', self.relax.data.param_types[model][i]):
                    min_options[i] = 0.5

                # ts.
                elif match('ts', self.relax.data.param_types[model][i]):
                    min_options[i] = 1000.0 * 1e-12

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    min_options[i] = 0.0

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    min_options[i] = 1.02 * 1e-10

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    min_options[i] = -170 * 1e-6

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the extended model-free equation."
                    return min_options

        return min_options


    def grid_setup(self, model=None, inc_vector=None):
        """The grid search setup function."""

        # Setup the grid options.
        min_options = []

        # The original model-free equations.
        if match('mf_orig', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2.
                if match('S2', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 1.0])

                # te.
                elif match('te', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 10000.0 * 1e-12])

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2])

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 1.0 * 1e-10, 1.05 * 1e-10])

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], -120 * 1e-6, -200 * 1e-6])

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the original model-free equation."
                    return min_options

        # The extended model-free equations.
        elif match('mf_ext', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2f.
                if match('S2f', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 1.0])

                # tf.
                elif match('tf', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 10000.0 * 1e-12])

                # S2f.
                elif match('S2s', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 1.0])

                # tf.
                elif match('ts', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 10000.0 * 1e-12])

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 0.0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2])

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], 1.0 * 1e-10, 1.1 * 1e-10])

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    min_options.append([inc_vector[i], -120 * 1e-6, -200 * 1e-6])

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the extended model-free equation."
                    return min_options

        return min_options


    def linear_constraints(self, model=None):
        """Function for setting up the model-free linear constraint matrices A and b."""

        # Initialisation.
        A = []
        b = []
        types = self.relax.data.param_types[model]
        n = len(types)
        zero_array = zeros(n, Float64)
        j = 0

        # The original model-free equations.
        for i in range(n):
            # S2, S2f, and S2s (0 <= S2 <= 1).
            if match("S2", types[i]):
                # S2 >= 0
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

                # -S2 >= -1
                A.append(zero_array * 0.0)
                A[j][i] = -1.0
                b.append(-1.0)
                j = j + 1

            # te, tf, and ts (te >= 0).
            elif match("t[efs]", types[i]):
                if match("ts", types[i]):
                    A.append(zero_array * 0.0)

                    # Find the index of tf if the parameter exists.
                    index = None
                    for k in range(n):
                        if match("tf", types[k]):
                            index = k

                    # Dual correlation times (tf <= ts) or (ts - tf >= 0).
                    if index != None:
                        A[j][index] = -1.0

                    A[j][i] = 1.0
                    b.append(0.0)
                    j = j + 1
                else:
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    b.append(0.0)
                    j = j + 1

            # Rex (Rex >= 0).
            elif match("Rex", types[i]):
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Bond length (0.9e-10 <= r <= 2e-10)
            elif match("Bond length", types[i]):
                # r >= 0.9e-10
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.9e-10)
                j = j + 1

                # -r >= -2e-10
                A.append(zero_array * 0.0)
                A[j][i] = -1.0
                b.append(-2e-10)
                j = j + 1

            # CSA (-300e-6 <= CSA <= -100e-6).
            elif match("CSA", types[i]):
                # CSA >= -300e-6
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(-300e-6)
                j = j + 1

                # -CSA >= 100e-6
                A.append(zero_array * 0.0)
                A[j][i] = -1.0
                b.append(100e-6)
                j = j + 1

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def main_loop(self, model=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, print_flag=0):
        """The main iterative minimisation loop."""

        # Linear constraints.
        if constraints:
            constraint_function = self.relax.specific_setup.setup("linear_constraints", model)
            if constraint_function == None:
                return
            A, b = constraint_function(model)

        # Loop over the residues.
        for self.res in range(len(self.relax.data.seq)):
            if print_flag >= 1:
                if print_flag >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + `self.relax.data.seq[self.res][0]` + " " + self.relax.data.seq[self.res][1]
                print string
                string2 = ""
                for i in range(len(string)):
                    string2 = string2 + "~"
                print string2

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Diagonal scaling.
            scaling_vector = None
            if self.relax.data.scaling.has_key(model):
                scaling_vector = self.relax.data.scaling[model][self.res]

            # If any data is missing jump to the next residue.
            data = zeros(self.relax.data.num_ri, Float64)
            errors = zeros(self.relax.data.num_ri, Float64)
            for i in range(self.relax.data.num_ri):
                if self.relax.data.relax_data[i][self.res, 2] == 0.0:
                    continue
                data[i] = self.relax.data.relax_data[i][self.res, 0]
                errors[i] = self.relax.data.relax_data[i][self.res, 1]
            self.function_ops = ()

            # Initialise the functions used in the minimisation.
            self.mf = Mf(self.relax, equation=self.relax.data.equations[model], param_types=self.relax.data.param_types[model], init_params=self.relax.data.params[model][self.res], relax_data=data, errors=errors, bond_length=self.relax.data.bond_length[self.res][0], csa=self.relax.data.csa[self.res][0], diff_type=self.relax.data.diff_type, diff_params=self.relax.data.diff_params, scaling_vector=scaling_vector)

            # Levenberg-Marquardt minimisation.
            if match('[Ll][Mm]$', min_algor) or match('[Ll]evenburg-[Mm]arquardt$', min_algor):
                min_options = min_options + (self.mf.lm_dri, errors)
            # Levenberg-Marquardt minimisation with constraints.
            elif constraints == 1 and (match('[Ll][Mm]$', min_options[0]) or match('[Ll]evenburg-[Mm]arquardt$', min_options[0])):
                min_options = min_options + (self.mf.lm_dri, errors)

            # Minimisation.
            if constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=self.relax.data.params[model][self.res], min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=self.relax.data.params[model][self.res], min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
            if results == None:
                return
            self.params, self.func, iter, fc, gc, hc, self.warning = results
            self.iter_count = self.iter_count + iter
            self.f_count = self.f_count + fc
            self.g_count = self.g_count + gc
            self.h_count = self.h_count + hc

            # Place the results in various data structures.
            self.relax.data.params[model][self.res] = self.params
            self.relax.data.min_results[model][self.res] = [self.func, self.iter_count, self.f_count, self.g_count, self.h_count]


    def map_bounds(self, model=None):
        """The function for creating bounds for the mapping function."""

        # Bounds array.
        bounds = zeros((len(self.relax.data.param_types[model]), 2), Float64)

        # The original model-free equations.
        if match('mf_orig', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2.
                if match('S2', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1]

                # te.
                elif match('te', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1e-8]

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2]

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    bounds[i] = [-100 * 1e-6, -300 * 1e-6]

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the original model-free equation."
                    return bounds

        # The extended model-free equations.
        elif match('mf_ext', self.relax.data.equations[model]):
            for i in range(len(self.relax.data.param_types[model])):
                # S2f.
                if match('S2f', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1]

                # tf.
                elif match('tf', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1e-8]

                # S2s.
                elif match('S2s', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1]

                # ts.
                elif match('ts', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 1e-8]

                # Rex.
                elif match('Rex', self.relax.data.param_types[model][i]):
                    bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2]

                # Bond length.
                elif match('Bond length', self.relax.data.param_types[model][i]):
                    bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

                # CSA.
                elif match('CSA', self.relax.data.param_types[model][i]):
                    bounds[i] = [-100 * 1e-6, -300 * 1e-6]

                # Unknown parameter.
                else:
                    print "Unknown parameter '" + self.relax.data.param_types[model][i] + "' for the extended model-free equation."
                    return bounds

        return bounds


    def map_labels(self, model, bounds, swap, inc):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        types = self.relax.data.param_types[model]
        n = len(types)
        axis_incs = 5.0
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in range(n):
            # S2, S2f, and S2s.
            if match("S2", types[swap[i]]):
                # Labels.
                labels = labels + "\"" + types[swap[i]] + "\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1.0
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1.0

            # te, tf, and ts.
            elif match("t[efs]", types[i]):
                # Labels.
                labels = labels + "\"" + types[swap[i]] + " (ps)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e12
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e12

            # Rex.
            elif match("Rex", types[i]):
                # Labels.
                labels = labels + "\"Rex (" + self.relax.data.frq_labels[0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.frq[0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.frq[0])**2

            # Bond length.
            elif match("Bond length", types[i]):
                # Labels.
                labels = labels + "\"" + types[swap[i]] + " (A)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-10
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-10

            # CSA.
            elif match("CSA", types[i]):
                # Labels.
                labels = labels + "\"" + types[swap[i]] + " (ppm)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-6
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-6

            if i < n - 1:
                labels = labels + " "
            else:
                labels = labels + "}"

            # Tick locations.
            string = "{"
            val = 0.0
            for j in range(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc 
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in range(axis_incs + 1):
                if self.relax.data.scaling.has_key(model):
                    string = string + "\"" + "%.2f" % (vals * self.relax.data.scaling[model][0][swap[i]]) + "\" "
                else:
                    string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def print_header(self, file, model):
        """Function for printing the header of the results file."""

        # Initialise.
        types = self.relax.data.param_types[model]

        # Residue number and name.
        file.write("%-5s" % "Num")
        file.write("%-6s" % "Name")

        # Parameters.
        for i in range(len(types)):
            # S2, S2f, and S2s.
            if match("S2", types[i]):
                file.write("%-26s" % types[i])

            # te, tf, and ts.
            elif match("t[efs]", types[i]):
                file.write("%-26s" % (types[i] + " (ps)"))

            # Rex.
            elif match("Rex", types[i]):
                file.write("%-26s" % ("Rex (" + self.relax.data.frq_labels[0] + " MHz)"))

            # Bond length.
            elif match("Bond length", types[i]):
                file.write("%-26s" % (types[i] + " (A)"))

            # CSA.
            elif match("CSA", types[i]):
                file.write("%-26s" % (types[i] + " (ppm)"))

        # Minimisation results.
        file.write("%-26s" % "chi-squared")
        file.write("%-9s" % "iter")
        file.write("%-9s" % "f")
        file.write("%-9s" % "g")
        file.write("%-9s" % "h")
        file.write("%-30s\n" % "warning")


    def print_results(self, file, model):
        """Function for printing the core of the results file."""

        # Initialise.
        types = self.relax.data.param_types[model]

        # Loop over the residues.
        for i in range(len(self.relax.data.seq)):
            # Initialise.
            if self.relax.data.scaling.has_key(model):
                params = self.relax.data.params[model][i] * self.relax.data.scaling[model][i]
            else:
                params = self.relax.data.params[model][i]

            # Residue number and name.
            file.write("%-5s" % self.relax.data.seq[i][0])
            file.write("%-6s" % self.relax.data.seq[i][1])

            # Parameters.
            for j in range(len(types)):
                # S2, S2f, and S2s.
                if match("S2", types[j]):
                    file.write("%-26s" % `params[j]`)

                # te, tf, and ts.
                elif match("t[efs]", types[j]):
                    file.write("%-26s" % `(params[j] / 1e-12)`)

                # Rex.
                elif match("Rex", types[j]):
                    file.write("%-26s" % `params[j] * (2.0 * pi * self.relax.data.frq[0])**2`)

                # Bond length.
                elif match("Bond length", types[j]):
                    file.write("%-26s" % `(params[j] / 1e-10)`)

                # CSA.
                elif match("CSA", types[j]):
                    file.write("%-26s" % `(params[j] / 1e-6)`)

            # Minimisation results.
            file.write("%-26s" % `self.relax.data.min_results[model][i][0]`)
            file.write("%-9i" % self.relax.data.min_results[model][i][1])
            file.write("%-9i" % self.relax.data.min_results[model][i][2])
            file.write("%-9i" % self.relax.data.min_results[model][i][3])
            file.write("%-9i" % self.relax.data.min_results[model][i][4])
            #if self.warning:
            #    file.write("%-30s\n" % `self.warning`)

            # End of line
            file.write("\n")


    def scaling_vector(self):
        """Function for creating the scaling vector."""

        self.scale_vect = ones(len(self.types), Float64)
        for i in range(len(self.types)):
            # te, tf, and ts.
            if match('t', self.types[i]):
                self.scale_vect[i] = 1e-9
            elif self.types[i] == 'Rex':
                self.scale_vect[i] = 1.0 / (2.0 * pi * self.relax.data.frq[0]) ** 2
            elif self.types[i] == 'Bond length':
                self.scale_vect[i] = 1e-10
            elif self.types[i] == 'CSA':
                self.scale_vect[i] = 1e-4



    def select(self, model, scaling=1):
        """Macro for the selection of a preset model-free model.

        Arguments
        ~~~~~~~~~

        model:   The name of the preset model.
        scaling: The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        The preset model-free models are:
            'm0'    => []
            'm1'    => [S2]
            'm2'    => [S2, te]
            'm3'    => [S2, Rex]
            'm4'    => [S2, te, Rex]
            'm5'    => [S2f, S2s, ts]
            'm6'    => [S2f, tf, S2s, ts]
            'm7'    => [S2f, S2s, ts, Rex]
            'm8'    => [S2f, tf, S2s, ts, Rex]
            'm9'    => [Rex]

            'm10'    => [CSA]
            'm11'    => [CSA, S2]
            'm12'    => [CSA, S2, te]
            'm13'    => [CSA, S2, Rex]
            'm14'    => [CSA, S2, te, Rex]
            'm15'    => [CSA, S2f, S2s, ts]
            'm16'    => [CSA, S2f, tf, S2s, ts]
            'm17'    => [CSA, S2f, S2s, ts, Rex]
            'm18'    => [CSA, S2f, tf, S2s, ts, Rex]
            'm19'    => [CSA, Rex]

            'm20'    => [Bond length]
            'm21'    => [Bond length, S2]
            'm22'    => [Bond length, S2, te]
            'm23'    => [Bond length, S2, Rex]
            'm24'    => [Bond length, S2, te, Rex]
            'm25'    => [Bond length, S2f, S2s, ts]
            'm26'    => [Bond length, S2f, tf, S2s, ts]
            'm27'    => [Bond length, S2f, S2s, ts, Rex]
            'm28'    => [Bond length, S2f, tf, S2s, ts, Rex]
            'm29'    => [Bond length, CSA, Rex]

            'm30'    => [Bond length, CSA]
            'm31'    => [Bond length, CSA, S2]
            'm32'    => [Bond length, CSA, S2, te]
            'm33'    => [Bond length, CSA, S2, Rex]
            'm34'    => [Bond length, CSA, S2, te, Rex]
            'm35'    => [Bond length, CSA, S2f, S2s, ts]
            'm36'    => [Bond length, CSA, S2f, tf, S2s, ts]
            'm37'    => [Bond length, CSA, S2f, S2s, ts, Rex]
            'm38'    => [Bond length, CSA, S2f, tf, S2s, ts, Rex]
            'm39'    => [Bond length, CSA, Rex]

        Warning:  A few of the models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.


        Diagonal scaling.

        This is the scaling of parameter values with the intent of having the same order of
        magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
        Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18]
        (Rex is divided by (2*pi*600,000,000)**2 to make it field strength independent).  The
        scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 2.0, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.  The reason for diagonal scaling is that certain minimisation
        techniques fail when the model is not properly scaled.


        Examples
        ~~~~~~~~

        To pick model 'm1', run:

        relax> mf_model_select('m1')
        """

        # Arguments.
        self.model = model

        # Test if sequence data is loaded.
        if not len(self.relax.data.seq):
            print "Sequence data has to be loaded first."
            return

        # Test if the model already exists.
        try:
            self.relax.data.equations
        except AttributeError:
            pass
        else:
            print "Models have already been set."
            return

        # Test the scaling flag.
        if scaling == 0 or scaling == 1:
            self.scaling = scaling
        else:
            print "The scaling flag is set incorrectly."
            return

        # Block 1.
        if model == 'm0':
            self.equation = 'mf_orig'
            self.types = []
        elif model == 'm1':
            self.equation = 'mf_orig'
            self.types = ['S2']
        elif model == 'm2':
            self.equation = 'mf_orig'
            self.types = ['S2', 'te']
        elif model == 'm3':
            self.equation = 'mf_orig'
            self.types = ['S2', 'Rex']
        elif model == 'm4':
            self.equation = 'mf_orig'
            self.types = ['S2', 'te', 'Rex']
        elif model == 'm5':
            self.equation = 'mf_ext'
            self.types = ['S2f', 'S2s', 'ts']
        elif model == 'm6':
            self.equation = 'mf_ext'
            self.types = ['S2f', 'tf', 'S2s', 'ts']
        elif model == 'm7':
            self.equation = 'mf_ext'
            self.types = ['S2f', 'S2s', 'ts', 'Rex']
        elif model == 'm8':
            self.equation = 'mf_ext'
            self.types = ['S2f', 'tf', 'S2s', 'ts', 'Rex']
        elif model == 'm9':
            self.equation = 'mf_orig'
            self.types = ['Rex']

        # Block 2.
        elif model == 'm10':
            self.equation = 'mf_orig'
            self.types = ['CSA']
        elif model == 'm11':
            self.equation = 'mf_orig'
            self.types = ['CSA', 'S2']
        elif model == 'm12':
            self.equation = 'mf_orig'
            self.types = ['CSA', 'S2', 'te']
        elif model == 'm13':
            self.equation = 'mf_orig'
            self.types = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            self.equation = 'mf_orig'
            self.types = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            self.equation = 'mf_ext'
            self.types = ['CSA', 'S2f', 'S2s', 'ts']
        elif model == 'm16':
            self.equation = 'mf_ext'
            self.types = ['CSA', 'S2f', 'tf', 'S2s', 'ts']
        elif model == 'm17':
            self.equation = 'mf_ext'
            self.types = ['CSA', 'S2f', 'S2s', 'ts', 'Rex']
        elif model == 'm18':
            self.equation = 'mf_ext'
            self.types = ['CSA', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
        elif model == 'm19':
            self.equation = 'mf_orig'
            self.types = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            self.equation = 'mf_orig'
            self.types = ['Bond length']
        elif model == 'm21':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'S2']
        elif model == 'm22':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'S2', 'te']
        elif model == 'm23':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'S2', 'Rex']
        elif model == 'm24':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'S2', 'te', 'Rex']
        elif model == 'm25':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'S2f', 'S2s', 'ts']
        elif model == 'm26':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'S2f', 'tf', 'S2s', 'ts']
        elif model == 'm27':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'S2f', 'S2s', 'ts', 'Rex']
        elif model == 'm28':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
        elif model == 'm29':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'Rex']

        # Block 4.
        elif model == 'm30':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA']
        elif model == 'm31':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA', 'S2']
        elif model == 'm32':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA', 'S2', 'te']
        elif model == 'm33':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'CSA', 'S2f', 'S2s', 'ts']
        elif model == 'm36':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'CSA', 'S2f', 'tf', 'S2s', 'ts']
        elif model == 'm37':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'CSA', 'S2f', 'S2s', 'ts', 'Rex']
        elif model == 'm38':
            self.equation = 'mf_ext'
            self.types = ['Bond length', 'CSA', 'S2f', 'tf', 'S2s', 'ts', 'Rex']
        elif model == 'm39':
            self.equation = 'mf_orig'
            self.types = ['Bond length', 'CSA', 'Rex']

        # Invalid models.
        else:
            print "The model '" + model + "' is invalid."
            return

        # Create the scaling vector.
        self.scaling_vector()

        # Update the data structures.
        self.data_update()
