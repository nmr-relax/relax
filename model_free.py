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


from math import pi
from Numeric import Float64, array, ones, zeros
from re import match
from string import replace

from functions.mf import Mf
from minimise.generic import generic_minimise


class Model_free:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def create(self, model=None, equation=None, param_types=None, scaling=1):
        """Function to create a model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.seq):
            print "Sequence data has to be loaded first."
            return

        # Arguments
        equation = equation
        param_types = param_types

        # Test the scaling flag.
        if scaling == 0 or scaling == 1:
            self.scaling = scaling
        else:
            print "The scaling flag is set incorrectly."
            return

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in range(len(param_types)):
            # Check if the parameter is a string.
            if type(param_types[i]) != str:
                print "The parameter " + `param_types[i]` + " is not a string."
                return

            # Invalid parameter flag.
            invalid_param = 0

            # S2.
            if param_types[i] == 'S2':
                # Does the array contain more than one instance of S2.
                if s2:
                    invalid_param = 1
                s2 = 1

                # Does the array contain S2s.
                s2s_flag = 0
                for j in range(len(param_types)):
                    if param_types[j] == 'S2s':
                        s2s_flag = 1
                if s2s_flag:
                    invalid_param = 1

            # te.
            elif param_types[i] == 'te':
                # Does the array contain more than one instance of te and has the extended model-free formula been selected.
                if equation == 'mf_ext' or te:
                    invalid_param = 1
                te = 1

                # Does the array contain the parameter S2.
                s2_flag = 0
                for j in range(len(param_types)):
                    if param_types[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1

            # S2f.
            elif param_types[i] == 'S2f':
                # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1

            # S2s.
            elif param_types[i] == 'S2s':
                # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1

            # tf.
            elif param_types[i] == 'tf':
                # Does the array contain more than one instance of tf and has the original model-free formula been selected.
                if equation == 'mf_orig' or tf:
                    invalid_param = 1
                tf = 1

                # Does the array contain the parameter S2f.
                s2f_flag = 0
                for j in range(len(param_types)):
                    if param_types[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1

            # ts.
            elif param_types[i] == 'ts':
                # Does the array contain more than one instance of ts and has the original model-free formula been selected.
                if equation == 'mf_orig' or ts:
                    invalid_param = 1
                ts = 1

                # Does the array contain the parameter S2 or S2s.
                flag = 0
                for j in range(len(param_types)):
                    if param_types[j] == 'S2' or param_types[j] == 'S2f':
                        flag = 1
                if not flag:
                    invalid_param = 1

            # Rex.
            elif param_types[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1

            # Bond length.
            elif param_types[i] == 'r':
                if r:
                    invalid_param = 1
                r = 1

            # CSA.
            elif param_types[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1

            # Unknown parameter.
            else:
                print "The parameter " + param_types[i] + " is not supported."
                return

            # The invalid parameter flag is set.
            if invalid_param:
                print "The parameter array " + `param_types` + " contains an invalid parameter or combination of parameters."
                return

        # Create the scaling vector.
        self.scaling_vector(param_types)

        # Update the data structures.
        self.data_update(model, equation, param_types)


    def data_update(self, model, equation, param_types):
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

        self.relax.data.equations[model] = []
        self.relax.data.param_types[model] = []
        for i in range(len(self.relax.data.seq)):
            self.relax.data.equations[model].append(equation)
            self.relax.data.param_types[model].append(param_types)

        # Create the params data structure.
        self.relax.data.params[model] = zeros((len(self.relax.data.seq), len(param_types)), Float64)
        self.relax.data.param_errors[model] = zeros((len(self.relax.data.seq), len(param_types)), Float64)

        # Diagonal scaling.
        if self.scaling:
            self.relax.data.scaling[model] = zeros((len(self.relax.data.seq), len(param_types)), Float64)
            self.relax.data.scaling[model][:] = self.scale_vect

        # Minimisation results.
        self.relax.data.min_results[model] = []
        for i in range(len(self.relax.data.seq)):
            self.relax.data.min_results[model].append([0.0, 0, 0, 0, 0, None])


    def fixed_setup(self, param_types=None, min_options=None):
        """The fixed parameter value setup function."""

        for i in range(len(param_types)):
            # {S2, S2f, S2s}.
            if match('S2', param_types[i]):
                min_options[i] = 0.5

            # {te, tf, ts}.
            elif match('t', param_types[i]):
                if param_types[i] == 'tf':
                    min_options[i] = 10.0 * 1e-12
                elif param_types[i] == 'ts':
                    min_options[i] = 1000.0 * 1e-12
                else:
                    min_options[i] = 100.0 * 1e-12

            # Rex.
            if param_types[i] == 'Rex':
                min_options[i] = 0.0

            # Bond length.
            if param_types[i] == 'r':
                min_options[i] = 1.02 * 1e-10

            # CSA.
            if param_types[i] == 'CSA':
                min_options[i] = -170 * 1e-6

        return min_options


    def grid_setup(self, param_types=None, inc_vector=None):
        """The grid search setup function."""

        # Initialise.
        min_options = []

        for i in range(len(param_types)):
            # {S2, S2f, S2s}.
            if match('S2', param_types[i]):
                min_options.append([inc_vector[i], 0.0, 1.0])

            # {te, tf, ts}.
            elif match('t', param_types[i]):
                min_options.append([inc_vector[i], 0.0, 10000.0 * 1e-12])

            # Rex.
            elif param_types[i] == 'Rex':
                min_options.append([inc_vector[i], 0.0, 10.0 / (2.0 * pi * self.relax.data.frq[0])**2])

            # Bond length.
            elif param_types[i] == 'r':
                min_options.append([inc_vector[i], 1.0 * 1e-10, 1.05 * 1e-10])

            # CSA.
            elif param_types[i] == 'CSA':
                min_options.append([inc_vector[i], -120 * 1e-6, -200 * 1e-6])

        return min_options


    def linear_constraints(self, model=None, param_types=None):
        """Function for setting up the model-free linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~
        The order parameter constraints are:

            0 <= S2 <= 1
            0 <= S2f <= 1
            0 <= S2s <= 1

        By substituting the formula S2 = S2f.S2s into the above inequalities, the additional two
        inequalities can be derived:

            S2 <= S2f
            S2 <= S2s

        Correlation time constraints are:

            te >= 0
            tf >= 0
            ts >= 0

            tf <= ts

        Additional constraints used include:

            Rex >= 0
            0.9e-10 <= r <= 2e-10
            -300e-6 <= CSA <= 0


        Rearranged notation
        ~~~~~~~~~~~~~~~~~~~
        The above ineqality constraints can be rearranged into:

            S2 >= 0
            -S2 >= -1
            S2f >= 0
            -S2f >= -1
            S2s >= 0
            -S2s >= -1
            S2f - S2 >= 0
            S2s - S2 >= 0
            te >= 0
            tf >= 0
            ts >= 0
            ts - tf >= 0
            Rex >= 0
            r >= 0.9e-10
            -r >= -2e-10
            CSA >= -300e-6
            -CSA >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~
        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            |-1  0  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  1  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            | 0 -1  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  0  1  0  0  0  0  0  0 |     | S2  |      |    0    |
            |                           |     |     |      |         |
            | 0  0 -1  0  0  0  0  0  0 |     | S2f |      |   -1    |
            |                           |     |     |      |         |
            |-1  1  0  0  0  0  0  0  0 |     | S2s |      |    0    |
            |                           |     |     |      |         |
            |-1  0  1  0  0  0  0  0  0 |     | te  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  1  0  0  0  0  0 |  .  | tf  |  >=  |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  1  0  0  0  0 |     | ts  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  1  0  0  0 |     | Rex |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0 -1  1  0  0  0 |     |  r  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  0  1  0  0 |     | CSA |      |    0    |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  1  0 |                  | 0.9e-10 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0 -1  0 |                  | -2e-10  |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0  1 |                  | -300e-6 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0 -1 |                  |    0    |

        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(param_types)
        zero_array = zeros(n, Float64)
        j = 0

        # The original model-free equations.
        for i in range(n):
            # Order parameters {S2, S2f, S2s}.
            if match('S2', param_types[i]):
                # 0 <= S2 <= 1.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0)
                b.append(-1.0)
                j = j + 2

                # S2 <= S2f and S2 <= S2s.
                if param_types[i] == 'S2':
                    for k in range(n):
                        if param_types[k] == 'S2f' or param_types[k] == 'S2s':
                            A.append(zero_array * 0.0)
                            A[j][i] = -1.0
                            A[j][k] = 1.0
                            b.append(0.0)
                            j = j + 1

            # Correlation times {tm, te, tf, ts}.
            elif match('t', param_types[i]):
                # te >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

                # tf <= ts.
                if param_types[i] == 'ts':
                    for k in range(n):
                        if param_types[k] == 'tf':
                            A.append(zero_array * 0.0)
                            A[j][i] = 1.0
                            A[j][k] = -1.0
                            b.append(0.0)
                            j = j + 1

            # Rex.
            elif param_types[i] == 'Rex':
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Bond length.
            elif match('r', param_types[i]):
                # 0.9e-10 <= r <= 2e-10.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                if self.relax.data.scaling.has_key(model):
                    b.append(0.9e-10 / self.relax.data.scaling[model][0][i])
                    b.append(-2e-10 / self.relax.data.scaling[model][0][i])
                else:
                    b.append(0.9e-10)
                    b.append(-2e-10)
                j = j + 2

            # CSA.
            elif match('CSA', param_types[i]):
                # -300e-6 <= CSA <= 0.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                if self.relax.data.scaling.has_key(model):
                    b.append(-300e-6 / self.relax.data.scaling[model][0][i])
                else:
                    b.append(-300e-6)
                b.append(0.0)
                j = j + 2

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def macro_create(self, model=None, equation=None, param_types=None, scaling=1):
        """Macro to create a model-free model.

        Arguments
        ~~~~~~~~~

        model:  The name of the model-free model.

        equation:  The model-free equation.

        param_types:  The parameters of the model.

        scaling:  The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        The model-free model name can be any string.


        Model-free equation.

        'mf_orig' selects the original model-free equations with parameters {S2, te}.
        'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
        'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.


        Model-free parameters.

        The following parameters are accepted for the original model-free equation:
            S2:     The square of the generalised order parameter.
            te:     The effective correlation time.
        The following parameters are accepted for the extended model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2:     The square of the generalised order parameter S2 = S2f*S2s.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for the extended 2 model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2s:    The square of the generalised order parameter of the slower motion.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for all equations:
            Rex:    The chemical exchange relaxation.
            r:      The average bond length <r>.
            CSA:    The chemical shift anisotropy.


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

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> model.create_mf('m1', 'mf_orig', ['S2'])
        relax> model.create_mf(model='m1', param_types=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2', 'ts',
        'Rex', 'CSA', 'r'.

        relax> model.create_mf('large_model', 'mf_ext', ['S2f', 'tf', 'S2', 'ts', 'Rex', 'CSA',
                               'r'])
        relax> model.create_mf(model='large_model', param_types=['S2f', 'tf', 'S2', 'ts', 'Rex',
                               'CSA', 'r'], equation='mf_ext')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "model.create_mf("
            text = text + "model=" + `model`
            text = text + ", equation=" + `equation`
            text = text + ", param_types=" + `param_types`
            text = text + ", scaling=" + `scaling` + ")\n"
            print text

        # Model argument.
        if type(model) != str:
            print "The model argument must be a string."
            return

        # Equation.
        elif equation == None:
            print "The model-free equation type is not selected."
            return
        elif type(equation) != str:
            print "The model-free equation argument must be a string."
            return

        # Parameter types.
        elif param_types == None:
            print "No parameter types have been supplied."
            return
        elif type(param_types) != list:
            print "The parameter types argument must be an array."
            return

        # Scaling.
        elif type(scaling) != int or (scaling != 0 and scaling != 1):
            print "The scaling argument must be either the integers 0 or 1."
            return

        # Execute the functional code.
        self.create(model=model, equation=equation, param_types=param_types, scaling=scaling)


    def macro_select(self, model=None, scaling=1):
        """Macro for the selection of a preset model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset model.

        scaling:  The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        The preset model-free models are:
            'm0'    => []
            'm1'    => [S2]
            'm2'    => [S2, te]
            'm3'    => [S2, Rex]
            'm4'    => [S2, te, Rex]
            'm5'    => [S2f, S2, ts]
            'm6'    => [S2f, tf, S2, ts]
            'm7'    => [S2f, S2, ts, Rex]
            'm8'    => [S2f, tf, S2, ts, Rex]
            'm9'    => [Rex]

            'm10'   => [CSA]
            'm11'   => [CSA, S2]
            'm12'   => [CSA, S2, te]
            'm13'   => [CSA, S2, Rex]
            'm14'   => [CSA, S2, te, Rex]
            'm15'   => [CSA, S2f, S2, ts]
            'm16'   => [CSA, S2f, tf, S2, ts]
            'm17'   => [CSA, S2f, S2, ts, Rex]
            'm18'   => [CSA, S2f, tf, S2, ts, Rex]
            'm19'   => [CSA, Rex]

            'm20'   => [r]
            'm21'   => [r, S2]
            'm22'   => [r, S2, te]
            'm23'   => [r, S2, Rex]
            'm24'   => [r, S2, te, Rex]
            'm25'   => [r, S2f, S2, ts]
            'm26'   => [r, S2f, tf, S2, ts]
            'm27'   => [r, S2f, S2, ts, Rex]
            'm28'   => [r, S2f, tf, S2, ts, Rex]
            'm29'   => [r, CSA, Rex]

            'm30'   => [r, CSA]
            'm31'   => [r, CSA, S2]
            'm32'   => [r, CSA, S2, te]
            'm33'   => [r, CSA, S2, Rex]
            'm34'   => [r, CSA, S2, te, Rex]
            'm35'   => [r, CSA, S2f, S2, ts]
            'm36'   => [r, CSA, S2f, tf, S2, ts]
            'm37'   => [r, CSA, S2f, S2, ts, Rex]
            'm38'   => [r, CSA, S2f, tf, S2, ts, Rex]
            'm39'   => [r, CSA, Rex]

        Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.  This is due to the extreme flexibly of these models where a change in the
        parameter 'r' is compensated by a corresponding change in the parameter 'CSA' and
        vice versa.


        Additional preset model-free models, which are simply extensions of the above models with
        the addition of a local tm parameter are:
            'tm0'   => [tm]
            'tm1'   => [tm, S2]
            'tm2'   => [tm, S2, te]
            'tm3'   => [tm, S2, Rex]
            'tm4'   => [tm, S2, te, Rex]
            'tm5'   => [tm, S2f, S2, ts]
            'tm6'   => [tm, S2f, tf, S2, ts]
            'tm7'   => [tm, S2f, S2, ts, Rex]
            'tm8'   => [tm, S2f, tf, S2, ts, Rex]
            'tm9'   => [tm, Rex]

            'tm10'  => [tm, CSA]
            'tm11'  => [tm, CSA, S2]
            'tm12'  => [tm, CSA, S2, te]
            'tm13'  => [tm, CSA, S2, Rex]
            'tm14'  => [tm, CSA, S2, te, Rex]
            'tm15'  => [tm, CSA, S2f, S2, ts]
            'tm16'  => [tm, CSA, S2f, tf, S2, ts]
            'tm17'  => [tm, CSA, S2f, S2, ts, Rex]
            'tm18'  => [tm, CSA, S2f, tf, S2, ts, Rex]
            'tm19'  => [tm, CSA, Rex]

            'tm20'  => [tm, r]
            'tm21'  => [tm, r, S2]
            'tm22'  => [tm, r, S2, te]
            'tm23'  => [tm, r, S2, Rex]
            'tm24'  => [tm, r, S2, te, Rex]
            'tm25'  => [tm, r, S2f, S2, ts]
            'tm26'  => [tm, r, S2f, tf, S2, ts]
            'tm27'  => [tm, r, S2f, S2, ts, Rex]
            'tm28'  => [tm, r, S2f, tf, S2, ts, Rex]
            'tm29'  => [tm, r, CSA, Rex]

            'tm30'  => [tm, r, CSA]
            'tm31'  => [tm, r, CSA, S2]
            'tm32'  => [tm, r, CSA, S2, te]
            'tm33'  => [tm, r, CSA, S2, Rex]
            'tm34'  => [tm, r, CSA, S2, te, Rex]
            'tm35'  => [tm, r, CSA, S2f, S2, ts]
            'tm36'  => [tm, r, CSA, S2f, tf, S2, ts]
            'tm37'  => [tm, r, CSA, S2f, S2, ts, Rex]
            'tm38'  => [tm, r, CSA, S2f, tf, S2, ts, Rex]
            'tm39'  => [tm, r, CSA, Rex]



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

        relax> model.select_mf('m1')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "model.select_mf("
            text = text + "model=" + `model`
            text = text + ", scaling=" + `scaling` + ")\n"
            print text

        # Model argument.
        if type(model) != str:
            print "The model argument must be a string."
            return

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            print "The scaling argument must be either the integers 0 or 1."
            return

        # Execute the functional code.
        self.select(model=model, scaling=scaling)


    def minimise(self, model=None, i=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, print_flag=0):
        """Model-free minimisation."""

        # Linear constraints.
        if constraints:
            constraint_function = self.relax.specific_setup.setup("linear_constraints", self.relax.data.equations[model][i])
            if constraint_function == None:
                return
            A, b = constraint_function(model, self.relax.data.param_types[model][i])

        if print_flag >= 1:
            if print_flag >= 2:
                print "\n\n"
            string = "Fitting to residue: " + `self.relax.data.seq[i][0]` + " " + self.relax.data.seq[i][1]
            print string
            string2 = ""
            for j in range(len(string)):
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
            scaling_vector = self.relax.data.scaling[model][i]

        # If any data is missing jump to the next residue.
        data = zeros(self.relax.data.num_ri, Float64)
        errors = zeros(self.relax.data.num_ri, Float64)
        for j in range(self.relax.data.num_ri):
            if self.relax.data.relax_data[j][i, 2] == 0.0:
                continue
            data[j] = self.relax.data.relax_data[j][i, 0]
            errors[j] = self.relax.data.relax_data[j][i, 1]
        self.function_ops = ()

        # Initialise the functions used in the minimisation.
        self.mf = Mf(self.relax, equation=self.relax.data.equations[model][i], param_types=self.relax.data.param_types[model][i], init_params=self.relax.data.params[model][i], relax_data=data, errors=errors, bond_length=self.relax.data.bond_length[i][0], csa=self.relax.data.csa[i][0], diff_type=self.relax.data.diff_type, diff_params=self.relax.data.diff_params, scaling_vector=scaling_vector)

        # Levenberg-Marquardt minimisation.
        if constraints and not match('^[Gg]rid', min_algor):
            algor = min_options[0]
        else:
            algor = min_algor
        if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
            min_options = min_options + (self.mf.lm_dri, errors)


        # Minimisation.
        if constraints:
            results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=self.relax.data.params[model][i], min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
        else:
            results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=self.relax.data.params[model][i], min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
        if results == None:
            return
        self.params, self.func, iter, fc, gc, hc, self.warning = results
        self.iter_count = self.iter_count + iter
        self.f_count = self.f_count + fc
        self.g_count = self.g_count + gc
        self.h_count = self.h_count + hc

        # Place the results in various data structures.
        self.relax.data.params[model][i] = self.params
        self.relax.data.min_results[model][i] = [self.func, self.iter_count, self.f_count, self.g_count, self.h_count, self.warning]


    def map_bounds(self, model, param_types):
        """The function for creating bounds for the mapping function."""

        # Bounds array.
        bounds = zeros((len(param_types), 2), Float64)

        for i in range(len(param_types)):
            # {S2, S2f, S2s}.
            if match('S2', param_types[i]):
                bounds[i] = [0, 1]

            # {te, tf, ts}.
            elif match('t', param_types[i]):
                bounds[i] = [0, 1e-8]

            # Rex.
            elif param_types[i] == 'Rex':
                bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.frq[0])**2]

            # Bond length.
            elif param_types[i] == 'r':
                bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

            # CSA.
            elif param_types[i] == 'CSA':
                bounds[i] = [-100 * 1e-6, -300 * 1e-6]

        return bounds


    def map_labels(self, model, param_types, bounds, swap, inc):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        n = len(param_types)
        axis_incs = 5.0
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in range(n):
            # {S2, S2f, S2s}.
            if match('S2', param_types[swap[i]]):
                # Labels.
                labels = labels + "\"" + param_types[swap[i]] + "\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1.0
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1.0

            # {te, tf, and ts}.
            elif match('t', param_types[swap[i]]):
                # Labels.
                labels = labels + "\"" + param_types[swap[i]] + " (ps)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e12
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e12

            # Rex.
            elif param_types[swap[i]] == 'Rex':
                # Labels.
                labels = labels + "\"Rex (" + self.relax.data.frq_labels[0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.frq[0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.frq[0])**2

            # Bond length.
            elif param_types[swap[i]] == 'r':
                # Labels.
                labels = labels + "\"" + param_types[swap[i]] + " (A)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-10
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-10

            # CSA.
            elif param_types[swap[i]] == 'CSA':
                # Labels.
                labels = labels + "\"" + param_types[swap[i]] + " (ppm)\""

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


    def print_header(self, file):
        """Function for printing the header of the results file."""

        # Residue number and name.
        file.write("%-5s" % "Num")
        file.write("%-6s" % "Name")

        # Model details.
        file.write("%-6s" % "Model")
        file.write("%-10s" % "Equation")
        file.write("%-36s" % "Params")

        # Parameters.
        file.write("%-26s" % "S2")
        file.write("%-26s" % "S2f")
        file.write("%-26s" % "S2s")
        file.write("%-26s" % "tf_(ps)")
        file.write("%-26s" % "te_or_ts_(ps)")
        file.write("%-26s" % ("Rex_(" + self.relax.data.frq_labels[0] + "_MHz)"))
        file.write("%-26s" % "Bond_length_(A)")
        file.write("%-26s" % "CSA_(ppm)")

        # Minimisation results.
        file.write("%-26s" % "Chi-squared")
        file.write("%-9s" % "Iter")
        file.write("%-9s" % "f")
        file.write("%-9s" % "g")
        file.write("%-9s" % "h")
        file.write("Warning")

        # End of line.
        file.write("\n")


    def print_results(self, file, model, param_types):
        """Function for printing the core of the results file."""

        # Loop over the residues.
        for i in range(len(self.relax.data.seq)):
            # Initialise.
            types = param_types[i]
            if self.relax.data.scaling.has_key(model):
                params = self.relax.data.params[model][i] * self.relax.data.scaling[model][i]
            else:
                params = self.relax.data.params[model][i]

            # Residue number and name.
            file.write("%-5s" % self.relax.data.seq[i][0])
            file.write("%-6s" % self.relax.data.seq[i][1])

            # Model details.
            file.write("%-6s" % model)
            file.write("%-10s" % self.relax.data.equations[model][i])
            file.write("%-36s" % replace(`types`, ' ', ''))

            # S2.
            flag = 1
            for j in range(len(types)):
                # S2.
                if types[j] == 'S2':
                    file.write("%-26s" % `params[j]`)
                    flag = 0
                    continue

                # S2f and S2s.
                elif types[j] == 'S2f':
                    for k in range(len(types)):
                        if types[k] == 'S2s':
                            file.write("%-26s" % `params[j]*params[k]`)
                            flag = 0
                            continue
            if flag:
                file.write("%-26s" % "N/A")

            # S2f.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'S2f':
                    file.write("%-26s" % `params[j]`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # S2s.
            flag = 1
            for j in range(len(types)):
                # S2s.
                if types[j] == 'S2s':
                    file.write("%-26s" % `params[j]`)
                    flag = 0
                    continue

                # S2f and S2.
                elif types[j] == 'S2f':
                    for k in range(len(types)):
                        if types[k] == 'S2':
                            file.write("%-26s" % `params[k]/params[j]`)
                            flag = 0
                            continue
            if flag:
                file.write("%-26s" % "N/A")

            # tf.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'tf':
                    file.write("%-26s" % `params[j] / 1e-12`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # te or ts.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'te' or types[j] == 'ts':
                    file.write("%-26s" % `params[j] / 1e-12`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # Rex.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'Rex':
                    file.write("%-26s" % `params[j] * (2.0 * pi * self.relax.data.frq[0])**2`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # Bond length.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'r':
                    file.write("%-26s" % `params[j] / 1e-10`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # CSA.
            flag = 1
            for j in range(len(types)):
                if types[j] == 'CSA':
                    file.write("%-26s" % `params[j] / 1e-6`)
                    flag = 0
                    continue
            if flag:
                file.write("%-26s" % "N/A")

            # Minimisation results.
            file.write("%-26s" % `self.relax.data.min_results[model][i][0]`)
            file.write("%-9i" % self.relax.data.min_results[model][i][1])
            file.write("%-9i" % self.relax.data.min_results[model][i][2])
            file.write("%-9i" % self.relax.data.min_results[model][i][3])
            file.write("%-9i" % self.relax.data.min_results[model][i][4])
            if self.relax.data.min_results[model][i][5] != None:
                file.write(self.relax.data.min_results[model][i][5])

            # End of line.
            file.write("\n")


    def scaling_vector(self, param_types):
        """Function for creating the scaling vector."""

        self.scale_vect = ones(len(param_types), Float64)
        for i in range(len(param_types)):
            # te, tf, and ts.
            if match('t', param_types[i]):
                self.scale_vect[i] = 1e-12

            # Rex.
            elif param_types[i] == 'Rex':
                self.scale_vect[i] = 1.0 / (2.0 * pi * self.relax.data.frq[0]) ** 2

            # Bond length.
            elif param_types[i] == 'r':
                self.scale_vect[i] = 1e-10

            # CSA.
            elif param_types[i] == 'CSA':
                self.scale_vect[i] = 1e-4



    def select(self, model=None, scaling=1):
        """Function for the selection of a preset model-free model."""

        # Test if sequence data is loaded.
        try:
            self.relax.data.seq
        except AttributeError:
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


        # Preset models.
        ################

        # Block 1.
        if model == 'm0':
            equation = 'mf_orig'
            param_types = []
        elif model == 'm1':
            equation = 'mf_orig'
            param_types = ['S2']
        elif model == 'm2':
            equation = 'mf_orig'
            param_types = ['S2', 'te']
        elif model == 'm3':
            equation = 'mf_orig'
            param_types = ['S2', 'Rex']
        elif model == 'm4':
            equation = 'mf_orig'
            param_types = ['S2', 'te', 'Rex']
        elif model == 'm5':
            equation = 'mf_ext'
            param_types = ['S2f', 'S2', 'ts']
        elif model == 'm6':
            equation = 'mf_ext'
            param_types = ['S2f', 'tf', 'S2', 'ts']
        elif model == 'm7':
            equation = 'mf_ext'
            param_types = ['S2f', 'S2', 'ts', 'Rex']
        elif model == 'm8':
            equation = 'mf_ext'
            param_types = ['S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm9':
            equation = 'mf_orig'
            param_types = ['Rex']

        # Block 2.
        elif model == 'm10':
            equation = 'mf_orig'
            param_types = ['CSA']
        elif model == 'm11':
            equation = 'mf_orig'
            param_types = ['CSA', 'S2']
        elif model == 'm12':
            equation = 'mf_orig'
            param_types = ['CSA', 'S2', 'te']
        elif model == 'm13':
            equation = 'mf_orig'
            param_types = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            equation = 'mf_orig'
            param_types = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            equation = 'mf_ext'
            param_types = ['CSA', 'S2f', 'S2', 'ts']
        elif model == 'm16':
            equation = 'mf_ext'
            param_types = ['CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm17':
            equation = 'mf_ext'
            param_types = ['CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm18':
            equation = 'mf_ext'
            param_types = ['CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm19':
            equation = 'mf_orig'
            param_types = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            equation = 'mf_orig'
            param_types = ['r']
        elif model == 'm21':
            equation = 'mf_orig'
            param_types = ['r', 'S2']
        elif model == 'm22':
            equation = 'mf_orig'
            param_types = ['r', 'S2', 'te']
        elif model == 'm23':
            equation = 'mf_orig'
            param_types = ['r', 'S2', 'Rex']
        elif model == 'm24':
            equation = 'mf_orig'
            param_types = ['r', 'S2', 'te', 'Rex']
        elif model == 'm25':
            equation = 'mf_ext'
            param_types = ['r', 'S2f', 'S2', 'ts']
        elif model == 'm26':
            equation = 'mf_ext'
            param_types = ['r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm27':
            equation = 'mf_ext'
            param_types = ['r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm28':
            equation = 'mf_ext'
            param_types = ['r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm29':
            equation = 'mf_orig'
            param_types = ['r', 'Rex']

        # Block 4.
        elif model == 'm30':
            equation = 'mf_orig'
            param_types = ['r', 'CSA']
        elif model == 'm31':
            equation = 'mf_orig'
            param_types = ['r', 'CSA', 'S2']
        elif model == 'm32':
            equation = 'mf_orig'
            param_types = ['r', 'CSA', 'S2', 'te']
        elif model == 'm33':
            equation = 'mf_orig'
            param_types = ['r', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            equation = 'mf_orig'
            param_types = ['r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            equation = 'mf_ext'
            param_types = ['r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'm36':
            equation = 'mf_ext'
            param_types = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm37':
            equation = 'mf_ext'
            param_types = ['r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm38':
            equation = 'mf_ext'
            param_types = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm39':
            equation = 'mf_orig'
            param_types = ['r', 'CSA', 'Rex']


        # Preset models with local correlation time.
        ############################################

        # Block 1.
        elif model == 'tm0':
            equation = 'mf_orig'
            param_types = ['tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            param_types = ['tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            param_types = ['tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            param_types = ['tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            param_types = ['tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            param_types = ['tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            param_types = ['tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            param_types = ['tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            param_types = ['tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            param_types = ['tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            param_types = ['tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            param_types = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            param_types = ['tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            param_types = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            param_types = ['tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            param_types = ['tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            param_types = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            param_types = ['tm', 'r', 'CSA', 'Rex']

        # Invalid models.
        else:
            print "The model '" + model + "' is invalid."
            return

        # Create the scaling vector.
        self.scaling_vector(param_types)

        # Update the data structures.
        self.data_update(model, equation, param_types)
